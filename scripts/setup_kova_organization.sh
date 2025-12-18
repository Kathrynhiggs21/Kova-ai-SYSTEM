#!/bin/bash
#
# Kova Master Hub Organization Setup Script
#
# This script helps set up and run the complete file organization process
# for all Kova-related files from Google Drive.
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MASTER_HUB_DIR="$HOME/Kova-Master-Hub"
INVENTORY_DIR="$PROJECT_DIR/kova_file_inventory"

# Print banner
echo ""
echo "=========================================="
echo "   Kova Master Hub Organization Setup"
echo "=========================================="
echo ""

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log_success "Found Python $PYTHON_VERSION"

# Check for required Python packages
log_info "Checking Python dependencies..."
MISSING_PACKAGES=()

python3 -c "import google.oauth2" 2>/dev/null || MISSING_PACKAGES+=("google-auth")
python3 -c "import google_auth_oauthlib" 2>/dev/null || MISSING_PACKAGES+=("google-auth-oauthlib")
python3 -c "import googleapiclient" 2>/dev/null || MISSING_PACKAGES+=("google-api-python-client")

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    log_warning "Missing packages: ${MISSING_PACKAGES[*]}"
    log_info "Install with: pip install ${MISSING_PACKAGES[*]}"
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_PACKAGES[@]}"
        log_success "Packages installed"
    else
        log_error "Required packages not installed. Exiting."
        exit 1
    fi
else
    log_success "All required packages are installed"
fi

# Check for Google Drive credentials
log_info "Checking Google Drive credentials..."
if [ ! -f "$PROJECT_DIR/credentials.json" ]; then
    log_warning "credentials.json not found"
    log_info "Please download your OAuth 2.0 credentials from:"
    log_info "https://console.cloud.google.com/apis/credentials"
    log_info ""
    log_info "Steps:"
    log_info "1. Create a new project or select existing"
    log_info "2. Enable Google Drive API"
    log_info "3. Create OAuth 2.0 Client ID (Desktop app)"
    log_info "4. Download and save as: $PROJECT_DIR/credentials.json"
    echo ""
    read -p "Do you have the credentials file ready? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter path to credentials file: " CREDS_PATH
        if [ -f "$CREDS_PATH" ]; then
            cp "$CREDS_PATH" "$PROJECT_DIR/credentials.json"
            log_success "Credentials file copied"
        else
            log_error "File not found: $CREDS_PATH"
            exit 1
        fi
    else
        log_error "Cannot proceed without credentials. Exiting."
        exit 1
    fi
else
    log_success "Found credentials.json"
fi

# Ask user what they want to do
echo ""
echo "What would you like to do?"
echo ""
echo "1) Import and analyze files from Google Drive"
echo "2) Create Kova Master Hub folder structure"
echo "3) Organize files (dry run)"
echo "4) Organize files (execute)"
echo "5) Full setup (all of the above)"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " CHOICE

case $CHOICE in
    1)
        log_info "Starting Google Drive import and analysis..."
        cd "$PROJECT_DIR"
        python3 scripts/gdrive_import.py
        log_success "Import complete!"
        log_info "Check results in: $INVENTORY_DIR"
        ;;

    2)
        log_info "Creating Kova Master Hub folder structure..."
        if [ ! -d "$MASTER_HUB_DIR" ]; then
            mkdir -p "$MASTER_HUB_DIR"
            log_success "Created directory: $MASTER_HUB_DIR"
        fi
        python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" --dry-run
        log_success "Folder structure preview complete"
        echo ""
        read -p "Create the folder structure? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR"
            log_success "Folder structure created at: $MASTER_HUB_DIR"
        fi
        ;;

    3)
        log_info "Running organization in dry-run mode..."
        # Find latest inventory
        LATEST_INVENTORY=$(ls -t "$INVENTORY_DIR"/inventory_*.json 2>/dev/null | head -1)
        if [ -z "$LATEST_INVENTORY" ]; then
            log_error "No inventory file found. Run option 1 first."
            exit 1
        fi
        log_info "Using inventory: $LATEST_INVENTORY"
        python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" \
            --inventory "$LATEST_INVENTORY" \
            --dry-run
        log_success "Dry run complete. Review the output above."
        ;;

    4)
        log_info "Organizing files (EXECUTE mode)..."
        LATEST_INVENTORY=$(ls -t "$INVENTORY_DIR"/inventory_*.json 2>/dev/null | head -1)
        if [ -z "$LATEST_INVENTORY" ]; then
            log_error "No inventory file found. Run option 1 first."
            exit 1
        fi
        log_info "Using inventory: $LATEST_INVENTORY"
        log_warning "This will move files. Make sure you've reviewed the dry run!"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" \
                --inventory "$LATEST_INVENTORY" \
                --execute
            log_success "Organization complete!"
            log_info "Files organized in: $MASTER_HUB_DIR"
        else
            log_info "Cancelled."
        fi
        ;;

    5)
        log_info "Running full setup..."

        # Step 1: Import from Google Drive
        log_info "Step 1/4: Importing from Google Drive..."
        cd "$PROJECT_DIR"
        python3 scripts/gdrive_import.py

        # Step 2: Create folder structure
        log_info "Step 2/4: Creating folder structure..."
        if [ ! -d "$MASTER_HUB_DIR" ]; then
            mkdir -p "$MASTER_HUB_DIR"
        fi
        # Just create folders, don't show dry run
        python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" > /dev/null 2>&1

        # Step 3: Dry run organization
        log_info "Step 3/4: Running organization preview..."
        LATEST_INVENTORY=$(ls -t "$INVENTORY_DIR"/inventory_*.json 2>/dev/null | head -1)
        python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" \
            --inventory "$LATEST_INVENTORY" \
            --dry-run

        # Step 4: Ask to execute
        echo ""
        log_info "Step 4/4: Execute organization?"
        log_warning "Review the dry run output above before proceeding."
        read -p "Execute organization? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 "$PROJECT_DIR/scripts/file_organizer.py" "$MASTER_HUB_DIR" \
                --inventory "$LATEST_INVENTORY" \
                --execute
            log_success "Full setup complete!"
            log_info "Master Hub location: $MASTER_HUB_DIR"
            log_info "Inventory location: $INVENTORY_DIR"
        else
            log_info "Setup cancelled at execution step."
            log_info "You can run option 4 later to execute organization."
        fi
        ;;

    6)
        log_info "Exiting..."
        exit 0
        ;;

    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac

# Print next steps
echo ""
echo "=========================================="
echo "   Next Steps"
echo "=========================================="
echo ""
echo "• Review your files in: $MASTER_HUB_DIR"
echo "• Check purgatory folder: $MASTER_HUB_DIR/09-Purgatory"
echo "• Read the guides:"
echo "  - KOVA_FILE_ORGANIZATION.md (structure details)"
echo "  - KOVA_ORGANIZATION_GUIDE.md (usage guide)"
echo ""
echo "• Set up automated maintenance:"
echo "  - Daily: Re-run option 1 to import new files"
echo "  - Weekly: Review purgatory folder"
echo "  - Monthly: Archive old files"
echo ""
log_success "Done!"
echo ""
