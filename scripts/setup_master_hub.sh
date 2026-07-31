#!/bin/bash
set -e

# Kova Master Hub Setup Script
# Creates the complete folder structure for Kova OS

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          KOVA MASTER HUB - STRUCTURE SETUP                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
MASTER_HUB_PATH="${1:-../KOVA_MASTER_HUB}"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating Kova Master Hub at: $MASTER_HUB_PATH${NC}"
echo ""

# Create main directory
mkdir -p "$MASTER_HUB_PATH"
cd "$MASTER_HUB_PATH"

# Function to create directory with description
create_dir() {
    local dir_path=$1
    local description=$2

    mkdir -p "$dir_path"
    echo "$description" > "$dir_path/.description"
    echo -e "${GREEN}✓${NC} Created: $dir_path"
}

echo "📁 Creating folder structure..."
echo ""

# 01_CORE_SYSTEM
echo "Creating 01_CORE_SYSTEM..."
create_dir "01_CORE_SYSTEM" "Core system files and repositories"
create_dir "01_CORE_SYSTEM/repositories" "All Kova AI repositories"
create_dir "01_CORE_SYSTEM/repositories/Kova-ai-SYSTEM" "Main orchestration hub"
create_dir "01_CORE_SYSTEM/repositories/kova-ai" "Backend API service"
create_dir "01_CORE_SYSTEM/repositories/kova-ai-site" "Website and documentation"
create_dir "01_CORE_SYSTEM/repositories/kova-ai-mem0" "Memory and persistence system"
create_dir "01_CORE_SYSTEM/repositories/kova-ai-docengine" "Document processing engine"
create_dir "01_CORE_SYSTEM/repositories/Kova-AI-Scribbles" "Experimental features"
create_dir "01_CORE_SYSTEM/config" "System-wide configuration files"
create_dir "01_CORE_SYSTEM/secrets" "Encrypted credentials and API keys"

# 02_DOCUMENTATION
echo ""
echo "Creating 02_DOCUMENTATION..."
create_dir "02_DOCUMENTATION" "All system documentation"
create_dir "02_DOCUMENTATION/architecture" "System architecture documents"
create_dir "02_DOCUMENTATION/api" "API documentation"
create_dir "02_DOCUMENTATION/guides" "User and developer guides"
create_dir "02_DOCUMENTATION/specifications" "Technical specifications"

# 03_INTEGRATIONS
echo ""
echo "Creating 03_INTEGRATIONS..."
create_dir "03_INTEGRATIONS" "External service integrations"
create_dir "03_INTEGRATIONS/google_drive" "Google Drive integration files"
create_dir "03_INTEGRATIONS/google_drive/sync" "Drive sync configurations"
create_dir "03_INTEGRATIONS/google_drive/imported_files" "Files imported from Drive"
create_dir "03_INTEGRATIONS/google_drive/manifests" "Import manifests"
create_dir "03_INTEGRATIONS/github" "GitHub integration files"
create_dir "03_INTEGRATIONS/github/webhooks" "Webhook configurations"
create_dir "03_INTEGRATIONS/github/actions" "GitHub Actions workflows"
create_dir "03_INTEGRATIONS/github/templates" "PR and Issue templates"
create_dir "03_INTEGRATIONS/claude" "Claude AI integration files"
create_dir "03_INTEGRATIONS/claude/prompts" "Saved prompts"
create_dir "03_INTEGRATIONS/claude/artifacts" "Generated artifacts"
create_dir "03_INTEGRATIONS/claude/conversations" "Conversation history"
create_dir "03_INTEGRATIONS/external_apis" "Other API integrations"
create_dir "03_INTEGRATIONS/external_apis/openai" "OpenAI integration"
create_dir "03_INTEGRATIONS/external_apis/pinecone" "Pinecone vector DB"
create_dir "03_INTEGRATIONS/external_apis/custom" "Custom API integrations"

# 04_WORKFLOWS
echo ""
echo "Creating 04_WORKFLOWS..."
create_dir "04_WORKFLOWS" "Automation and workflow files"
create_dir "04_WORKFLOWS/automation" "Automated workflow scripts"
create_dir "04_WORKFLOWS/ci_cd" "CI/CD pipeline configurations"
create_dir "04_WORKFLOWS/deployment" "Deployment scripts and configs"
create_dir "04_WORKFLOWS/monitoring" "Monitoring and alerting configs"

# 05_DATA
echo ""
echo "Creating 05_DATA..."
create_dir "05_DATA" "Data storage and management"
create_dir "05_DATA/databases" "Database files"
create_dir "05_DATA/databases/schemas" "Database schemas"
create_dir "05_DATA/databases/migrations" "Database migrations"
create_dir "05_DATA/databases/backups" "Database backups"
create_dir "05_DATA/storage" "File storage"
create_dir "05_DATA/storage/files" "General files"
create_dir "05_DATA/storage/media" "Media files"
create_dir "05_DATA/storage/exports" "Exported data"
create_dir "05_DATA/cache" "Cached data"
create_dir "05_DATA/logs" "System logs"
create_dir "05_DATA/logs/application" "Application logs"
create_dir "05_DATA/logs/errors" "Error logs"
create_dir "05_DATA/logs/audit" "Audit logs"

# 06_DEVELOPMENT
echo ""
echo "Creating 06_DEVELOPMENT..."
create_dir "06_DEVELOPMENT" "Development workspace"
create_dir "06_DEVELOPMENT/active" "Current development work"
create_dir "06_DEVELOPMENT/active/features" "Feature development"
create_dir "06_DEVELOPMENT/active/bugfixes" "Bug fixes"
create_dir "06_DEVELOPMENT/active/experiments" "Experimental code"
create_dir "06_DEVELOPMENT/testing" "Testing files"
create_dir "06_DEVELOPMENT/testing/unit_tests" "Unit tests"
create_dir "06_DEVELOPMENT/testing/integration_tests" "Integration tests"
create_dir "06_DEVELOPMENT/testing/test_data" "Test data"
create_dir "06_DEVELOPMENT/prototypes" "Prototypes and POCs"
create_dir "06_DEVELOPMENT/prototypes/poc" "Proof of concepts"
create_dir "06_DEVELOPMENT/prototypes/demos" "Demo code"
create_dir "06_DEVELOPMENT/archive" "Archived development files"
create_dir "06_DEVELOPMENT/archive/completed" "Completed work"
create_dir "06_DEVELOPMENT/archive/deprecated" "Deprecated code"

# 07_OPERATIONS
echo ""
echo "Creating 07_OPERATIONS..."
create_dir "07_OPERATIONS" "Operational procedures and docs"
create_dir "07_OPERATIONS/runbooks" "Operational runbooks"
create_dir "07_OPERATIONS/incidents" "Incident reports"
create_dir "07_OPERATIONS/incidents/reports" "Incident reports"
create_dir "07_OPERATIONS/incidents/postmortems" "Post-mortem analyses"
create_dir "07_OPERATIONS/maintenance" "Maintenance procedures"
create_dir "07_OPERATIONS/maintenance/schedules" "Maintenance schedules"
create_dir "07_OPERATIONS/maintenance/procedures" "Maintenance procedures"
create_dir "07_OPERATIONS/backups" "Backup files and procedures"
create_dir "07_OPERATIONS/backups/automated" "Automated backups"
create_dir "07_OPERATIONS/backups/manual" "Manual backups"

# 08_ANALYTICS
echo ""
echo "Creating 08_ANALYTICS..."
create_dir "08_ANALYTICS" "Analytics and reporting"
create_dir "08_ANALYTICS/metrics" "Performance metrics"
create_dir "08_ANALYTICS/metrics/performance" "Performance metrics"
create_dir "08_ANALYTICS/metrics/usage" "Usage metrics"
create_dir "08_ANALYTICS/metrics/errors" "Error metrics"
create_dir "08_ANALYTICS/reports" "Analytics reports"
create_dir "08_ANALYTICS/reports/daily" "Daily reports"
create_dir "08_ANALYTICS/reports/weekly" "Weekly reports"
create_dir "08_ANALYTICS/reports/monthly" "Monthly reports"
create_dir "08_ANALYTICS/dashboards" "Dashboard configurations"
create_dir "08_ANALYTICS/dashboards/grafana" "Grafana dashboards"
create_dir "08_ANALYTICS/dashboards/custom" "Custom dashboards"

# Create README in master hub
echo ""
echo "Creating documentation..."
cat > README.md << 'EOL'
# KOVA MASTER HUB

This is the central organization structure for the entire Kova AI ecosystem.

## Structure

- **01_CORE_SYSTEM** - Core system files and all repositories
- **02_DOCUMENTATION** - All documentation
- **03_INTEGRATIONS** - External service integrations
- **04_WORKFLOWS** - Automation and CI/CD
- **05_DATA** - Data storage and management
- **06_DEVELOPMENT** - Development workspace
- **07_OPERATIONS** - Operational procedures
- **08_ANALYTICS** - Analytics and reporting

## Usage

Each folder contains a `.description` file explaining its purpose.

Navigate to the appropriate folder for your task.

## Organization Principles

1. **Core First** - Essential system files in 01_CORE_SYSTEM
2. **Documentation** - All docs in 02_DOCUMENTATION
3. **Integrations** - External services in 03_INTEGRATIONS
4. **Active Development** - Work in 06_DEVELOPMENT/active
5. **Archive Old Work** - Completed work to archive folders

## Getting Started

See `02_DOCUMENTATION/guides/` for detailed guides.

---

Last Updated: $(date +%Y-%m-%d)
EOL

# Create index file
cat > INDEX.md << 'EOL'
# KOVA MASTER HUB - DIRECTORY INDEX

## Quick Links

### Repositories
- [Kova-ai-SYSTEM](01_CORE_SYSTEM/repositories/Kova-ai-SYSTEM/) - Main hub
- [kova-ai](01_CORE_SYSTEM/repositories/kova-ai/) - Backend API
- [kova-ai-site](01_CORE_SYSTEM/repositories/kova-ai-site/) - Website
- [kova-ai-mem0](01_CORE_SYSTEM/repositories/kova-ai-mem0/) - Memory system
- [kova-ai-docengine](01_CORE_SYSTEM/repositories/kova-ai-docengine/) - Document engine

### Documentation
- [Architecture](02_DOCUMENTATION/architecture/)
- [API Docs](02_DOCUMENTATION/api/)
- [User Guides](02_DOCUMENTATION/guides/)

### Integrations
- [Google Drive](03_INTEGRATIONS/google_drive/)
- [GitHub](03_INTEGRATIONS/github/)
- [Claude AI](03_INTEGRATIONS/claude/)

### Development
- [Active Work](06_DEVELOPMENT/active/)
- [Testing](06_DEVELOPMENT/testing/)
- [Prototypes](06_DEVELOPMENT/prototypes/)

---

*Generated: $(date)*
EOL

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Kova Master Hub structure created successfully!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Location: $MASTER_HUB_PATH"
echo ""
echo "Next steps:"
echo "1. Move existing Kova-ai-SYSTEM repo to 01_CORE_SYSTEM/repositories/"
echo "2. Import files from Google Drive to 03_INTEGRATIONS/google_drive/imported_files/"
echo "3. Organize files according to categories"
echo "4. Review and update INDEX.md"
echo ""
echo "Use 'tree' command to view structure:"
echo "  tree -L 2 $MASTER_HUB_PATH"
echo ""
