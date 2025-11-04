#!/bin/bash
# Startup environment validation script for Kova AI System

echo "🔍 Checking environment configuration..."

# Required environment variables
REQUIRED_VARS=(
    "POSTGRES_DB"
    "POSTGRES_USER" 
    "POSTGRES_PASSWORD"
    "DATABASE_URL"
)

# Optional but recommended variables
OPTIONAL_VARS=(
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "GITHUB_TOKEN"
    "PINECONE_API_KEY"
)

# Check required variables
missing_required=0
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: Required environment variable $var is not set"
        missing_required=1
    else
        echo "✅ $var is configured"
    fi
done

# Check optional variables and warn if missing
for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  WARNING: Optional environment variable $var is not set (may limit functionality)"
    else
        echo "✅ $var is configured"
    fi
done

# Exit with error if required variables are missing
if [ $missing_required -eq 1 ]; then
    echo ""
    echo "❌ Environment check failed. Please check your .env file."
    echo "💡 Copy .env.example to .env and configure the required values:"
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

echo ""
echo "✅ Environment check passed! Starting application..."
echo ""