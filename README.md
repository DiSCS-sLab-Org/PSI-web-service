# 🔒 Private Set Intersection (PSI) Web Dashboard

A privacy-preserving web service for **secure IP-set intersection** using the [OpenMined PSI](https://github.com/OpenMined/PSI) library, compiled to WebAssembly for client-side execution.

## 🏗 Project Overview
- **Privacy-preserving PSI protocol**: Neither client nor server sees the other's complete IP dataset. Server processes encrypted client requests without accessing raw client data.
- **Client-side intersection computation**: All PSI cryptography and intersection calculations run entirely in the browser using WebAssembly. Only the client can compute the final intersection results.
- **Automatic intersection logging**: All computed intersection results are automatically sent to the server for threat intelligence analysis and audit purposes.
- **Role-based access control**:
  - **Users**: Upload IP lists, compute intersections, download their own results
  - **Admins**: View all sessions, download any intersection data, access system-wide operations
- **Comprehensive session tracking**: All PSI operations logged with timestamps, client metadata, and intersection details for security monitoring.

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

Create users:
```bash
python init_user.py username password user   # regular user
python init_user.py username password admin  # admin
```

## 🔧 Usage

1. **Login** at `/login`.
2. **Upload an IP list** (one IP per line).
3. **Compute PSI**: The browser’s WebAssembly module computes the private set intersection with the server’s list.
4. **Download results**.  

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

---
