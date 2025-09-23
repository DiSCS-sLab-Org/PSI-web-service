#!/bin/bash
# Start PSI service for production on VM

export PSI_HOST="139.91.90.9"
export PSI_PORT="8000"
export SERVER_SET_PATH="data/server_ips.txt"

echo "🚀 Starting PSI service in PRODUCTION mode"
echo "   Host: $PSI_HOST"
echo "   Port: $PSI_PORT"
echo "   URL: http://$PSI_HOST:$PSI_PORT"

python server.py