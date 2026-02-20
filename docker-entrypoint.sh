#!/bin/sh
set -eu

# Seed Docker volume with initial data on first run.
mkdir -p /data

if [ ! -f /data/server_ips.txt ]; then
  if [ -f /app/data/server_ips.txt ]; then
    cp /app/data/server_ips.txt /data/server_ips.txt
  else
    # Start with an empty set if no seed file is bundled.
    : > /data/server_ips.txt
  fi
fi

if [ ! -f /data/client_ips.txt ] && [ -f /app/data/client_ips.txt ]; then
  cp /app/data/client_ips.txt /data/client_ips.txt
fi

if [ ! -f /data/psi.db ] && [ -f /app/data/psi.db ]; then
  cp /app/data/psi.db /data/psi.db
fi

exec "$@"
