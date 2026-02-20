# Private Set Intersection (PSI) Service

FastAPI-based web service for privacy-preserving IP set intersection.

## What This Project Does

This service lets a client compare its IP list against a server-side IP list without exposing the full client list to the server.

It uses OpenMined PSI and provides:

- PSI setup and processing endpoints (`/setup`, `/process`)
- Web dashboard + login flow (`/`, `/login`)
- User authentication with roles (`user`, `admin`)
- Session logging in SQLite (client set size, intersection size, metadata)
- Per-user and admin session views/download endpoints

## How It Works

1. Server loads a threat-intel IP set from `SERVER_SET_PATH` (default `/data/server_ips.txt`).
2. Client asks `/setup` for PSI setup parameters.
3. Client computes encrypted PSI request in browser-side JS/WASM.
4. Server sends encrypted PSI response from `/process`.
5. Client derives intersection and can log results to the server.
6. Server stores session metadata in SQLite (`/data/psi.db`).

## Why This Is PSI (and not plain upload)

Naive approach (not PSI):

- Client uploads full IP list to server.
- Server directly computes intersection.
- Server learns full client dataset.

This service's PSI flow:

- Client file is read locally in the browser (`FileReader`), not uploaded as raw list.
- Browser creates cryptographic PSI request and sends only encoded request bytes to server.
- Server processes request with its private key and dataset, returns PSI response bytes.
- Browser computes final intersection locally using WASM.

## What Each Side Learns

Server side (current implementation):

- Does not receive raw client input list.
- Receives PSI request bytes at `/process`.
- Receives intersection output only because dashboard currently calls `/api/log-psi-result` with `intersection_data`.

Client side:

- Does not receive plaintext `server_ips.txt`.
- Receives PSI setup/response objects (`/setup`, `/process`) derived from server set.
- Uses those objects to compute intersection locally.

Important caveat:

- The current dashboard sends intersection IPs back to server for session history/auditing.
- If you want stricter privacy where server does not learn intersection elements, remove that logging call or store only counts.

## How Server Set Is Used Without Sending Plain List

- Server loads raw IPs from `/data/server_ips.txt` internally.
- `/setup` returns a cryptographic setup message from `CreateSetupMessage(...)`, not the plaintext file.
- Client can run PSI with this setup but does not directly get server plaintext IP rows from API responses.

## Run With Docker

1. Create env file:

```bash
cp .env.example .env
```

2. Start service:

```bash
docker compose up -d --build
```

3. Open:

- `http://<vm-ip>:8000`
- Health check: `http://<vm-ip>:8000/health`

## Data, DB, and Users

- The service stores runtime data in a Docker-managed volume: `psi_data`.
- SQLite DB path inside container: `/data/psi.db`.
- Server set file path inside container: `/data/server_ips.txt`.
- On first start, the container seeds `/data` from bundled files if missing.
- If no seed file exists, `/data/server_ips.txt` is created empty. Populate it with one IP per line.

Create users:

```bash
docker compose exec psi python init_user.py <username> <password> [role]
```

Examples:

```bash
docker compose exec psi python init_user.py alice strongpass user
docker compose exec psi python init_user.py admin strongpass admin
```

Check users:

```bash
docker compose exec psi python -c "import sqlite3; c=sqlite3.connect('/data/psi.db').cursor(); print(c.execute('SELECT id, username, role, created_at FROM users').fetchall())"
```

Update server IP set (one IP per line):

```bash
docker cp ./data/server_ips.txt psi-service:/data/server_ips.txt
docker compose restart psi
```

## Port

- Container port: `8000`
- Host port default: `8000` 
- Change host port in `.env` with `PSI_HOST_PORT=<port>`

## Useful Commands

```bash
# Status
docker compose ps

# Logs
docker compose logs -f psi

# Restart
docker compose restart

# Stop
docker compose down
```
