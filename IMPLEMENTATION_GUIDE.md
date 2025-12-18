# Kova OS - Complete Implementation Guide

## 🎯 Overview

This guide walks you through implementing Kova OS - the intelligent operating system layer for your Kova AI development infrastructure.

---

## 📋 What's Been Created

### 1. Google Drive Integration System
**File:** `kova-ai/app/services/google_drive_integration.py`

**Features:**
- Search Google Drive for Kova files
- Categorize files (core, docs, code, config, etc.)
- Detect duplicates by name, size, and content
- Identify obsolete files
- Generate folder structure
- Create file manifests
- Generate migration plans

### 2. File Organization API
**File:** `kova-ai/app/api/file_organization_endpoints.py`

**Endpoints:**
- `POST /file-org/analyze` - Analyze files from various sources
- `GET /file-org/structure` - Get recommended folder structure
- `POST /file-org/migration-plan` - Create migration plan
- `GET /file-org/duplicates` - Find duplicates
- `GET /file-org/obsolete` - Find obsolete files
- `POST /file-org/categorize` - Categorize a file
- `GET /file-org/stats` - Get organization statistics

### 3. Master Hub Setup Script
**File:** `scripts/setup_master_hub.sh`

Creates the complete Kova Master Hub folder structure:
```
KOVA_MASTER_HUB/
├── 01_CORE_SYSTEM/
├── 02_DOCUMENTATION/
├── 03_INTEGRATIONS/
├── 04_WORKFLOWS/
├── 05_DATA/
├── 06_DEVELOPMENT/
├── 07_OPERATIONS/
└── 08_ANALYTICS/
```

### 4. Kova OS Blueprint
**File:** `KOVA_OS_BLUEPRINT.md`

Complete operational blueprint including:
- Vision and purpose
- Current state analysis
- Folder structure design
- Implementation phases
- Next steps roadmap
- Success metrics

---

## 🚀 Implementation Steps

### Step 1: Set Up Google Drive API (REQUIRED)

#### 1.1 Create Google Cloud Project
```bash
# Visit: https://console.cloud.google.com/

# 1. Create new project: "Kova-AI-Drive-Integration"
# 2. Enable Google Drive API
# 3. Create OAuth 2.0 credentials
# 4. Download credentials JSON
```

#### 1.2 Configure Credentials
```bash
# Place credentials file
mv ~/Downloads/credentials.json kova-ai/credentials/google_drive_credentials.json

# Set environment variable
export GOOGLE_CREDENTIALS_PATH=./credentials/google_drive_credentials.json

# Or add to .env
echo "GOOGLE_CREDENTIALS_PATH=./credentials/google_drive_credentials.json" >> kova-ai/.env
```

#### 1.3 Install Google API Libraries
```bash
cd kova-ai
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Create Master Hub Structure

```bash
# Run the setup script
chmod +x scripts/setup_master_hub.sh
./scripts/setup_master_hub.sh

# This creates: ../KOVA_MASTER_HUB/
# Or specify custom location:
./scripts/setup_master_hub.sh /path/to/custom/location
```

### Step 3: Start Kova AI System

```bash
cd kova-ai

# Create .env if not exists
cp .env.example .env

# Edit with your API keys
nano .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### Step 4: Import and Analyze Google Drive Files

#### 4.1 Via API
```bash
# Analyze files
curl -X POST http://localhost:8000/file-org/analyze \
  -H "Content-Type: application/json" \
  -d '{"source": "google_drive"}' | jq

# Get recommended structure
curl http://localhost:8000/file-org/structure | jq

# Create migration plan
curl -X POST http://localhost:8000/file-org/migration-plan \
  -H "Content-Type: application/json" \
  -d '{"manifest_id": "latest", "dry_run": true}' | jq
```

#### 4.2 Via Python Script
```bash
cd kova-ai
python -m app.services.google_drive_integration
```

### Step 5: Review and Execute Migration

#### 5.1 Review Generated Manifest
```bash
# The manifest will contain:
# - All found files
# - Categories (core, docs, code, config, etc.)
# - Duplicates detected
# - Obsolete files identified
# - Main/authoritative files
# - Recommended actions
```

#### 5.2 Execute File Migration
```bash
# Manually move files according to migration plan
# Or create automated migration script

# Example structure:
cp -r ImportedFiles/core/* KOVA_MASTER_HUB/01_CORE_SYSTEM/
cp -r ImportedFiles/docs/* KOVA_MASTER_HUB/02_DOCUMENTATION/
# etc.
```

### Step 6: Organize Existing Kova-ai-SYSTEM Repo

```bash
# Move current repo into master hub
mv /path/to/Kova-ai-SYSTEM ../KOVA_MASTER_HUB/01_CORE_SYSTEM/repositories/

# Update working directory
cd ../KOVA_MASTER_HUB/01_CORE_SYSTEM/repositories/Kova-ai-SYSTEM
```

### Step 7: Create Missing Repositories

```bash
# Create kova-ai-docengine
gh repo create Kathrynhiggs21/kova-ai-docengine --private --description "Kova AI Document Processing Engine"

# Clone into master hub
cd ../KOVA_MASTER_HUB/01_CORE_SYSTEM/repositories/
git clone https://github.com/Kathrynhiggs21/kova-ai-docengine.git

# Add to system
curl -X POST http://localhost:8000/multi-repo/add \
  -H "Content-Type: application/json" \
  -d '{
    "repo_full_name": "Kathrynhiggs21/kova-ai-docengine",
    "repo_type": "service"
  }'
```

---

## 📊 File Organization Process

### Automatic Categorization

Files are automatically categorized based on:

1. **Core System** - Keywords: system, core, main, master
2. **Documentation** - Extensions: .md, .txt, .doc, .pdf
3. **Configuration** - Extensions: .json, .yaml, .yml, .env
4. **Code** - Extensions: .py, .js, .ts, .go, .rs
5. **Unknown** - Everything else

### Duplicate Detection

Duplicates are identified by:
- Similar filenames (normalized)
- File size
- Content hash (when available)

**Strategy:**
- Keep most recent version
- Archive older versions
- Flag for manual review if uncertain

### Obsolete File Detection

Files marked obsolete if:
- Contains keywords: old, backup, copy, temp, draft
- Version numbers indicating old versions
- Not modified in >6 months (configurable)

---

## 🎨 Folder Structure Usage

### Where to Put Files

| File Type | Destination |
|-----------|-------------|
| Repository code | `01_CORE_SYSTEM/repositories/{repo-name}/` |
| API documentation | `02_DOCUMENTATION/api/` |
| User guides | `02_DOCUMENTATION/guides/` |
| Google Drive imports | `03_INTEGRATIONS/google_drive/imported_files/` |
| Claude artifacts | `03_INTEGRATIONS/claude/artifacts/` |
| CI/CD configs | `04_WORKFLOWS/ci_cd/` |
| Deployment scripts | `04_WORKFLOWS/deployment/` |
| Database schemas | `05_DATA/databases/schemas/` |
| Active development | `06_DEVELOPMENT/active/` |
| Test files | `06_DEVELOPMENT/testing/` |
| Completed projects | `06_DEVELOPMENT/archive/completed/` |
| Runbooks | `07_OPERATIONS/runbooks/` |
| Performance metrics | `08_ANALYTICS/metrics/performance/` |

---

## 🔧 API Usage Examples

### Analyze Files
```bash
curl -X POST http://localhost:8000/file-org/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "source": "google_drive",
    "filters": {
      "keywords": ["kova", "ai", "system"]
    }
  }'
```

### Get Folder Structure
```bash
curl http://localhost:8000/file-org/structure
```

### Categorize a File
```bash
curl -X POST "http://localhost:8000/file-org/categorize?filename=kova_config.json&mime_type=application/json"
```

### Get Organization Stats
```bash
curl http://localhost:8000/file-org/stats
```

---

## 📈 Monitoring Progress

### Check Organization Status
```bash
# Via API
curl http://localhost:8000/file-org/stats | jq

# Expected output:
{
  "total_files": 150,
  "organized": 120,
  "pending": 30,
  "duplicates": 15,
  "obsolete": 10,
  "categories": {
    "core": 25,
    "documentation": 40,
    "configuration": 15,
    "code": 50,
    "unknown": 20
  }
}
```

### View Master Hub Structure
```bash
cd ../KOVA_MASTER_HUB
tree -L 3
```

---

## 🎯 Success Criteria

### Phase 2 Complete When:
- [ ] Google Drive API configured
- [ ] Master Hub structure created
- [ ] All Drive files imported and analyzed
- [ ] Files categorized (100%)
- [ ] Duplicates identified and handled
- [ ] Obsolete files archived
- [ ] All files in correct locations
- [ ] Documentation updated
- [ ] All repos in master hub

---

## 🚨 Troubleshooting

### Google Drive API Issues
```bash
# Error: Credentials not found
export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json

# Error: API not enabled
# Visit: https://console.cloud.google.com/apis/library/drive.googleapis.com
# Click "Enable API"

# Error: Permission denied
# Ensure OAuth consent screen is configured
# Add test users if in testing mode
```

### Import Errors
```bash
# Check Python dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# Verify imports
python -c "from app.services.google_drive_integration import GoogleDriveKovaIntegration; print('OK')"
```

### API Endpoint Not Found
```bash
# Restart API
docker-compose restart api

# Check logs
docker-compose logs api

# Verify endpoint
curl http://localhost:8000/docs
```

---

## 📚 Next Steps After Organization

1. **Implement Memory System** (kova-ai-mem0)
   - Context persistence
   - Learning from patterns
   - Smart suggestions

2. **Build Document Engine** (kova-ai-docengine)
   - PDF processing
   - Document generation
   - Template management

3. **Create Dashboard**
   - Web UI for file browser
   - Organization controls
   - Analytics views

4. **Advanced Automation**
   - Smart file routing
   - Auto-categorization improvements
   - Predictive organization

5. **Scale to Team**
   - Multi-user support
   - Permissions system
   - Collaboration features

---

## 🎉 Summary

You now have:
✅ Complete Google Drive integration
✅ Automated file organization system
✅ Duplicate detection
✅ Master Hub folder structure
✅ File categorization API
✅ Migration planning tools
✅ Kova OS blueprint

**Next:** Execute the implementation steps above to organize your Kova ecosystem!

---

*For questions or issues, refer to KOVA_OS_BLUEPRINT.md*
