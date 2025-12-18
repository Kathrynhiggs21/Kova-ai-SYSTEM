# 🚀 Kova AI System - Complete Setup Guide

## AI-Powered Development Automation Platform

Kova AI is a comprehensive, production-ready system that automatically detects and fixes code errors, processes natural language commands, and manages your entire development workflow through AI.

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Multi-Repository Management](#-multi-repository-management) 🆕
3. [File Organization System](#-file-organization-system) 🆕
4. [Files to Download](#-files-to-download)
5. [System Requirements](#-system-requirements)
6. [Installation Steps](#-installation-steps)
7. [Configuration](#-configuration)
8. [Testing the System](#-testing-the-system)
9. [AppSheet Setup](#-appsheet-setup)
10. [Features](#-features)
11. [Troubleshooting](#-troubleshooting)

## 🎯 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM.git
cd Kova-ai-SYSTEM

# 2. Run the setup script
chmod +x setup_kova_system.sh
./setup_kova_system.sh

# 3. Edit your API keys in kova-ai/.env

# 4. Access the system at http://localhost:8000
```

## 🔗 Multi-Repository Management

**NEW**: The Kova AI System now manages multiple repositories from one central hub!

### Managed Repositories

This system coordinates these Kova AI repositories:

- **Kova-ai-SYSTEM** - Main orchestration hub (this repo)
- **kova-ai** - Core backend API service
- **kova-ai-site** - Website and documentation
- **kova-ai-mem0** - Memory and persistence system
- **kova-ai-docengine** - Document processing engine
- **Kova-AI-Scribbles** - Experimental features

### Key Features

✅ **Auto-Discovery** - Automatically finds new Kova AI repos
✅ **Cross-Repo Sync** - Coordinate updates across all repos
✅ **Claude Integration** - AI analyzes all repos together
✅ **Dynamic Configuration** - Add new repos without code changes
✅ **Centralized Control** - Manage everything from one place
✅ **Production-Ready** - Retry logic, rate limiting, error handling
✅ **Comprehensive Testing** - Automated validation and test suite
✅ **Well-Documented** - Setup guides, troubleshooting, examples

### Quick Multi-Repo Commands

```bash
# Check status of all repos
curl http://localhost:8000/multi-repo/status

# Sync all repos with Claude AI
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}'

# Discover new repos
curl http://localhost:8000/multi-repo/discover

# Add a new repo
curl -X POST http://localhost:8000/multi-repo/add \
  -H "Content-Type: application/json" \
  -d '{"repo_full_name": "Kathrynhiggs21/kova-ai-newrepo"}'
```

### Testing & Validation

```bash
# Validate configuration
python3 scripts/validate_config.py

# Run full test suite
python3 scripts/test_multi_repo.py
```

📚 **Documentation:**
- **[Complete Multi-Repo Guide](MULTI_REPO_GUIDE.md)** - API reference, workflows, best practices
- **[Setup Guide](SETUP_GUIDE.md)** - Step-by-step installation and configuration

---

## 📂 File Organization System

**NEW**: Comprehensive file management system for organizing all Kova-related files from Google Drive and other sources!

### What It Does

- **Imports** all Kova-related files from Google Drive
- **Analyzes** files for relevance, duplicates, and categorization
- **Organizes** files into a structured Master Hub
- **Maintains** clean organization with automated workflows

### Key Features

✅ **Automated Import** - Scan and import from Google Drive
✅ **Smart Categorization** - Auto-categorize files by type and purpose
✅ **Duplicate Detection** - Find exact and similar duplicates
✅ **Relevance Scoring** - Score files 1-10 for importance
✅ **Purgatory System** - Isolate questionable files for review
✅ **Standardized Naming** - Consistent file naming convention
✅ **Folder Structure** - 10 main categories with subcategories

### Folder Structure

```
Kova-Master-Hub/
├── 01-Core-System/          # Architecture, docs, configs
├── 02-Repositories/         # All Kova repos
├── 03-Integrations/         # Google Drive, Claude, GitHub, etc.
├── 04-Data-Management/      # Active data, archives, backups
├── 05-Development/          # Prototypes, experiments
├── 06-Operations/           # Monitoring, maintenance, security
├── 07-Communication/        # Email, meetings, collaboration
├── 08-Resources/            # Learning, assets, references
├── 09-Purgatory/            # Files needing review
└── 10-Meta/                 # Organization tools & docs
```

### Quick Start

```bash
# 1. Set up (interactive)
./scripts/setup_kova_organization.sh

# 2. Or run manually:
# Import from Google Drive
python3 scripts/gdrive_import.py

# Organize files (dry run first!)
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory kova_file_inventory/inventory_*.json \
  --dry-run

# Execute organization
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory kova_file_inventory/inventory_*.json \
  --execute
```

### Tools Included

- **`gdrive_import.py`** - Import and analyze Google Drive files
- **`file_organizer.py`** - Organize files into Master Hub structure
- **`setup_kova_organization.sh`** - Interactive setup wizard

### Analysis Features

The system provides comprehensive file analysis:

- **Relevance Scoring**: 1-10 score based on keywords, recency, type
- **Category Detection**: CORE, INT, DATA, DEV, OPS, COM, RES
- **Duplicate Finding**: Exact name, similar name, semantic duplicates
- **Metadata Extraction**: Size, dates, owners, links

### Sample Output

```
📊 KOVA FILE ANALYSIS REPORT

📁 Total Files: 342
💾 Total Size: 1.2 GB

📂 Files by Category:
  CORE      :   45 files (13.2%)
  INT       :   78 files (22.8%)
  DATA      :   23 files (6.7%)
  ...

⭐ Files by Relevance:
  Critical (9-10)      :   23 files (6.7%)
  Important (7-8)      :   87 files (25.4%)
  Useful (5-6)         :  145 files (42.4%)
  ...

🔁 Duplicates Found: 15
```

### Maintenance Workflows

- **Daily**: Import new files from Google Drive
- **Weekly**: Review purgatory folder
- **Monthly**: Archive files older than 6 months
- **Quarterly**: Full cleanup and reorganization

📚 **Documentation:**
- **[File Organization Reference](KOVA_FILE_ORGANIZATION.md)** - Complete structure details
- **[Organization Guide](KOVA_ORGANIZATION_GUIDE.md)** - Step-by-step usage guide

---

## 📦 Complete Platform Structure

All required files are included in this repository and organized as follows:

### Essential Files (All Included!)

1. **`setup_kova_system.sh`** - Main installation script ✅
2. **`docker-compose.yml`** - Docker services configuration ✅
3. **`Dockerfile`** - Container configuration ✅
4. **`requirements.txt`** - Python dependencies ✅
5. **`.env.example`** - Environment configuration template ✅
6. **`app/main.py`** - Main application file ✅
7. **`scripts/init.sql`** - Database initialization ✅
8. **`appsheet_config.json`** - AppSheet dashboard configuration ✅

### Current Repository Structure

```
Kova-ai-SYSTEM/
├── setup_kova_system.sh
├── verify_platform.sh
├── kova-ai/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── ai_endpoints.py
│   │   │   └── webhooks.py
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   └── (other modules)
│   ├── scripts/
│   │   └── init.sql
│   ├── monitoring/
│   │   ├── prometheus/
│   │   └── grafana/
│   ├── deployment/
│   │   ├── nginx/
│   │   └── kubernetes/
│   └── appsheet_config.json
```

## 💻 System Requirements

### Required Software
- **Docker** & **Docker Compose** (latest versions)
- **Python 3.11+**
- **Git**
- **4GB RAM minimum** (8GB recommended)
- **10GB free disk space**

### Required API Keys
You'll need to obtain these API keys:

1. **OpenAI API Key** (Required)
   - Get from: https://platform.openai.com/api-keys
   - Cost: ~$0.01-0.03 per request

2. **Anthropic API Key** (Required)
   - Get from: https://console.anthropic.com/
   - Cost: ~$0.01-0.03 per request

3. **GitHub Personal Access Token** (Required)
   - Get from: https://github.com/settings/tokens
   - Permissions needed: repo, webhook

4. **Pinecone API Key** (Required)
   - Get from: https://www.pinecone.io/
   - Free tier available

5. **Google Cloud Service Account** (Optional)
   - For Google Workspace integration

## 📝 Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM.git
cd Kova-ai-SYSTEM

# Verify platform completeness (optional)
chmod +x verify_platform.sh
./verify_platform.sh
```

### Step 2: Configure Environment

```bash
# Copy environment template
cd kova-ai
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or your preferred editor
```

#### `kova-ai/.env` (fill in your actual values)
```bash
# MUST FILL THESE:
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GITHUB_TOKEN=ghp_your-actual-token-here
PINECONE_API_KEY=your-actual-key-here
```

### Step 3: Run Installation

```bash
# Return to root directory
cd ..

# Make script executable and run
chmod +x setup_kova_system.sh
./setup_kova_system.sh
```

# Run installation
./setup_kova_system.sh
```

### Step 4: Verify Installation

```bash
# Check if services are running
docker-compose ps

# Test the API
curl http://localhost:8000/health

# View logs
docker-compose logs -f api
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file with your actual values:

```bash
# Essential (MUST configure)
OPENAI_API_KEY=sk-...          # Your OpenAI key
ANTHROPIC_API_KEY=sk-ant-...   # Your Anthropic key
GITHUB_TOKEN=ghp_...            # Your GitHub token
PINECONE_API_KEY=...            # Your Pinecone key

# Optional (can use defaults)
POSTGRES_PASSWORD=...           # Database password
SECRET_KEY=...                  # JWT secret key
ADMIN_EMAIL=...                 # Admin email
```

### GitHub Webhook Setup

1. Go to your repository settings on GitHub
2. Add webhook:
   - URL: `http://your-domain:8000/webhooks/github`
   - Content type: `application/json`
   - Secret: (same as GITHUB_WEBHOOK_SECRET in .env)
   - Events: Push, Pull Request, Issues

## 🧪 Testing the System

### Basic Health Check
```bash
curl http://localhost:8000/health
```

### Test AI Command
```bash
curl -X POST http://localhost:8000/ai/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create a REST API for user management"}'
```

### Test Error Scanning
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"name": "test-repo"}'
```

### Access Dashboards
- **API Documentation**: http://localhost:8000/docs
- **Grafana Monitoring**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090

## 📱 AppSheet Setup

### Import Configuration

1. Open Google AppSheet: https://www.appsheet.com/
2. Create new app → Start with your own data
3. Choose "Import from JSON"
4. Upload `appsheet_config.json`
5. Configure data source:
   - URL: Your API endpoint (e.g., http://your-domain:8000)
   - Authentication: API Key (from your .env file)

### Configure Tables

1. Go to Data → Tables
2. For each table, set:
   - Source: REST API
   - Endpoint: As specified in JSON
   - Authentication: Bearer token

### Deploy App

1. Go to Deploy → Deployment Check
2. Fix any warnings
3. Click "Deploy App"
4. Share with your team

## ✨ Features

### Core Capabilities

- **🔍 Automatic Error Detection**
  - Syntax errors
  - Security vulnerabilities
  - Performance issues
  - Style violations

- **🔧 Auto-Fix System**
  - High-confidence automatic fixes
  - Rollback on failure
  - Test validation

- **🤖 AI Integration**
  - GPT-4 for code generation
  - Claude for code analysis
  - Natural language commands

- **📊 Real-time Monitoring**
  - WebSocket updates
  - Grafana dashboards
  - Prometheus metrics

- **🔗 Integrations**
  - GitHub webhooks
  - Google Workspace
  - Slack notifications
  - AppSheet dashboard

## 🐛 Troubleshooting

### Common Issues

#### Services won't start
```bash
# Check Docker
docker --version
docker-compose --version

# Reset everything
docker-compose down -v
docker-compose up -d
```

#### Database connection errors
```bash
# Check PostgreSQL
docker-compose logs postgres

# Reinitialize database
docker-compose exec postgres psql -U kova -d kova < scripts/init.sql
```

#### API key errors
```bash
# Verify .env file
cat kova-ai/.env | grep API_KEY

# Restart services after changing .env
docker-compose restart
```

#### Port conflicts
```bash
# Check ports
netstat -tulpn | grep -E '8000|5432|6379|3000'

# Change ports in docker-compose.yml if needed
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v
rm -rf postgres_data redis_data

# Restart fresh
./setup_kova_system.sh
```

## 📚 API Documentation

Once running, access interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /ai/command` - Execute AI command
- `POST /api/scan` - Scan repository
- `POST /webhooks/github` - GitHub webhook
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## 🔒 Security Notes

1. **Change default passwords** in production
2. **Use HTTPS** with proper SSL certificates
3. **Restrict API access** with authentication
4. **Keep API keys secure** and rotate regularly
5. **Enable firewall** for production deployment

## 🚀 Production Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Enable SSL/TLS with Let's Encrypt
3. Use managed databases (RDS, Cloud SQL)
4. Implement proper logging (ELK stack)
5. Set up backup strategies
6. Use Kubernetes for orchestration

## 📞 Support

- **Documentation**: Check `/docs` endpoint
- **Logs**: `docker-compose logs -f`
- **Health Check**: `curl http://localhost:8000/health`

## 🎉 Success!

Your Kova AI System is now ready! The system will:
- ✅ Continuously scan for errors
- ✅ Auto-fix issues with high confidence
- ✅ Process natural language commands
- ✅ Learn from your codebase
- ✅ Provide real-time monitoring

Access your system at: **http://localhost:8000**

---

**Enjoy your AI-powered development platform! 🚀**
