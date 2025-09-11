#!/bin/bash
set -e

echo "🚀 Kova AI System Setup Starting..."

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Use the appropriate Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo "✅ Docker and Docker Compose are available"

# Change to kova-ai directory
cd kova-ai

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys before running the system!"
    echo "   Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN, PINECONE_API_KEY"
fi

# Build and start services
echo "🔨 Building and starting Kova AI services..."
$DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true
$DOCKER_COMPOSE up --build -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
$DOCKER_COMPOSE ps

# Test API health
echo "🩺 Testing API health..."
max_attempts=10
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is healthy!"
        break
    else
        echo "⏳ Attempt $attempt/$max_attempts - API not ready yet..."
        sleep 5
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ API health check failed. Check logs with: $DOCKER_COMPOSE logs api"
    exit 1
fi

echo ""
echo "🎉 Kova AI System is running successfully!"
echo ""
echo "📚 Access points:"
echo "   - API Health: http://localhost:8000/health"
echo "   - API Docs (Swagger): http://localhost:8000/docs"
echo "   - API Docs (ReDoc): http://localhost:8000/redoc"
echo "   - Metrics: http://localhost:8000/metrics"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: $DOCKER_COMPOSE logs -f"
echo "   - Stop services: $DOCKER_COMPOSE down"
echo "   - Restart services: $DOCKER_COMPOSE restart"
echo ""
echo "📝 Don't forget to:"
echo "   1. Edit .env with your actual API keys"
echo "   2. Configure your AppSheet dashboard using appsheet_config.json"
echo "   3. Set up monitoring if needed (Prometheus/Grafana configs are included)"
