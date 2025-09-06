#!/bin/bash
set -euo pipefail
compose_bin() {
  if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    echo "docker compose"
  elif command -v docker-compose &>/dev/null; then
    echo "docker-compose"
  else
    echo "Docker Compose not found."
    exit 1
  fi
}
COMPOSE=$(compose_bin)
[ ! -f .env ] && [ -f .env.example ] && cp .env.example .env || true
$COMPOSE pull || true
$COMPOSE up -d --build
for i in {1..60}; do curl -sf http://localhost:8000/health && break || sleep 2; done
echo "Kova AI System up. Docs: http://localhost:8000/docs"
