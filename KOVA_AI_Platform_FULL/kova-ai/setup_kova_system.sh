#!/bin/bash
set -e

echo "🚀 Setting up KOVA AI System..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from the kova-ai directory."
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys before continuing!"
    echo "   Required: OPENAI_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN, PINECONE_API_KEY"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

echo "🏗️  Building Docker containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check function
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service_name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start properly"
    return 1
}

# Check services
check_service "API" "http://localhost:8000/health"
check_service "Database" "http://localhost:8000/health"

echo ""
echo "🎉 KOVA AI System is ready!"
echo ""
echo "📚 Available endpoints:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check:      http://localhost:8000/health"
echo "   • Metrics:           http://localhost:8000/metrics"
echo "   • AI Commands:       POST http://localhost:8000/ai/command"
echo "   • Repository Scan:   POST http://localhost:8000/api/scan"
echo ""
echo "🔗 Test the system:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📊 View logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Stop the system:"
echo "   docker compose down"
echo ""