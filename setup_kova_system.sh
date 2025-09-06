#!/bin/bash
set -e

echo "🚀 Starting Kova AI System Setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys before running the system."
    echo "   Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN, PINECONE_API_KEY"
fi

# Make quickstart script executable
chmod +x scripts/quickstart.sh

echo "🔧 Building and starting Kova AI System..."
docker-compose up --build -d

echo ""
echo "✅ Kova AI System is starting up!"
echo ""
echo "📊 Services starting:"
echo "   - API Server: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - PostgreSQL Database: localhost:5432"
echo ""
echo "📝 To check logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "🎉 Setup complete!"