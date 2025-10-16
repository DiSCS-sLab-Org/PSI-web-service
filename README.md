# 🔒 Private Set Intersection (PSI) Web Service

A privacy-preserving web application for **secure IP address set intersection** using the [OpenMined PSI](https://github.com/OpenMined/PSI) library.

## 🏗 Project Overview

This PSI web service allows organizations to securely compare their IP address lists with a server's threat intelligence database without exposing their complete datasets to each other. Built using OpenMined's cryptographic PSI protocol with client-side WebAssembly execution.

**Key Features:**
- **Privacy-preserving computation**: Client and server can find common IP addresses without revealing their complete lists to each other
- **WebAssembly execution**: All PSI cryptographic operations run client-side in the browser for enhanced security
- **Automated logging**: Intersection results are automatically captured for threat intelligence analysis and audit trails
- **Session management**: Complete tracking of all PSI operations with metadata and timestamps

## 🛠 Technology Stack

**Backend:**
- **FastAPI** - Python web framework with PSI endpoints
- **SQLite** - Database for user management and session logging
- **OpenMined PSI** - Cryptographic library for private set intersection
- **Session-based Authentication** - Secure token authentication with role-based access control

**Frontend:**
- **WebAssembly** - Client-side PSI cryptographic operations
- **JavaScript ES6+** - Modern web interface
- **Custom WASM MIME handling** - Secure WebAssembly execution

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 FORTH Foundation for Research and Technology-Hellas

### Third-Party Licenses

This project uses [OpenMined PSI](https://github.com/OpenMined/PSI), which is licensed under the Apache License 2.0. See the [NOTICE](NOTICE) file for full attribution details.
