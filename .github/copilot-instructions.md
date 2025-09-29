# Kova AI System Development Instructions

**Always follow these instructions first and fallback to additional search and context gathering only if the information in these instructions is incomplete or found to be in error.**

## Project Overview

The Kova AI System is a comprehensive AI-powered development automation platform built with FastAPI, PostgreSQL, Docker, and monitoring tools. It provides automatic error detection, AI integrations, and real-time monitoring capabilities.

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus & Grafana
- **AI Integration**: OpenAI GPT-4, Anthropic Claude
- **Version Control**: Git with GitHub webhooks
- **Deployment**: Kubernetes-ready with Nginx

### Architecture Principles
- **Microservices**: Containerized services with clear separation of concerns
- **API-First**: RESTful API with comprehensive OpenAPI documentation
- **Event-Driven**: GitHub webhooks trigger automated workflows
- **Observability**: Built-in metrics, logging, and health checks
- **Security**: Environment-based configuration, API key management

## Working Effectively

### System Requirements
- **Docker** & **Docker Compose** (latest versions) - REQUIRED
- **Python 3.11+** (for local development)
- **Git**
- **4GB RAM minimum** (8GB recommended)
- **10GB free disk space**

### Bootstrap and Build (Docker - Recommended)
Run these commands in sequence from the repository root:

```bash
# Verify platform completeness (optional but recommended)
chmod +x verify_platform.sh
./verify_platform.sh

# Setup and build system
chmod +x setup_kova_system.sh
./setup_kova_system.sh
```

**TIMING**: Complete Docker setup takes approximately 25-30 seconds. **NEVER CANCEL** builds. Set timeout to 60+ minutes if using automation.

**NOTE**: The Dockerfile has been fixed to handle SSL certificate issues with `--trusted-host` flags for pip installations.

### Alternative Local Development Setup
If Docker is not available, you can run the application locally:

```bash
cd kova-ai

# Install Python dependencies
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**TIMING**: Local Python setup takes 30-60 seconds for dependency installation. **NEVER CANCEL** pip installs.

### Environment Configuration
Before running the system, you MUST configure API keys in `kova-ai/.env`:

```bash
# Essential API keys (MUST configure for full functionality)
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GITHUB_TOKEN=ghp_your-actual-token-here
PINECONE_API_KEY=your-actual-key-here

# Database configuration (defaults work for development)
POSTGRES_DB=kova
POSTGRES_USER=kova
POSTGRES_PASSWORD=kova_pass
```

### Managing the System

#### Docker Commands (Primary Method)
```bash
cd kova-ai

# Start services
docker compose up -d

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f api
docker compose logs -f db

# Stop services
docker compose down

# Reset everything (if needed)
docker compose down -v
rm -rf postgres_data redis_data
./setup_kova_system.sh
```

#### Service Status Check
```bash
# Check running containers
docker compose ps

# Check API health
curl http://localhost:8000/health
```

### Key Access Points
When the system is running, access these URLs:

- **API Health**: http://localhost:8000/health
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Prometheus Metrics**: http://localhost:8000/metrics

## Validation and Testing

### ALWAYS Run These Validation Steps
After making any changes to the codebase:

1. **Verify Platform**: `./verify_platform.sh`
2. **Build and Start**: `./setup_kova_system.sh` (NEVER CANCEL - takes ~25 seconds)
3. **Test Health Endpoint**: `curl http://localhost:8000/health`
4. **Test AI Command**: 
   ```bash
   curl -X POST http://localhost:8000/ai/command \
     -H "Content-Type: application/json" \
     -d '{"command": "test command"}'
   ```
5. **Verify Documentation**: Access http://localhost:8000/docs in browser

### Manual Testing Scenarios
**CRITICAL**: Always manually validate these complete scenarios after making changes:

#### Scenario 1: Basic API Functionality
1. Start the system with `./setup_kova_system.sh`
2. Verify health endpoint returns `{"status":"ok"}`
3. Test AI command endpoint with sample data
4. Check Swagger documentation loads correctly
5. Verify metrics endpoint is accessible

#### Scenario 2: Database Integration
1. Ensure PostgreSQL container is running
2. Verify database schema exists (check init.sql is applied)
3. Test any database-dependent endpoints

#### Scenario 3: Environment Configuration
1. Modify .env file with test values
2. Restart services: `docker compose restart`
3. Verify configuration changes take effect

### No Automated Testing Infrastructure
**IMPORTANT**: This repository does not have pytest, flake8, or black configured. Manual testing is required.

## Development Workflows

### Making Code Changes
1. **Start Development Environment**:
   ```bash
   cd /path/to/Kova-ai-SYSTEM
   ./setup_kova_system.sh  # Initial setup
   cd kova-ai
   docker compose up -d    # Start services
   ```

2. **Code Development Cycle**:
   - Make changes to Python files in `kova-ai/app/`
   - Container auto-reloads on file changes (volume mounting)
   - Test immediately: `curl http://localhost:8000/health`
   - Check logs: `docker compose logs -f api`

3. **Adding New Features**:
   - Follow the file organization in `app/` directory
   - Add routers to appropriate `api/` files
   - Update main.py to include new routers
   - Test endpoints via `/docs` Swagger UI

4. **Database Changes**:
   - Modify `scripts/init.sql` for schema changes
   - Reset database: `docker compose down -v && ../setup_kova_system.sh`
   - Verify changes in database client or API responses

5. **Configuration Updates**:
   - Modify `.env` file for environment variables
   - Restart services: `docker compose restart`
   - Verify changes take effect through API calls

### Debugging Workflows
1. **API Issues**:
   ```bash
   # Check API logs
   docker compose logs -f api
   
   # Test specific endpoints
   curl -v http://localhost:8000/health
   curl -X POST http://localhost:8000/ai/command -H "Content-Type: application/json" -d '{"command": "test"}'
   ```

2. **Database Issues**:
   ```bash
   # Check database logs
   docker compose logs -f db
   
   # Connect to database
   docker compose exec db psql -U kova -d kova
   ```

3. **Container Issues**:
   ```bash
   # Check container status
   docker compose ps
   
   # Restart specific service
   docker compose restart api
   
   # Reset everything
   docker compose down -v && ../setup_kova_system.sh
   ```

### Integration Testing
1. **GitHub Webhooks**:
   - Configure webhook in repository settings
   - URL: `http://your-domain:8000/webhooks/github`
   - Test with repository events (push, PR, issues)

2. **AI Endpoints**:
   - Ensure API keys are configured in `.env`
   - Test AI command processing
   - Verify responses are properly formatted

3. **Monitoring**:
   - Access Prometheus: http://localhost:9090
   - Access Grafana: http://localhost:3000
   - Verify metrics collection at `/metrics`

## Common Development Tasks

### Key Project Files and Directories
```
Kova-ai-SYSTEM/
├── setup_kova_system.sh       # Main installation script
├── verify_platform.sh         # Platform verification
├── kova-ai/
│   ├── docker-compose.yml     # Docker services configuration
│   ├── Dockerfile             # Container configuration (SSL fixed)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── api/              # API endpoints
│   │   │   ├── health.py     # Health check endpoint
│   │   │   ├── ai_endpoints.py # AI command processing
│   │   │   └── webhooks.py   # GitHub webhooks
│   │   ├── database/         # Database models and sessions
│   │   ├── core/             # Core business logic
│   │   ├── security/         # Authentication and security
│   │   ├── tasks/            # Background tasks
│   │   ├── utils/            # Utility functions
│   │   └── integrations/     # External service integrations
│   ├── scripts/
│   │   ├── init.sql          # Database schema initialization
│   │   └── quickstart.sh     # Alternative startup script
│   ├── monitoring/
│   │   ├── prometheus/       # Prometheus configuration
│   │   └── grafana/          # Grafana dashboards
│   ├── deployment/
│   │   ├── nginx/            # Nginx configuration
│   │   └── kubernetes/       # Kubernetes manifests
│   └── appsheet_config.json  # AppSheet integration config
```

### API Endpoints
The application exposes these key endpoints:
- `GET /health` - Health check (always returns `{"status":"ok"}`)
- `POST /ai/command` - Execute AI commands
- `POST /webhooks/github` - GitHub webhook handler
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /metrics` - Prometheus metrics

### Modifying API Endpoints
When changing API endpoints in `kova-ai/app/api/`:
1. Always check that router definitions exist (`router = APIRouter`)
2. Restart the application to see changes
3. Verify changes appear in `/docs` Swagger UI
4. Test the endpoint with curl or HTTP client

### Database Changes
Database schema is defined in `kova-ai/scripts/init.sql`:
- `repository` table: stores repository information
- `error` table: stores error logs with timestamps

For schema changes:
1. Modify `init.sql`
2. Reset database: `docker compose down -v && (cd .. && ./setup_kova_system.sh)`
3. Verify schema changes with database client

## Troubleshooting

### Common Issues and Solutions

#### Docker Build Failures
**Symptom**: SSL certificate errors during pip install
**Solution**: The Dockerfile includes `--trusted-host` flags (already fixed)

#### Services Won't Start
```bash
# Check Docker
docker --version
docker compose version

# Reset everything
docker compose down -v
./setup_kova_system.sh
```

#### Database Connection Errors
```bash
# Check PostgreSQL logs
docker compose logs db

# Verify database is running
docker compose ps
```

#### API Key Errors
```bash
# Verify .env file exists and has values
cat kova-ai/.env | grep API_KEY

# Restart services after changing .env
docker compose restart
```

#### Port Conflicts
```bash
# Check if ports are in use
netstat -tulpn | grep -E '8000|5432'

# Change ports in docker-compose.yml if needed
```

### Logs and Debugging
```bash
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f db

# Follow logs in real-time while testing
docker compose logs -f api &
curl http://localhost:8000/health
```

## Critical Timing and Timeout Information

### **NEVER CANCEL** Operations
- **Docker Build**: 25-30 seconds typical, can take up to 5 minutes on slow networks
- **Service Startup**: 10-15 seconds for all containers to be ready
- **Database Initialization**: 5-10 seconds for PostgreSQL to accept connections

### Recommended Timeouts for Automation
- **Build commands**: Set timeout to 300 seconds (5 minutes) minimum
- **Service startup**: Set timeout to 60 seconds minimum
- **Health checks**: Set timeout to 30 seconds minimum

## Environment Management

### Development Environment Setup
```bash
# Always start from repository root
cd /path/to/Kova-ai-SYSTEM

# Verify platform before starting
./verify_platform.sh

# Setup environment (creates .env from .env.example)
./setup_kova_system.sh

# Edit API keys (REQUIRED for full functionality)
cd kova-ai && nano .env
```

### Required Environment Variables
Essential variables that MUST be configured:
```bash
# AI Service Keys (REQUIRED)
OPENAI_API_KEY=sk-...              # OpenAI GPT-4 integration
ANTHROPIC_API_KEY=sk-ant-...       # Anthropic Claude integration
GITHUB_TOKEN=ghp_...               # GitHub API access
PINECONE_API_KEY=...               # Vector database for AI

# Database (defaults work for development)
POSTGRES_DB=kova
POSTGRES_USER=kova
POSTGRES_PASSWORD=kova_pass

# Security (generate secure values for production)
SECRET_KEY=your-secret-key-here
GITHUB_WEBHOOK_SECRET=webhook-secret
```

### API Key Validation
Test API keys are working:
```bash
# Test OpenAI integration
curl -X POST http://localhost:8000/ai/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test openai connection"}'

# Test GitHub integration
curl -X POST http://localhost:8000/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "Design for failure."}'
```

## Container Management Best Practices

### Service Dependencies
Services start in this order:
1. **Database (PostgreSQL)**: Must be ready before API
2. **API (FastAPI)**: Depends on database connection
3. **Monitoring**: Independent services (Prometheus, Grafana)

### Volume Management
```bash
# Persistent data volumes
db_data:/var/lib/postgresql/data    # Database storage
.:/app                              # Code volume (live reload)

# Reset persistent data
docker compose down -v              # Removes volumes
rm -rf postgres_data redis_data     # Clean local data
```

### Log Management
```bash
# Real-time monitoring
docker compose logs -f              # All services
docker compose logs -f api          # API only
docker compose logs -f db           # Database only

# Log analysis
docker compose logs api | grep ERROR
docker compose logs db | grep -i "ready to accept"
```

## Production Deployment Notes

### Security Checklist
1. **Change default passwords** in production
2. **Use HTTPS** with proper SSL certificates
3. **Restrict API access** with authentication
4. **Keep API keys secure** and rotate regularly
5. **Enable firewall** for production deployment

### Monitoring Setup
The system includes Prometheus metrics at `/metrics` endpoint. Configure external monitoring tools to scrape:
- `http://your-domain:8000/metrics`

Grafana dashboards are available in `monitoring/grafana/` directory.

## Coding Standards and Best Practices

### Python Code Style
- **Follow PEP 8**: Use standard Python style conventions
- **Type Hints**: Always include type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings for all functions and classes
- **Error Handling**: Use proper exception handling with specific exception types
- **Async/Await**: Use async/await for I/O operations (database, API calls)

### FastAPI Conventions
- **Router Organization**: Group related endpoints in separate router files
- **Dependency Injection**: Use FastAPI's dependency system for database sessions, authentication
- **Pydantic Models**: Define request/response models using Pydantic BaseModel
- **Status Codes**: Use appropriate HTTP status codes (200, 201, 400, 401, 404, 500)
- **OpenAPI Tags**: Tag endpoints for better documentation organization

### Database Patterns
- **SQLAlchemy ORM**: Use SQLAlchemy models for database operations
- **Connection Pooling**: Database sessions managed through dependency injection
- **Migrations**: Schema changes should be documented in `scripts/init.sql`
- **Transactions**: Use database transactions for multi-step operations

### API Design
- **RESTful URLs**: Follow REST conventions for endpoint naming
- **Consistent Responses**: All endpoints return JSON with consistent structure
- **Error Responses**: Use standard error format with `detail` field
- **Pagination**: Implement offset/limit pagination for list endpoints
- **Filtering**: Support query parameters for filtering results

### Security Practices
- **Environment Variables**: Never hardcode secrets, use `.env` files
- **API Keys**: Validate API keys in headers or query parameters
- **Input Validation**: Validate all inputs using Pydantic models
- **CORS**: Configure CORS appropriately for production
- **Rate Limiting**: Implement rate limiting for public endpoints

### Testing Approach
- **Manual Testing**: Use curl commands for API endpoint testing
- **Health Checks**: Always verify `/health` endpoint first
- **Docker Testing**: Test in containerized environment matching production
- **Integration Testing**: Test complete workflows including database operations
- **API Documentation**: Verify changes appear correctly in `/docs` Swagger UI

### File Organization
```
app/
├── main.py              # FastAPI app initialization, CORS, middleware
├── api/                 # API endpoints grouped by functionality
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   ├── ai_endpoints.py  # AI command processing endpoints
│   └── webhooks.py      # GitHub webhook handlers
├── database/            # Database models and sessions
│   ├── __init__.py
│   ├── models.py        # SQLAlchemy models
│   └── session.py       # Database session management
├── core/                # Core business logic
├── security/            # Authentication and security utilities
├── tasks/               # Background task definitions
├── utils/               # Shared utility functions
└── integrations/        # External service integrations
```

### Common Patterns
1. **Adding New Endpoints**:
   - Create router in appropriate `api/` file
   - Define Pydantic request/response models
   - Add router to `main.py`
   - Test with curl and verify in `/docs`

2. **Database Operations**:
   - Use dependency injection for database sessions
   - Define SQLAlchemy models in `database/models.py`
   - Use proper exception handling for database errors

3. **External API Calls**:
   - Use async HTTP clients (httpx)
   - Implement proper timeout and retry logic
   - Handle API key authentication in headers

## Additional Information

### Platform Verification
Always run `./verify_platform.sh` before reporting issues. This script checks:
- Required files and directory structure
- Python syntax validation
- Docker configuration validity
- API router definitions

### Performance Expectations
- **API Response Time**: < 100ms for health endpoint
- **Memory Usage**: ~100MB for API container, ~50MB for PostgreSQL
- **Startup Time**: Complete system ready in 30-45 seconds

### Integration Points
- **GitHub Webhooks**: Configure webhooks to point to `/webhooks/github`
- **AppSheet**: Configuration in `appsheet_config.json`
- **External APIs**: OpenAI, Anthropic, Pinecone integrations via environment variables

## Quick Reference

### Essential Commands
```bash
# Initial Setup
./verify_platform.sh                    # Verify system completeness
./setup_kova_system.sh                  # One-time setup and build
cd kova-ai && nano .env                 # Configure API keys

# Daily Development
docker compose up -d                    # Start services
docker compose logs -f api              # Monitor API logs
curl http://localhost:8000/health       # Test API health
docker compose down                     # Stop services

# Troubleshooting
docker compose ps                       # Check service status
docker compose restart api             # Restart API service
docker compose down -v && ../setup_kova_system.sh  # Reset everything
```

### Key URLs (when running)
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### File Locations
- **API Code**: `kova-ai/app/`
- **Environment**: `kova-ai/.env`
- **Database Schema**: `kova-ai/scripts/init.sql`
- **Docker Config**: `kova-ai/docker-compose.yml`
- **Setup Script**: `setup_kova_system.sh`

### Common Test Commands
```bash
# Health check
curl http://localhost:8000/health

# Test AI endpoint
curl -X POST http://localhost:8000/ai/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test"}'

# Test webhook
curl -X POST http://localhost:8000/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}'
```

### Development Workflow Summary
1. **Setup**: Run `./setup_kova_system.sh` once
2. **Configure**: Edit `kova-ai/.env` with API keys
3. **Develop**: Make changes in `kova-ai/app/` (auto-reload enabled)
4. **Test**: Use curl commands or visit `/docs`
5. **Debug**: Check logs with `docker compose logs -f api`
6. **Reset**: Use `docker compose down -v && ../setup_kova_system.sh` if needed