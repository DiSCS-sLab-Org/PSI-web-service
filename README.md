# 🔒 Private Set Intersection (PSI) Web Dashboard

A privacy-preserving web service for **secure IP-set intersection** using the [OpenMined PSI](https://github.com/OpenMined/PSI) library, compiled to WebAssembly for client-side execution.

## 🏗 Project Overview
- **Client-side WebAssembly computation**: PSI cryptography runs entirely in the browser, so the client’s full list never reaches the server.
- **Minimal data exposure**: The server only receives cryptographically blinded requests and returns an opaque response.  
  Intersection results can be stored on the server **only through the backend logic** (e.g. `/results` or `/api/log-psi-result`), not because of an end-user choice in the interface.
- **Role-based authentication & auditing**: Built-in user roles (admin/user) and session logging.

## 📁 Structure
```
psi/
├── server.py              # FastAPI backend with PSI endpoints
├── database.py            # SQLite operations and session logging
├── init_user.py           # User creation utility
├── static/
│   ├── dashboard.html     # Main PSI dashboard
│   ├── login_clean.html   # Login page
│   └── js/
│       ├── psi_wasm_web.js   # WebAssembly PSI module (OpenMined)
│       └── wasm_web.d.ts     # TypeScript definitions
├── data/
│   ├── server_ips.txt     # Server-side IP set
│   └── psi.db             # Session log database
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in production
./start_prod.sh
```

Access the dashboard at:  
`http://<server-ip>:8000`  
Login page: `http://<server-ip>:8000/login`

Create users:
```bash
python init_user.py username password user   # regular user
python init_user.py username password admin  # admin
```

## 🔧 Usage

1. **Login** at `/login`.
2. **Upload an IP list** (one IP per line).
3. **Compute PSI**: The browser’s WebAssembly module computes the private set intersection with the server’s list.
4. **View or download results**.  
   Any logging of intersection size or elements occurs only through the server-side code (not an optional client-side action).

## 🔒 Privacy & Security

- **Client-side computation**: All PSI operations run inside WebAssembly in the browser.
- **Cryptographic protocol**: Based on OpenMined’s PSI secure multi-party computation.
- **Server exposure**: Receives only blinded PSI requests and the PSI response it generates; optional server logging of results is handled by backend endpoints.
- **Authentication & logging**: JWT-based auth, role-based permissions, and a full session audit trail.

## 🛠 Technology

**Backend**
- FastAPI (Python)
- SQLite database
- Custom static handler serving `.wasm` with correct `application/wasm` MIME type

**Frontend**
- WebAssembly PSI module compiled from OpenMined PSI C++ code
- Vanilla JavaScript (ES6+) for UI and Fetch API calls
- HTML/CSS for responsive dashboard

### Key API Endpoints
- `GET /setup` – Send server PSI setup message
- `POST /process` – Process PSI request and return PSI response
- `POST /api/login` – Authenticate user
- `GET /api/sessions` – Retrieve session history
- `POST /api/log-psi-result` – Log PSI computation results

---
