#!/bin/bash
set -e

# Kova AI Multi-Repository Deployment Script
# Deploys changes across all Kova AI repositories

echo "🚀 Kova AI Multi-Repo Deployment"
echo "=================================="

# Configuration
GITHUB_OWNER="Kathrynhiggs21"
REPOS=(
    "Kova-ai-SYSTEM"
    "kova-ai"
    "kova-ai-site"
    "kova-ai-mem0"
    "kova-ai-docengine"
    "Kova-AI-Scribbles"
)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."

    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ git is not installed${NC}"
        exit 1
    fi

    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI (gh) not found. Some features will be limited.${NC}"
    fi

    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set. API calls may be rate-limited.${NC}"
    fi

    echo -e "${GREEN}✅ Prerequisites check complete${NC}"
}

# Clone or update repository
clone_or_update_repo() {
    local repo=$1
    local repo_path="../$repo"

    echo ""
    echo "📦 Processing $repo..."

    if [ -d "$repo_path" ]; then
        echo "  Repository exists, pulling latest changes..."
        cd "$repo_path"
        git fetch origin
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "  Using current branch"
        cd - > /dev/null
    else
        echo "  Cloning repository..."
        cd ..
        git clone "https://github.com/$GITHUB_OWNER/$repo.git" || echo "  Clone failed, may not exist yet"
        cd - > /dev/null
    fi
}

# Deploy common configs
deploy_common_configs() {
    local repo=$1
    local repo_path="../$repo"

    if [ ! -d "$repo_path" ]; then
        echo "  Skipping (repository not found)"
        return
    fi

    echo "  Deploying common configurations..."

    # Copy env template if it doesn't exist
    if [ ! -f "$repo_path/.env" ]; then
        cp deployment_templates/common/env.template "$repo_path/.env.example" 2>/dev/null || true
    fi

    # Copy GitHub workflows if applicable
    if [ -d "$repo_path/.github" ]; then
        mkdir -p "$repo_path/.github/workflows"
        # Could copy workflow templates here
    fi

    echo -e "${GREEN}  ✅ Configs deployed${NC}"
}

# Get repo status
get_repo_status() {
    local repo=$1
    local repo_path="../$repo"

    if [ -d "$repo_path" ]; then
        cd "$repo_path"
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        local commit=$(git rev-parse --short HEAD 2>/dev/null)
        local status=$(git status --porcelain 2>/dev/null | wc -l)

        echo "  Branch: $branch | Commit: $commit | Modified files: $status"
        cd - > /dev/null
    else
        echo "  Status: Not cloned"
    fi
}

# Main deployment function
deploy_all() {
    echo ""
    echo "🔄 Deploying to all repositories..."
    echo ""

    for repo in "${REPOS[@]}"; do
        clone_or_update_repo "$repo"
        deploy_common_configs "$repo"
        get_repo_status "$repo"
    done
}

# Sync configuration
sync_configs() {
    echo ""
    echo "⚙️  Syncing configurations across repos..."

    for repo in "${REPOS[@]}"; do
        local repo_path="../$repo"
        if [ -d "$repo_path" ]; then
            echo "  Syncing $repo..."

            # Copy multi-repo config
            cp kova_repos_config.json "$repo_path/" 2>/dev/null || true

            # Copy deployment templates if repo-specific template exists
            if [ -d "deployment_templates/$repo" ]; then
                cp -r "deployment_templates/$repo/"* "$repo_path/" 2>/dev/null || true
            fi
        fi
    done

    echo -e "${GREEN}✅ Configuration sync complete${NC}"
}

# Create missing repos
create_missing_repos() {
    echo ""
    echo "🆕 Checking for missing repositories..."

    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI required to create repositories${NC}"
        return
    fi

    for repo in "${REPOS[@]}"; do
        local repo_path="../$repo"
        if [ ! -d "$repo_path" ]; then
            echo "  $repo not found. Create it? (y/n)"
            read -r response
            if [ "$response" = "y" ]; then
                gh repo create "$GITHUB_OWNER/$repo" --private --description "Kova AI - $repo"
                clone_or_update_repo "$repo"
            fi
        fi
    done
}

# Show status of all repos
show_status() {
    echo ""
    echo "📊 Status of all repositories:"
    echo "=============================="

    for repo in "${REPOS[@]}"; do
        echo ""
        echo "📁 $repo"
        get_repo_status "$repo"
    done
}

# Display menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) Deploy to all repos"
    echo "2) Sync configurations"
    echo "3) Show status of all repos"
    echo "4) Clone/update all repos"
    echo "5) Create missing repos"
    echo "6) Exit"
    echo ""
    read -p "Enter choice [1-6]: " choice

    case $choice in
        1) deploy_all ;;
        2) sync_configs ;;
        3) show_status ;;
        4)
            for repo in "${REPOS[@]}"; do
                clone_or_update_repo "$repo"
            done
            ;;
        5) create_missing_repos ;;
        6) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
}

# Main execution
main() {
    check_prerequisites

    # If arguments provided, run non-interactively
    if [ $# -gt 0 ]; then
        case $1 in
            deploy) deploy_all ;;
            sync) sync_configs ;;
            status) show_status ;;
            *) echo "Unknown command: $1" ;;
        esac
    else
        # Interactive mode
        while true; do
            show_menu
            echo ""
            read -p "Continue? (y/n): " continue
            if [ "$continue" != "y" ]; then
                break
            fi
        done
    fi

    echo ""
    echo -e "${GREEN}✅ Multi-repo deployment complete!${NC}"
}

main "$@"
