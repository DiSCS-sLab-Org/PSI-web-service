# 🔒 Private Set Intersection (PSI) Web Dashboard

A privacy-preserving Private Set Intersection web service built using OpenMined PSI library.

## 🎯 Project Overview

This project provides **client-side privacy-preserving PSI** where:
- **Server only sees intersection results, never the client's full IP list** - encrypted PSI protocol protects non-matching data
- **WebAssembly-based computation** runs entirely in the browser
- **Role-based authentication** with admin and user access levels
- **Session logging and audit trail** for compliance

### What We Achieved ✅

1. **Privacy-Preserving Architecture**: Server only receives intersection results, client's full IP list remains private
2. **Client-Side WebAssembly PSI**: Computation happens in browser using OpenMined PSI.js
3. **Complete Web Dashboard**: File upload, PSI computation, results download
4. **User Management**: Registration, authentication, role-based access control
5. **Session Auditing**: All PSI computations are logged with metadata
6. **CORS/MIME Resolution**: Local WebAssembly serving with proper headers

## 📁 Project Structure

```
psi/
├── 🌐 Web Service Backend
│   ├── server.py              # FastAPI web server with PSI endpoints
│   ├── database.py            # SQLite database operations
│   ├── init_user.py           # User creation utility
│
├── 🎨 Web Frontend
│   ├── static/
│   │   ├── dashboard.html     # Main PSI dashboard
│   │   ├── login_clean.html   # Login page
│   │   └── js/
│   │       ├── psi_wasm_web.js    # OpenMined PSI WebAssembly module
│   │       └── wasm_web.d.ts      # TypeScript definitions
│
├── 📊 Data & Configuration
│   ├── data/
│   │   ├── server_ips.txt     # Server's IP list
│   │   └── psi.db             # SQLite database
│
└── 🐍 Python Dependencies
    └── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Start the PSI Web Service

```bash
# Activate Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the web server
SERVER_SET_PATH="data/server_ips.txt" python server.py
```

**Expected output:**
```
Loading server IPs from: data/server_ips.txt
Loaded server IPs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Access the Web Dashboard

- **URL**: http://139.91.90.9:8000
- **Login Page**: http://139.91.90.9:8000/login

### 3. Create Users

```bash
source venv/bin/activate

# Create regular user
python init_user.py username password user

# Create admin user
python init_user.py username password admin
```

## 🔧 Usage Guide

### Web Dashboard Usage

1. **Login** at http://139.91.90.9:8000/login
2. **Upload IP file**: Click "Choose File" and select an IP list
   - File should contain one IP address per line
   - Supports IPv4 format (e.g., `192.168.1.1`)
3. **Compute PSI**: Click "Compute Private Set Intersection"
4. **View Results**: See intersection size and individual matching IPs
5. **Download Results**: Save results as JSON file
6. **Session History**: View past PSI computations

## 🔒 Privacy & Security Features

### Privacy Preservation Model
- **Client-side computation**: PSI runs in WebAssembly in the browser
- **Minimal data exposure**: Server only receives intersection results, not full IP lists
- **Cryptographic protocol**: Uses OpenMined PSI's secure multi-party computation
- **Local processing**: File processing and validation happens client-side

### Security Implementation
- **JWT-based authentication**: Secure session management
- **Role-based access control**: Admin vs user permissions
- **Input validation**: IP address format validation
- **Session logging**: Complete audit trail of all PSI operations
- **CORS protection**: Proper cross-origin resource sharing configuration

### Architecture Security
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Browser │    │   PSI Web Server │    │   Server Data   │
│                 │    │                  │    │                 │
│ 1. Load IPs     │    │ 1. Setup Message │    │ server_ips.txt  │
│ 2. PSI Setup    ├───►│ 2. Process PSI   │◄───┤                 │
│ 3. Encrypt Data │    │ 3. Log Session   │    │                 │
│ 4. Compute PSI  │    │ 4. Return Result │    │ psi.db          │
│ 5. Show Results │◄───┤                  │    │ (audit logs)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
     ▲
     │ Only intersection results sent to server
     └── WebAssembly PSI computation happens here
```

## 🛠 Technical Implementation

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLite with custom schema
- **PSI Library**: OpenMined PSI (Python bindings)
- **Authentication**: JWT tokens with HTTP Bearer
- **File Serving**: Custom static file handler for WASM MIME types

### Frontend Stack
- **WebAssembly**: OpenMined PSI.js for client-side computation
- **JavaScript**: Vanilla ES6+ with File API and Fetch API
- **CSS**: Custom responsive design with gradient themes
- **Security**: Content Security Policy friendly implementation

### API Endpoints
- `GET /health` - Health check
- `GET /setup` - PSI setup message generation
- `POST /process` - PSI request processing
- `POST /api/login` - User authentication
- `GET /api/sessions` - Session history
- `POST /api/log-psi-result` - Log PSI computation results

---

**Privacy-preserving PSI web service for secure IP threat intelligence sharing**