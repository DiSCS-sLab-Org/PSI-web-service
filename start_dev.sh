#!/bin/bash
# Start PSI service for local development

export PSI_HOST="127.0.0.1"
export PSI_PORT="8000"
export SERVER_SET_PATH="data/server_ips.txt"

echo "🚀 Starting PSI service in DEVELOPMENT mode"
echo "   Host: $PSI_HOST"
echo "   Port: $PSI_PORT"
echo "   URL: http://$PSI_HOST:$PSI_PORT"

python server.py