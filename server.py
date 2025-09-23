import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Depends, Request as FastAPIRequest, Form, UploadFile, File
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from private_set_intersection.python import Request, server
from database import Database

PSI_CONTAINER = os.getenv("PSI_CONTAINER", "raw").lower()  # raw | gcs | bloom
PSI_FPR = float(os.getenv("PSI_FPR", "1e-9"))
PSI_REVEAL = os.getenv("PSI_REVEAL", "elements").lower()  # elements | size
PORT = int(os.getenv("PSI_PORT", "8000"))
SERVER_SET_PATH = os.getenv("SERVER_SET_PATH", "/data/server_ips.txt")

# Initialize database
db = Database()
security = HTTPBearer(auto_error=False)


def load_ips(path):
    seen, out = set(), []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and s not in seen:
                seen.add(s)
                out.append(s)
    return out


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom static file serving with proper WASM MIME type
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Scope, Receive, Send

class PSIStaticFiles(StaticFiles):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"].endswith(".wasm"):
            # Serve WASM files with correct MIME type
            file_path = self.get_path(scope)
            if file_path and file_path.exists():
                response = FileResponse(file_path, media_type="application/wasm")
                await response(scope, receive, send)
                return
        # Default handling for other files
        await super().__call__(scope, receive, send)

# Mount static files with WASM support
app.mount("/static", PSIStaticFiles(directory="static"), name="static")

print(f"Loading server IPs from: {SERVER_SET_PATH}")
server_items = load_ips(SERVER_SET_PATH)
print(f"Loaded {len(server_items)} server IPs")

reveal_intersection = PSI_REVEAL == "elements"
psi_server = server.CreateWithNewKey(reveal_intersection)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[tuple]:
    """Get current user from token, returns (user_id, role)"""
    if not credentials:
        return None

    user_data = db.verify_session_token(credentials.credentials)
    return user_data


def require_auth(user_data: Optional[tuple] = Depends(get_current_user)) -> tuple:
    """Require authentication"""
    if user_data is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_data


def require_admin(user_data: tuple = Depends(require_auth)) -> tuple:
    """Require admin role"""
    user_id, role = user_data
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_data


def get_client_ip(request: FastAPIRequest) -> str:
    """Get client IP address"""
    return request.client.host if request.client else "unknown"


@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"


@app.get("/setup", response_class=PlainTextResponse)
def setup(num_client_inputs: int, container: str = PSI_CONTAINER, fpr: float = PSI_FPR):
    setup_message = psi_server.CreateSetupMessage(fpr, num_client_inputs, server_items)
    setup_bytes = setup_message.SerializeToString()
    return setup_bytes.hex()


@app.post("/process", response_class=PlainTextResponse)
def process(request_hex: str = Body(..., embed=True)):
    req_bytes = bytes.fromhex(request_hex)

    # Parse the bytes back into a Request protobuf object
    request_message = Request()
    request_message.ParseFromString(req_bytes)

    # Process the request
    response_message = psi_server.ProcessRequest(request_message)
    resp_bytes = response_message.SerializeToString()
    return resp_bytes.hex()


@app.post("/results", response_class=PlainTextResponse)
def receive_results(results: dict = Body(...)):
    """Optional endpoint for clients to share intersection results with server"""
    with open("/data/server_received_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(
        f"Server received intersection results: {results['intersection_size']} common IP addresses"
    )
    return "Results received"


# Web Dashboard Endpoints
@app.get("/", response_class=HTMLResponse)
def dashboard_home():
    """Main dashboard page - authentication handled by JavaScript"""
    return HTMLResponse(open("static/dashboard.html").read())


@app.get("/login", response_class=HTMLResponse)
def login_page():
    """Login page"""
    return HTMLResponse(open("static/login_clean.html").read())


@app.post("/api/login")
def login(username: str = Form(...), password: str = Form(...)):
    """User login endpoint"""
    user_data = db.verify_user(username, password)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, role = user_data
    token = db.create_session_token(user_id)
    return {"token": token, "user_id": user_id, "role": role}


@app.post("/api/logout")
def logout(user_data: tuple = Depends(require_auth)):
    """User logout endpoint"""
    return {"message": "Logged out successfully"}


@app.get("/api/sessions")
def get_user_sessions(user_data: tuple = Depends(require_auth)):
    """Get user's PSI sessions"""
    user_id, role = user_data
    sessions = db.get_user_sessions(user_id)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
def get_session_details(session_id: int, user_data: tuple = Depends(require_auth)):
    """Get detailed session information"""
    user_id, role = user_data
    session = db.get_session_details(session_id, user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/sessions/{session_id}/download")
def download_session_results(session_id: int, user_data: tuple = Depends(require_auth)):
    """Download session results as JSON"""
    user_id, role = user_data
    session = db.get_session_details(session_id, user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create downloadable JSON
    result = {
        "session_id": session["id"],
        "timestamp": session["timestamp"],
        "client_size": session["client_size"],
        "intersection_size": session["intersection_size"],
        "intersection": session["intersection_data"]
    }

    return JSONResponse(
        content=result,
        headers={
            "Content-Disposition": f"attachment; filename=psi_results_{session_id}.json"
        }
    )




@app.post("/api/log-psi-result")
def log_psi_result(
    client_size: int = Form(...),
    intersection_size: int = Form(...),
    intersection_data: str = Form(...),
    request: FastAPIRequest = ...,
    user_data: tuple = Depends(require_auth)
):
    """Log PSI computation results"""
    user_id, role = user_data
    try:
        intersection_list = json.loads(intersection_data)
    except json.JSONDecodeError:
        intersection_list = []

    client_ip = get_client_ip(request)

    session_id = db.log_psi_session(
        user_id=user_id,
        client_size=client_size,
        intersection_size=intersection_size,
        intersection_data=intersection_list,
        client_ip=client_ip
    )

    return {"session_id": session_id, "message": "Results logged successfully"}


# Admin endpoints (protected)
@app.get("/api/admin/sessions")
def admin_get_all_sessions(user_data: tuple = Depends(require_admin)):
    """Admin view of all sessions"""
    sessions = db.get_all_sessions()
    return {"sessions": sessions}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, log_level="info")
