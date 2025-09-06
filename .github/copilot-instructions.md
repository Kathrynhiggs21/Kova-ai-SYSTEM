# Kova AI System - GitHub Copilot Instructions

Kova AI is a comprehensive AI-powered development automation platform built with FastAPI, Docker, and PostgreSQL. The system automatically detects and fixes code errors, processes natural language commands, and manages development workflows through AI integration.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Prerequisites and Environment Setup
- **Python Version**: Python 3.11+ (Python 3.12.3 confirmed working)
- **Docker**: Required for containerized deployment
- **Database**: PostgreSQL 15 (via Docker)
- **Package Manager**: pip with trusted hosts for SSL issues

### Bootstrap and Build Process

**CRITICAL**: The Docker build process will fail in sandboxed environments due to SSL certificate verification issues with PyPI. Use the local development approach instead.

#### Platform Verification (Always run first)
```bash
chmod +x verify_platform.sh
./verify_platform.sh
```
- **Expected time**: 10-15 seconds
- **Purpose**: Validates all required files and structure are present
- **Expected output**: "All required files and structure are present!"

#### Docker Build (Known to fail in sandboxed environments)
```bash
# This WILL FAIL due to SSL certificate issues - documented limitation
chmod +x setup_kova_system.sh
./setup_kova_system.sh
```
- **Expected time**: 20-30 seconds before SSL failure
- **Known issue**: SSL certificate verification fails with PyPI in sandboxed environments
- **Error message**: "certificate verify failed: self-signed certificate in certificate chain"

#### Local Development Setup (RECOMMENDED)
```bash
cd kova-ai

# Install dependencies with trusted hosts to bypass SSL issues
python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fastapi uvicorn[standard] asyncpg sqlalchemy psycopg2-binary python-dotenv prometheus-client httpx
```
- **Expected time**: 30-60 seconds
- **NEVER CANCEL**: Wait for complete installation

#### Environment Configuration
```bash
cd kova-ai
cp .env.example .env
# Edit .env with actual API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN, PINECONE_API_KEY)
```

### Running the Application

#### Start FastAPI Application (Local Development)
```bash
cd kova-ai
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 9999 --log-level info
```
- **Expected time**: 2-3 seconds to start
- **Access points**:
  - Health endpoint: `http://127.0.0.1:9999/health`
  - API Documentation: `http://127.0.0.1:9999/docs`
  - ReDoc: `http://127.0.0.1:9999/redoc`

#### Docker Compose (When SSL issues are resolved)
```bash
cd kova-ai
docker-compose up --build -d
```
- **Expected time**: 3-5 minutes for initial build. NEVER CANCEL.
- **Timeout**: Set timeout to 10+ minutes for Docker builds

### Testing and Validation

#### Basic Health Check
```bash
curl http://127.0.0.1:9999/health
# Expected response: {"status":"ok"}
```

#### Test AI Command Endpoint
```bash
curl -X POST http://127.0.0.1:9999/ai/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test command"}'
# Expected response: {"received":{"command":"test command"}}
```

#### Manual Validation Scenarios
**ALWAYS** perform these validation steps after making changes:

1. **Import Test**: Verify all modules can be imported
   ```bash
   cd kova-ai
   python3 -c "import app.main; print('Import successful')"
   python3 -c "from app.main import app; print('FastAPI app loaded')"
   ```

2. **Endpoint Functionality**: Test core API endpoints
   ```bash
   # Start server first
   python3 -m uvicorn app.main:app --host 127.0.0.1 --port 9999 &
   
   # Test endpoints
   curl http://127.0.0.1:9999/health
   curl -X POST http://127.0.0.1:9999/ai/command -H "Content-Type: application/json" -d '{"command": "test"}'
   
   # Stop server
   pkill -f uvicorn
   ```

3. **Swagger Documentation**: Verify API docs load correctly
   ```bash
   curl -s http://127.0.0.1:9999/docs | head -5
   # Should return HTML with Swagger UI references
   ```

### Build Times and Timeouts

- **Platform verification**: 10-15 seconds
- **Python dependency installation**: 30-60 seconds. **NEVER CANCEL**
- **FastAPI startup**: 2-3 seconds
- **Docker build** (when working): 3-5 minutes. **NEVER CANCEL** - Set timeout to 10+ minutes
- **Database initialization**: 30-60 seconds

### Repository Structure

#### Key Directories
- `kova-ai/` - Main application directory
- `kova-ai/app/` - FastAPI application code
- `kova-ai/app/api/` - API endpoints (health, ai_endpoints, webhooks)
- `kova-ai/app/database/` - Database models and session management
- `kova-ai/app/core/` - Core application logic
- `kova-ai/monitoring/` - Prometheus and Grafana configurations
- `kova-ai/deployment/` - Kubernetes and Nginx configurations

#### Important Files
- `setup_kova_system.sh` - Main setup script (fails in sandboxed environments)
- `verify_platform.sh` - Platform verification script
- `kova-ai/docker-compose.yml` - Docker services configuration
- `kova-ai/requirements.txt` - Python dependencies
- `kova-ai/app/main.py` - FastAPI application entry point
- `kova-ai/.env.example` - Environment configuration template

### Common Development Tasks

#### Adding New API Endpoints
1. Create endpoint in appropriate file under `kova-ai/app/api/`
2. Follow existing pattern with APIRouter
3. Import and include router in `kova-ai/app/main.py`
4. Test manually with curl commands

#### Database Changes
1. Modify models in `kova-ai/app/database/models.py`
2. Update session configuration if needed in `kova-ai/app/database/session.py`
3. Test database connectivity (requires PostgreSQL instance)

#### Monitoring and Metrics
- Prometheus configuration: `kova-ai/monitoring/prometheus/prometheus.yml`
- Grafana datasource: `kova-ai/monitoring/grafana/datasources/prometheus.yml`
- Metrics endpoint: `/metrics` (built into FastAPI app)

### Known Issues and Limitations

1. **SSL Certificate Issues**: Docker builds fail in sandboxed environments due to PyPI SSL verification
   - **Workaround**: Use local development with `--trusted-host` flags
   - **Not fixable**: This is an environment limitation, not a code issue

2. **Database Dependency**: PostgreSQL required for full functionality
   - **Development**: App starts without DB but some endpoints may fail
   - **Production**: Requires PostgreSQL 15+ instance

3. **Port Conflicts**: Default port 8000 may be occupied
   - **Solution**: Use alternative ports (e.g., 9999) for testing

### Validation Checklist

Before completing any changes, **ALWAYS**:
- [ ] Run platform verification: `./verify_platform.sh`
- [ ] Test Python imports: `python3 -c "import app.main"`
- [ ] Start application: `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 9999`
- [ ] Test health endpoint: `curl http://127.0.0.1:9999/health`
- [ ] Test AI command endpoint with sample data
- [ ] Verify Swagger docs are accessible
- [ ] Check application logs for errors

### Quick Reference Commands

```bash
# Complete validation workflow
cd /path/to/Kova-ai-SYSTEM
./verify_platform.sh
cd kova-ai
python3 -c "import app.main; print('OK')"
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 9999 &
sleep 2
curl http://127.0.0.1:9999/health
curl -X POST http://127.0.0.1:9999/ai/command -H "Content-Type: application/json" -d '{"test": "data"}'
pkill -f uvicorn
```

## API Documentation

### Core Endpoints
- `GET /health` - Health check endpoint (always test this first)
- `POST /ai/command` - AI command processing endpoint
- `POST /webhooks/github` - GitHub webhook handler
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /metrics` - Prometheus metrics

### Response Formats
- Health: `{"status": "ok"}`
- AI Command: `{"received": <input_data>}`

### Environment Variables (Required for production)
- `OPENAI_API_KEY` - OpenAI API integration
- `ANTHROPIC_API_KEY` - Claude AI integration  
- `GITHUB_TOKEN` - GitHub API access
- `PINECONE_API_KEY` - Vector database integration
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database configuration

**Remember**: Always use the local development approach for testing and validation in sandboxed environments. The Docker approach is intended for production deployments where SSL certificate issues are resolved.