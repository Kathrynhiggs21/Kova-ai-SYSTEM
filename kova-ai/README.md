# KOVA AI Platform

This is the main backend for the KOVA AI system, built with FastAPI, PostgreSQL, and Docker.

## Quick Start

### Prerequisites
- Docker and Docker Compose (latest versions)
- 4GB RAM minimum (8GB recommended)

### Setup and Run

1. **Clone and navigate to the project**:
   ```bash
   git clone <repository-url>
   cd kova-ai
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Build and start services**:
   ```bash
   docker compose up --build
   ```

4. **Verify the API is running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok"}
   ```

## Environment Configuration

The application requires several environment variables. Copy `.env.example` to `.env` and configure:

### Required Variables
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `DATABASE_URL` - Database connection string

### Optional Variables (recommended for full functionality)
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Anthropic Claude API access  
- `GITHUB_TOKEN` - GitHub API access
- `PINECONE_API_KEY` - Vector database access

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation
- `GET /metrics` - Prometheus metrics
- `POST /ai/command` - AI command processing
- `POST /webhooks/github` - GitHub webhook handler

## Testing

### Build Test
```bash
docker compose build --no-cache
```

### Startup Test
```bash
docker compose up -d
docker compose logs api --tail=50
```

### Health Check Test
```bash
curl -f http://localhost:8000/health
```

### Python Import Test
```bash
docker compose exec api python -c "import app; print('Import successful')"
```

## Development

### Local Development (Alternative to Docker)
```bash
pip install -r requirements.txt
# Configure .env file
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Dependencies
- Python 3.11+
- FastAPI for the web framework
- PostgreSQL for data storage
- psycopg2-binary for database connectivity (dev-friendly version)

### Architecture
- `/app/api/` - API route definitions
- `/app/core/` - Core business logic
- `/app/database/` - Database models and sessions
- `/app/integrations/` - External service integrations
- `/scripts/` - Utility and startup scripts

## Troubleshooting

### Common Issues

**Environment validation fails**: Ensure `.env` file exists and contains required variables
```bash
cp .env.example .env
# Edit .env with proper values
```

**Database connection errors**: Ensure PostgreSQL container is running
```bash
docker compose logs db
docker compose ps
```

**Port conflicts**: Change ports in `docker-compose.yml` if 8000 or 5432 are in use

**Build failures**: Ensure Docker has sufficient resources and try:
```bash
docker compose down -v
docker compose build --no-cache
```

## Production Notes

- Replace `psycopg2-binary` with `psycopg2` in requirements.txt for production
- Use proper SSL certificates and HTTPS
- Set strong passwords and rotate API keys regularly
- Configure monitoring and logging appropriately
