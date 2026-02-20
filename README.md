# Private Set Intersection (PSI) Service

FastAPI-based PSI web service with Docker deployment.

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
