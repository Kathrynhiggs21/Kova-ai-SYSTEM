# Kova AI Multi-Repository System - Setup Guide

Complete step-by-step guide to set up and use the Kova AI multi-repository management system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Testing](#testing)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **Docker** and **Docker Compose** installed
- **Python 3.9+** installed
- **Git** configured
- **GitHub account** with access to Kova AI repositories
- **GitHub Personal Access Token** (for multi-repo sync)
- **Anthropic API Key** (for Claude AI integration)

### Getting API Keys

#### GitHub Personal Access Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
4. Generate and **copy the token** (starts with `ghp_`)

#### Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to **API Keys**
4. Create a new key and **copy it** (starts with `sk-ant-`)

---

## Quick Start

For experienced users who want to get started quickly:

```bash
# 1. Clone the repository
git clone https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM.git
cd Kova-ai-SYSTEM

# 2. Set up environment
cd kova-ai
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN and ANTHROPIC_API_KEY

# 3. Start the system
docker-compose up -d

# 4. Test the system
cd ..
python3 scripts/test_multi_repo.py
```

---

## Detailed Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM.git
cd Kova-ai-SYSTEM
```

### Step 2: Configure Environment Variables

#### Create the .env file

```bash
cd kova-ai
cp .env.example .env
```

#### Edit .env with your credentials

Open `.env` in your favorite editor:

```bash
nano .env  # or vim, code, etc.
```

Update the following variables:

```bash
# Database Configuration (keep defaults for local dev)
POSTGRES_DB=kova
POSTGRES_USER=kova
POSTGRES_PASSWORD=kova_pass
DATABASE_URL=postgresql+asyncpg://kova:kova_pass@db:5432/kova

# API Keys (REQUIRED)
API_KEY=your_api_key_here

# Multi-Repository Management (REQUIRED)
GITHUB_TOKEN=ghp_YOUR_ACTUAL_GITHUB_TOKEN_HERE
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_ANTHROPIC_KEY_HERE

# Optional: Webhook Secret
WEBHOOK_SECRET=your_webhook_secret_here
```

**Important**: Replace the placeholder values with your actual tokens!

### Step 3: Verify Configuration

Validate your repository configuration:

```bash
cd ..  # Back to Kova-ai-SYSTEM directory
python3 scripts/validate_config.py
```

You should see output like:

```
=== Validating Kova AI Repository Configuration ===

File Existence:
  ✓ Config file found

JSON Format:
  ✓ Valid JSON format

Required Fields:
  ✓ Field 'github_owner' present and valid
  ✓ Field 'repositories' present and valid
  ...

✓ Configuration is valid!
```

### Step 4: Start the System

#### Using Docker Compose (Recommended)

```bash
cd kova-ai
docker-compose up -d
```

This will:
- Start the PostgreSQL database
- Start the FastAPI application
- Expose the API at `http://localhost:8000`

#### Check if services are running

```bash
docker-compose ps
```

You should see two services running:
- `kova-ai-api-1`
- `kova-ai-db-1`

#### View logs

```bash
docker-compose logs -f api
```

Press `Ctrl+C` to stop following logs.

### Step 5: Test the System

Run the comprehensive test suite:

```bash
cd ..  # Back to Kova-ai-SYSTEM directory
python3 scripts/test_multi_repo.py
```

You should see output like:

```
=== Kova AI Multi-Repository System Tests ===

Configuration Tests:
  ✓ PASS - Validate Config File
  ✓ PASS - Validate .env.example

API Endpoint Tests:
  ✓ PASS - Health Check
  ✓ PASS - List Repositories
  ✓ PASS - Get Config
  ✓ PASS - Get Repo Status
  ✓ PASS - Discover Repos
  ✓ PASS - Sync Repositories

=== Test Summary ===
Total Tests: 8
Passed: 8
Failed: 0
Pass Rate: 100.0%

✓ All tests passed!
```

---

## Configuration

### Repository Configuration (`kova_repos_config.json`)

The main configuration file defines all Kova AI repositories and settings.

#### Structure

```json
{
  "github_owner": "Kathrynhiggs21",
  "repositories": [...],
  "sync_settings": {...},
  "discovery_settings": {...},
  "integration_settings": {...}
}
```

#### Adding a New Repository

You can add repositories in two ways:

**Method 1: Via API (Recommended)**

```bash
curl -X POST http://localhost:8000/multi-repo/add \
  -H "Content-Type: application/json" \
  -d '{
    "repo_full_name": "Kathrynhiggs21/kova-ai-newrepo",
    "repo_type": "service",
    "description": "New service"
  }'
```

**Method 2: Manual Edit**

Edit `kova_repos_config.json`:

```json
{
  "name": "kova-ai-newrepo",
  "full_name": "Kathrynhiggs21/kova-ai-newrepo",
  "description": "New service",
  "type": "service",
  "enabled": true,
  "sync_priority": 3,
  "features": ["api", "backend"]
}
```

#### Repository Types

- **core**: Essential system components (priority 1-2)
- **service**: Microservices and APIs (priority 2-3)
- **frontend**: User interfaces (priority 3-4)
- **experimental**: Prototypes and research (priority 4-5)

#### Sync Priority

- **1**: Highest priority (syncs first)
- **2**: High priority
- **3**: Normal priority
- **4**: Low priority
- **5**: Lowest priority (syncs last)

### Sync Settings

Configure automatic synchronization behavior:

```json
{
  "sync_settings": {
    "auto_sync_enabled": true,
    "sync_interval_minutes": 30,
    "sync_on_push": true,
    "sync_on_pr": true,
    "cross_repo_notifications": true
  }
}
```

### Discovery Settings

Configure automatic repository discovery:

```json
{
  "discovery_settings": {
    "auto_discover_new_repos": true,
    "repo_name_pattern": "kova-ai-*",
    "watch_for_new_repos": true
  }
}
```

---

## Testing

### Manual API Testing

#### Check API Health

```bash
curl http://localhost:8000/health
```

#### List All Repositories

```bash
curl http://localhost:8000/multi-repo/list | jq
```

#### Get Repository Status

```bash
curl http://localhost:8000/multi-repo/status | jq
```

#### Discover New Repositories

```bash
curl http://localhost:8000/multi-repo/discover | jq
```

#### Sync All Repositories

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": false}' | jq
```

#### Sync with Claude AI Analysis

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}' | jq
```

### Automated Testing

Run the full test suite:

```bash
python3 scripts/test_multi_repo.py
```

Validate configuration only:

```bash
python3 scripts/validate_config.py
```

---

## Usage

### Common Workflows

#### 1. Check Status of All Repos

```bash
curl http://localhost:8000/multi-repo/status | jq '.data.repos'
```

This shows:
- Which repos exist on GitHub
- Last update time
- Default branch
- Open issues count

#### 2. Find New Repos

```bash
curl http://localhost:8000/multi-repo/discover | jq
```

This automatically finds any new `kova-ai-*` repositories.

#### 3. Add a New Repo to System

```bash
curl -X POST http://localhost:8000/multi-repo/add \
  -H "Content-Type: application/json" \
  -d '{
    "repo_full_name": "Kathrynhiggs21/kova-ai-analytics",
    "repo_type": "service"
  }' | jq
```

#### 4. Sync All Repos

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": false}' | jq
```

#### 5. Get AI Analysis of Repos

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}' | jq '.data.claude_results'
```

### Continuous Sync Service

Start the continuous sync service (kovai-ai):

```bash
cd kovai-ai/app/services
python3 claude_bridge_service.py
```

This will:
- Sync every 5 minutes automatically
- Auto-reload repo list from config
- Send data to Claude for analysis
- Log all activities

---

## Troubleshooting

### API Not Starting

**Problem**: Docker containers not starting

**Solution**:

```bash
# Check logs
cd kova-ai
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Authentication Errors

**Problem**: `401 Unauthorized` or `403 Forbidden`

**Solution**:

1. Verify your tokens are correct in `.env`
2. Check GitHub token scopes include `repo` and `read:org`
3. Ensure Anthropic API key is valid

```bash
# Test GitHub token
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/user

# Test Anthropic key (should return 400, not 401)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_ANTHROPIC_KEY"
```

### Rate Limiting

**Problem**: GitHub API rate limit exceeded

**Solution**:

The system has built-in retry logic with exponential backoff. Rate limits reset after 1 hour.

Check your rate limit:

```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

### Repository Not Found

**Problem**: Repo shows `exists: false`

**Solution**:

1. Create the repository on GitHub first
2. Run discovery again:

```bash
curl http://localhost:8000/multi-repo/discover
```

3. Check status:

```bash
curl http://localhost:8000/multi-repo/status
```

### Configuration Errors

**Problem**: Config file validation fails

**Solution**:

```bash
# Validate config
python3 scripts/validate_config.py

# Check for common issues:
# - Missing required fields
# - Invalid JSON syntax
# - Duplicate repositories
# - Invalid repo types
```

### Claude API Errors

**Problem**: Claude integration failing

**Solution**:

1. Verify API key in `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. Check the Claude API endpoint is correct (should be `/v1/messages`)

3. Test without Claude first:
   ```bash
   curl -X POST http://localhost:8000/multi-repo/sync \
     -H "Content-Type: application/json" \
     -d '{"include_claude": false}'
   ```

### Docker Issues

**Problem**: Port 8000 already in use

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000

# Kill it or change the port in docker-compose.yml
# Then restart
docker-compose down
docker-compose up -d
```

**Problem**: Database connection errors

**Solution**:

```bash
# Reset database
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate
```

---

## Advanced Usage

### Custom Configuration

Create environment-specific configs:

```bash
# Development
cp kova_repos_config.json kova_repos_config.dev.json

# Production
cp kova_repos_config.json kova_repos_config.prod.json
```

### Manual Sync Service Testing

Test the sync service directly:

```bash
cd kova-ai/app/services
python3 multi_repo_sync_service.py
```

### API Documentation

View interactive API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Set up webhooks**: Configure GitHub webhooks for auto-sync
3. **Create monitoring**: Set up alerts for failed syncs
4. **Customize**: Adjust sync intervals and priorities
5. **Scale**: Deploy to production with proper credentials

---

## Getting Help

- **Issues**: https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/issues
- **Documentation**: Check `MULTI_REPO_GUIDE.md` for detailed API reference
- **Validation**: Run `python3 scripts/validate_config.py` anytime
- **Testing**: Run `python3 scripts/test_multi_repo.py` to verify setup

---

## Summary

You now have a fully functional multi-repository management system! The key commands are:

```bash
# Start system
cd kova-ai && docker-compose up -d

# Test system
python3 scripts/test_multi_repo.py

# Validate config
python3 scripts/validate_config.py

# View API docs
open http://localhost:8000/docs

# Check status
curl http://localhost:8000/multi-repo/status | jq

# Sync repos
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}' | jq
```

Happy coding! 🚀
