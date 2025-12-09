# Kova AI Multi-Repository Management Guide

## Overview

The Kova AI System now supports **multi-repository management**, enabling you to coordinate, sync, and manage all your Kova AI projects from a single central system.

## Architecture

```
Kova-ai-SYSTEM (Central Hub)
├── kova_repos_config.json          # Central configuration
├── kova-ai/                         # Main backend service
│   └── app/
│       ├── api/
│       │   ├── multi_repo_endpoints.py  # Multi-repo API
│       │   └── ai_endpoints.py          # Enhanced with multi-repo
│       └── services/
│           └── multi_repo_sync_service.py  # Core sync service
└── kovai-ai/                        # Async Claude bridge
    └── app/services/
        └── claude_bridge_service.py # Updated for multi-repo
```

## Configured Repositories

Your Kova AI system currently manages these repositories:

| Repository | Type | Purpose |
|------------|------|---------|
| **Kova-ai-SYSTEM** | Core | Main system orchestration |
| **kova-ai** | Core | Backend API service |
| **kova-ai-site** | Frontend | Website & documentation |
| **kova-ai-mem0** | Service | Memory & persistence |
| **kova-ai-docengine** | Service | Document processing (NEW) |
| **Kova-AI-Scribbles** | Experimental | Prototypes & research |

## How It Works

### 1. Claude Code Works on One Repo at a Time

**Important**: Claude Code operates in one repository directory at a time (currently `Kova-ai-SYSTEM`).

However, through the **Multi-Repo Sync Service**, this single repository can:
- ✅ Monitor all other Kova AI repos
- ✅ Sync data across all repos
- ✅ Coordinate updates between repos
- ✅ Auto-discover new repos
- ✅ Send data to Claude API for analysis

### 2. Central Configuration

All repositories are managed through `kova_repos_config.json`:

```json
{
  "github_owner": "Kathrynhiggs21",
  "repositories": [
    {
      "name": "kova-ai-docengine",
      "full_name": "Kathrynhiggs21/kova-ai-docengine",
      "type": "service",
      "enabled": true,
      "sync_priority": 2
    }
  ],
  "sync_settings": {
    "auto_sync_enabled": true,
    "sync_interval_minutes": 30
  }
}
```

## API Endpoints

### Multi-Repo Management

Access these endpoints at `http://localhost:8000/multi-repo/`

#### 1. Get Status of All Repos
```bash
curl http://localhost:8000/multi-repo/status
```

Response:
```json
{
  "status": "success",
  "data": {
    "total_repos": 6,
    "repos": {
      "Kathrynhiggs21/kova-ai-docengine": {
        "exists": false,
        "status": "not_found_or_planned"
      },
      "Kathrynhiggs21/kova-ai": {
        "exists": true,
        "updated_at": "2025-10-20T10:45:56Z",
        "default_branch": "main"
      }
    }
  }
}
```

#### 2. Sync All Repositories
```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}'
```

#### 3. Discover New Repos
```bash
curl http://localhost:8000/multi-repo/discover
```

This automatically finds any new `kova-ai-*` repositories you've created.

#### 4. Add a New Repository
```bash
curl -X POST http://localhost:8000/multi-repo/add \
  -H "Content-Type: application/json" \
  -d '{
    "repo_full_name": "Kathrynhiggs21/kova-ai-newrepo",
    "repo_type": "service",
    "description": "New Kova AI service"
  }'
```

#### 5. List All Repositories
```bash
curl http://localhost:8000/multi-repo/list
```

## Workflows

### Workflow 1: Adding a New Repository

**When you create a new Kova AI repo:**

1. **Create the repo on GitHub** (e.g., `kova-ai-analytics`)

2. **Add it to the system** (automatically):
   ```bash
   curl http://localhost:8000/multi-repo/discover
   ```

3. **Or add manually**:
   ```bash
   curl -X POST http://localhost:8000/multi-repo/add \
     -H "Content-Type: application/json" \
     -d '{
       "repo_full_name": "Kathrynhiggs21/kova-ai-analytics",
       "repo_type": "service"
     }'
   ```

4. **Verify it was added**:
   ```bash
   curl http://localhost:8000/multi-repo/list
   ```

### Workflow 2: Syncing All Repos

**To sync all repos with Claude AI:**

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}'
```

This will:
- Fetch latest data from all repos
- Send to Claude API for analysis
- Return comprehensive sync results

### Workflow 3: Checking Repo Status

**Before creating a new repo, check if it exists:**

```bash
curl http://localhost:8000/multi-repo/status | jq '.data.repos."Kathrynhiggs21/kova-ai-docengine"'
```

If `exists: false`, you need to create it on GitHub.

## Working with Claude Code

### Question: Can Claude Code work on multiple repos at once?

**Answer**: Not directly, but yes through the multi-repo system.

**How to work across repos:**

1. **Use Kova-ai-SYSTEM as your hub** - Run Claude Code here
2. **Use the API endpoints** - Control all repos from one place
3. **Use the sync service** - Automatically coordinate updates
4. **Use Claude Bridge** - AI analyzes all repos together

### Example: Updating All Repos

```python
# In Kova-ai-SYSTEM, create a script:
import httpx
import asyncio

async def update_all_repos():
    async with httpx.AsyncClient() as client:
        # Get all repos
        response = await client.get("http://localhost:8000/multi-repo/list")
        repos = response.json()["data"]["repositories"]

        # Sync all
        sync_response = await client.post(
            "http://localhost:8000/multi-repo/sync",
            json={"include_claude": True}
        )

        print(sync_response.json())

asyncio.run(update_all_repos())
```

## Automatic Discovery

The system can **automatically discover** new Kova AI repos:

**Settings in config:**
```json
{
  "discovery_settings": {
    "auto_discover_new_repos": true,
    "repo_name_pattern": "kova-ai-*",
    "watch_for_new_repos": true
  }
}
```

**Manual trigger:**
```bash
curl http://localhost:8000/multi-repo/discover
```

## Future Repos

### Planning Future Repos

You can add planned repos to the config **before creating them**:

```json
{
  "repositories": [
    {
      "name": "kova-ai-analytics",
      "full_name": "Kathrynhiggs21/kova-ai-analytics",
      "description": "Analytics and reporting service",
      "type": "service",
      "enabled": true,
      "sync_priority": 3,
      "features": ["analytics", "reporting", "dashboards"]
    }
  ]
}
```

When you run `/multi-repo/status`, it will show:
```json
{
  "Kathrynhiggs21/kova-ai-analytics": {
    "exists": false,
    "status": "not_found_or_planned"
  }
}
```

This helps you **track what needs to be created**.

## Integration with Claude AI

### Automatic Claude Sync

Every sync can include Claude AI analysis:

```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}'
```

Claude will:
- Analyze each repo's structure
- Identify patterns across repos
- Suggest improvements
- Coordinate cross-repo features

### Continuous Sync (kovai-ai service)

The async Claude Bridge Service runs continuously:

```bash
cd kovai-ai/app/services
python claude_bridge_service.py
```

This will:
- Sync every 5 minutes
- Auto-reload repo list from config
- Handle new repos automatically

## Testing the System

### Automated Testing

The system includes comprehensive testing and validation tools:

#### 1. Validate Configuration

Before starting, validate your configuration:

```bash
python3 scripts/validate_config.py
```

This checks:
- ✅ JSON syntax validity
- ✅ Required fields present
- ✅ Repository format correctness
- ✅ No duplicate entries
- ✅ Settings validity

#### 2. Run Full Test Suite

Test all endpoints and functionality:

```bash
python3 scripts/test_multi_repo.py
```

This tests:
- ✅ Configuration files
- ✅ API health
- ✅ All multi-repo endpoints
- ✅ Repository listing and status
- ✅ Discovery functionality
- ✅ Sync operations

**Example Output:**
```
=== Kova AI Multi-Repository System Tests ===

Configuration Tests:
  ✓ PASS - Validate Config File
  ✓ PASS - Validate .env.example

API Endpoint Tests:
  ✓ PASS - Health Check
  ✓ PASS - List Repositories (Found 6 repositories)
  ✓ PASS - Get Config (GitHub owner: Kathrynhiggs21)
  ✓ PASS - Get Repo Status (Checked 6 repositories)
  ✓ PASS - Discover Repos (Found 0 new repositories)
  ✓ PASS - Sync Repositories (Synced 6 repositories)

=== Test Summary ===
Total Tests: 8
Passed: 8
Failed: 0
Pass Rate: 100.0%

✓ All tests passed!
```

### Manual Testing

#### 1. Start the API
```bash
cd kova-ai
docker-compose up -d
```

#### 2. Test Multi-Repo Status
```bash
curl http://localhost:8000/multi-repo/status | jq
```

#### 3. Discover Repos
```bash
curl http://localhost:8000/multi-repo/discover | jq
```

#### 4. Sync All
```bash
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}' | jq
```

## Configuration Reference

### Repository Types

- **core**: Essential system components
- **service**: Microservices and APIs
- **frontend**: User interfaces
- **experimental**: Prototypes and research

### Sync Priority

- **1**: Highest priority (sync first)
- **2**: High priority
- **3**: Normal priority
- **4**: Low priority
- **5**: Lowest priority (sync last)

### Features Tags

Tag repos with features for organization:
- `ai-integration`
- `database`
- `api`
- `frontend`
- `monitoring`
- `documentation`

## Troubleshooting

### Repo Not Found

If a repo shows `exists: false`:
1. Create it on GitHub
2. Run discovery: `curl http://localhost:8000/multi-repo/discover`
3. Verify: `curl http://localhost:8000/multi-repo/status`

### API Key Issues

Ensure your `.env` has:
```bash
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### Config Not Loading

Check config path in service:
```bash
cat kova_repos_config.json
```

## Best Practices

1. **Keep config updated** - Add new repos immediately
2. **Use sync priority** - Critical repos sync first
3. **Enable auto-discovery** - Catch new repos automatically
4. **Regular syncs** - Run every 30 minutes
5. **Tag features** - Organize repos by functionality
6. **Test before prod** - Use `/status` before `/sync`

## Recent Improvements

The multi-repo system has been enhanced with several production-ready features:

### 🔧 **Retry Logic & Rate Limiting**
- Automatic retry with exponential backoff for GitHub API calls
- Handles rate limits gracefully (403 errors)
- Network error recovery with up to 4 retry attempts
- Base delay: 2 seconds, exponential increase (2s, 4s, 8s, 16s)

### ✅ **Comprehensive Testing**
- **Test Script** (`scripts/test_multi_repo.py`): Full API endpoint testing
- **Config Validator** (`scripts/validate_config.py`): JSON schema validation
- Automated checks for configuration integrity
- Color-coded output for easy debugging

### 🔐 **Correct Authentication**
- Fixed Claude API headers (now using `x-api-key` instead of `Authorization`)
- Updated to correct Anthropic endpoint: `/v1/messages`
- Environment variable documentation in `.env.example`
- Token scope requirements clearly documented

### 📝 **Enhanced Documentation**
- **SETUP_GUIDE.md**: Step-by-step setup instructions
- Troubleshooting section with common issues
- API usage examples with expected outputs
- Testing procedures and validation steps

### 🛠️ **Utilities**
- Configuration validation tool
- Automated test suite
- Better error messages and logging
- Comprehensive type hints

## Tools Reference

### Configuration Validation

```bash
# Validate your config before deploying
python3 scripts/validate_config.py
```

**What it checks:**
- JSON syntax and structure
- Required fields presence
- Repository format validation
- Duplicate detection
- Setting type validation

### Testing Suite

```bash
# Run all tests
python3 scripts/test_multi_repo.py
```

**What it tests:**
- Configuration file validity
- Environment setup
- API health
- All multi-repo endpoints
- Repository operations
- Sync functionality

### Quick Health Check

```bash
# Quick check if everything is working
curl http://localhost:8000/health && \
curl http://localhost:8000/multi-repo/status | jq '.data.total_repos'
```

## Summary

✅ **Claude Code limitation**: Works on one repo at a time
✅ **Solution**: Multi-repo management system
✅ **Benefits**: Coordinate all repos from one place
✅ **Auto-discovery**: Finds new repos automatically
✅ **Claude integration**: AI analyzes all repos together
✅ **Future-ready**: Add planned repos to config
✅ **Production-ready**: Retry logic, testing, validation
✅ **Well-documented**: Setup guides, troubleshooting, examples

You now have a complete, production-ready multi-repository management system for all your Kova AI projects!

## Quick Reference

**Setup:**
```bash
# 1. Configure
cp kova-ai/.env.example kova-ai/.env
# Edit .env with your tokens

# 2. Validate
python3 scripts/validate_config.py

# 3. Start
cd kova-ai && docker-compose up -d

# 4. Test
python3 scripts/test_multi_repo.py
```

**Daily Use:**
```bash
# Check status
curl http://localhost:8000/multi-repo/status | jq

# Discover new repos
curl http://localhost:8000/multi-repo/discover | jq

# Sync all repos
curl -X POST http://localhost:8000/multi-repo/sync \
  -H "Content-Type: application/json" \
  -d '{"include_claude": true}' | jq
```

**Troubleshooting:**
```bash
# Validate config
python3 scripts/validate_config.py

# Test system
python3 scripts/test_multi_repo.py

# View logs
cd kova-ai && docker-compose logs -f api

# Restart services
docker-compose restart
```

For detailed setup instructions, see **SETUP_GUIDE.md** 📖
