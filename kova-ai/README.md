# KOVA AI Platform

This is the main backend for the KOVA AI system. See `docker-compose.yml` for local dev setup. API runs on FastAPI at port 8000.

## API Endpoints

- `GET /health` - Basic health check
- `POST /ai/command` - Execute AI command
- `POST /api/scan` - Scan repository
- `POST /webhooks/github` - GitHub webhook receiver
- `GET /metrics` - Prometheus metrics
