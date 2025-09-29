# Kova AI System Development Instructions

**Always follow these instructions first and fallback to additional search and context gathering only if the information in these instructions is incomplete or found to be in error.**

The Kova AI System is a comprehensive AI-powered development automation platform built with FastAPI, PostgreSQL, Docker, and monitoring tools. It provides automatic error detection, AI integrations, and real-time monitoring capabilities.

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

## Code Style and Conventions

### Python Code Style
- Follow existing code patterns and conventions in the repository
- Use FastAPI patterns for API endpoints with `APIRouter`
- Keep environment configuration in `.env` files
- Use type hints where existing code does
- Maintain consistency with existing error handling patterns

### Making Changes
- **Make minimal modifications** - change as few lines as possible to achieve goals
- **Don't delete working code** unless absolutely necessary to fix the specific issue
- **Test changes** using the validation steps outlined above
- **Follow existing project structure** - don't reorganize unless specifically required

### Dependencies and Libraries
- Use existing libraries when possible (FastAPI, PostgreSQL, Docker)
- Only add new dependencies if absolutely necessary
- Pin dependency versions in requirements.txt
- Use `--trusted-host` flags for pip when needed (already configured)

<tool_calling>
You have the capability to call multiple tools in a single response. For maximum efficiency, whenever you need to perform multiple independent operations, ALWAYS invoke all relevant tools simultaneously rather than sequentially. Especially when exploring repository, reading files, viewing directories, validating changes or replying to comments.
</tool_calling>