# KOVA AI Platform

This is the main backend for the KOVA AI system. See `docker-compose.yml` for local dev setup. API runs on FastAPI at port 8000.

## API Endpoints

- `GET /api/health` - Basic health check
- `POST /api/ai/command` - Execute AI command
- `POST /api/scan` - Scan repository path and return file list
- `POST /api/webhooks/github` - GitHub webhook receiver
- `GET /api/metrics` - Prometheus metrics
