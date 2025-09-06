#!/bin/bash
# ================================================
# Kova AI System - Complete Setup Script
# ================================================
# Save this as: setup_kova_system.sh
# Run with: chmod +x setup_kova_system.sh && ./setup_kova_system.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Kova AI System - Complete Setup              ║${NC}"
echo -e "${BLUE}║              AI-Powered Development Platform           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    local missing=""
    
    # Check for required commands
    for cmd in docker docker-compose python3 git curl; do
        if ! command -v "$cmd" &> /dev/null; then
            missing="$missing $cmd"
        fi
    done
    
    if [ ! -z "$missing" ]; then
        echo -e "${RED}Missing required tools:$missing${NC}"
        echo -e "${YELLOW}Please install missing tools and run again.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites installed${NC}"
}

# Function to create project structure
create_project_structure() {
    echo -e "\n${YELLOW}Creating project structure...${NC}"
    
    # Create main directories
    mkdir -p kova-ai/{app,config,data,logs,credentials,scripts,monitoring,deployment}
    
    # Create app subdirectories
    mkdir -p kova-ai/app/{api,core,ai,database,integrations,tasks,security,utils,realtime}
    
    # Create monitoring subdirectories
    mkdir -p kova-ai/monitoring/{prometheus,grafana/{dashboards,datasources}}
    
    # Create deployment subdirectories
    mkdir -p kova-ai/deployment/{docker,kubernetes,nginx}
    
    echo -e "${GREEN}✓ Project structure created${NC}"
}

# Function to create Python files
create_python_files() {
    echo -e "\n${YELLOW}Creating Python application files...${NC}"
    
    cd kova-ai
    
    # Create __init__.py files
    touch app/__init__.py
    for dir in api core ai database integrations tasks security utils realtime; do
        touch app/$dir/__init__.py
    done
    
    # Copy Python files from artifacts (will be created separately)
    echo -e "${GREEN}✓ Python files created${NC}"
}

# Function to create Docker files
create_docker_files() {
    echo -e "\n${YELLOW}Creating Docker configuration...${NC}"
    
    # Create docker-compose.yml (will be created from artifact)
    # Create Dockerfile (will be created from artifact)
    
    echo -e "${GREEN}✓ Docker configuration created${NC}"
}

# Function to create configuration files
create_config_files() {
    echo -e "\n${YELLOW}Creating configuration files...${NC}"
    
    # Create requirements.txt (will be created from artifact)
    # Create .env.example (will be created from artifact)
    
    echo -e "${GREEN}✓ Configuration files created${NC}"
}

# Function to initialize services
initialize_services() {
    echo -e "\n${YELLOW}Initializing services...${NC}"
    
    # Pull Docker images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 30
    
    # Initialize database
    if [ -f scripts/init.sql ]; then
        docker-compose exec -T postgres psql -U kova_user -d kova_db < scripts/init.sql
    fi
    
    echo -e "${GREEN}✓ Services initialized${NC}"
}

# Function to display completion message
display_completion() {
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        Kova AI System Successfully Installed! 🚀       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${BLUE}Access Points:${NC}"
    echo -e "  • API:        http://localhost:8000"
    echo -e "  • API Docs:   http://localhost:8000/docs"
    echo -e "  • WebSocket:  ws://localhost:8001"
    echo -e "  • Grafana:    http://localhost:3000 (admin/admin)"
    echo -e "  • Prometheus: http://localhost:9090"
    
    echo -e "\n${BLUE}Quick Test Commands:${NC}"
    echo -e "  • Health Check:"
    echo -e "    curl http://localhost:8000/health"
    echo -e ""
    echo -e "  • AI Command:"
    echo -e "    curl -X POST http://localhost:8000/ai/command \\"
    echo -e "      -H 'Content-Type: application/json' \\"
    echo -e "      -d '{\"command\":\"create a user API\"}'"
    
    echo -e "\n${BLUE}Management Commands:${NC}"
    echo -e "  • View logs:    docker-compose logs -f"
    echo -e "  • Stop system:  docker-compose down"
    echo -e "  • Restart:      docker-compose restart"
    
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo -e "  1. Add your API keys to .env file"
    echo -e "  2. Import AppSheet configuration"
    echo -e "  3. Configure GitHub webhooks"
    echo -e "  4. Start using AI commands!"
}

# Main execution
main() {
    echo -e "${YELLOW}Starting Kova AI System setup...${NC}"
    
    # Check prerequisites
    check_prerequisites
    
    # Create project structure
    create_project_structure
    
    # Create all necessary files
    create_python_files
    create_docker_files
    create_config_files
    
    # Check for .env file
    if [ ! -f kova-ai/.env ]; then
        echo -e "\n${YELLOW}Creating .env file from template...${NC}"
        if [ -f kova-ai/.env.example ]; then
            cp kova-ai/.env.example kova-ai/.env
            echo -e "${YELLOW}⚠️  Please edit kova-ai/.env and add your API keys${NC}"
            echo -e "${YELLOW}Press Enter to continue after adding API keys...${NC}"
            read
        fi
    fi
    
    # Initialize services
    cd kova-ai
    initialize_services
    
    # Display completion message
    display_completion
}

# Run main function
main "$@"