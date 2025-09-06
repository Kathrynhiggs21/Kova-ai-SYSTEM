# 🚀 Kova AI System - Complete Platform

A complete AI-powered development automation platform with repository scanning, error detection, automatic fixes, and natural language command processing.

## 🎯 What's Inside

**FastAPI Application** with endpoints:
- `GET /health` - Health check 
- `GET /metrics` - Prometheus metrics
- `GET /docs` - Interactive API documentation
- `POST /ai/command` - Execute AI commands
- `POST /api/scan` - Scan repositories for errors
- `POST /webhooks/github` - GitHub webhook processing

**Database Schema** (PostgreSQL):
- `repositories` - Repository information
- `errors` - Detected errors and issues  
- `auto_fixes` - Generated automatic fixes
- `ai_commands` - AI command history

**Infrastructure**:
- Redis cache for performance
- Prometheus metrics collection
- Nginx reverse proxy (optional)
- Docker containerization
- One-shot deployment script

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys (OpenAI, Anthropic, GitHub, Pinecone)

### Installation (2 steps)

1. **Setup Environment**
```bash
cd /path/to/Kova-ai-SYSTEM/KOVA_AI_Platform_FULL/kova-ai
cp .env.example .env
# Edit .env with your API keys
```

2. **Deploy & Run**
```bash
./setup_kova_system.sh
```

### Access Points
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 🧪 Test the System

```bash
# Health check
curl http://localhost:8000/health

# Test AI command
curl -X POST http://localhost:8000/ai/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create a REST API for user management"}'

# Test repository scan
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"name": "my-repo", "url": "https://github.com/user/repo"}'
```

## 📁 Key Files

- `setup_kova_system.sh` - Complete deployment script
- `docker-compose.yml` - Multi-service orchestration
- `.env.example` - Environment configuration template
- `app/main.py` - FastAPI application
- `scripts/init.sql` - Database schema
- `docs/DEPLOYMENT_CHECKLIST.md` - Production deployment guide

## 🔧 API Keys Required

Add these to your `.env` file:
- `OPENAI_API_KEY` - From https://platform.openai.com/api-keys
- `ANTHROPIC_API_KEY` - From https://console.anthropic.com/
- `GITHUB_TOKEN` - From https://github.com/settings/tokens  
- `PINECONE_API_KEY` - From https://www.pinecone.io/

## 📊 Architecture

```
Client → [Nginx] → FastAPI → PostgreSQL
                      ↓         Redis
                  Prometheus
```

See `docs/architecture.md` for detailed system design.

## 🛠️ Development

```bash
# View logs
docker compose logs -f

# Restart services  
docker compose restart

# Stop everything
docker compose down

# Clean restart
docker compose down -v && ./setup_kova_system.sh
```

## 📚 Documentation

- `DESCRIPTIVE_TREE.md` - File structure explanation
- `docs/DEPLOYMENT_CHECKLIST.md` - Production deployment
- `docs/architecture.md` - System architecture
- `/docs` endpoint - Interactive API docs

## 🎉 Success!

Your Kova AI System is ready when:
- ✅ Health check returns `{"status": "ok"}`
- ✅ API docs accessible at `/docs`
- ✅ All endpoints responding
- ✅ Database tables created
- ✅ Metrics endpoint working

---

**Enjoy your AI-powered development platform! 🚀**
