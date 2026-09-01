#!/bin/bash
set -e

echo "🔍 Kova AI Platform Verification"
echo "================================"

# Check directory structure
echo "📁 Checking directory structure..."

required_files=(
    "kova-ai/docker-compose.yml"
    "kova-ai/Dockerfile"
    "kova-ai/requirements.txt"
    "kova-ai/.env.example"
    "kova-ai/app/main.py"
    "kova-ai/scripts/init.sql"
    "kova-ai/monitoring/prometheus/prometheus.yml"
    "kova-ai/monitoring/grafana/datasources/prometheus.yml"
    "kova-ai/deployment/nginx/nginx.conf"
    "kova-ai/appsheet_config.json"
    "setup_kova_system.sh"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file"
        missing_files+=("$file")
    fi
done

required_dirs=(
    "kova-ai/app/api"
    "kova-ai/app/database"
    "kova-ai/app/core"
    "kova-ai/app/security"
    "kova-ai/app/tasks"
    "kova-ai/app/utils"
    "kova-ai/app/integrations"
    "kova-ai/deployment/kubernetes"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/"
    else
        echo "   ❌ $dir/"
        missing_files+=("$dir")
    fi
done

# Check API endpoints
echo ""
echo "🌐 Checking API endpoint files..."
api_files=(
    "kova-ai/app/api/health.py"
    "kova-ai/app/api/ai_endpoints.py"
    "kova-ai/app/api/webhooks.py"
)

for file in "${api_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
        # Check if file contains router definition
        if grep -q "router = APIRouter" "$file"; then
            echo "      ✅ Contains router definition"
        else
            echo "      ⚠️  Missing router definition"
        fi
    else
        echo "   ❌ $file"
        missing_files+=("$file")
    fi
done

# Check Python syntax
echo ""
echo "🐍 Checking Python syntax..."
python_files=(
    "kova-ai/app/main.py"
    "kova-ai/app/api/health.py"
    "kova-ai/app/api/ai_endpoints.py"
    "kova-ai/app/api/webhooks.py"
    "kova-ai/app/database/session.py"
)

for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "   ✅ $file (syntax OK)"
        else
            echo "   ❌ $file (syntax error)"
            missing_files+=("$file syntax")
        fi
    fi
done

echo ""
echo "🧪 Checking configuration validator behavior..."
if python3 -m unittest discover -s tests -p "test_validate_config.py" -v; then
    echo "   ✅ Configuration validator regression tests passed"
else
    echo "   ❌ Configuration validator regression tests failed"
    missing_files+=("configuration validator tests")
fi

# Check Docker configuration
echo ""
echo "🐳 Checking Docker configuration..."
if [ -f "kova-ai/docker-compose.yml" ]; then
    if grep -q "version:" "kova-ai/docker-compose.yml"; then
        echo "   ✅ docker-compose.yml has version"
    fi
    if grep -q "services:" "kova-ai/docker-compose.yml"; then
        echo "   ✅ docker-compose.yml has services"
    fi
    if grep -q "api:" "kova-ai/docker-compose.yml"; then
        echo "   ✅ docker-compose.yml has api service"
    fi
    if grep -q "db:" "kova-ai/docker-compose.yml"; then
        echo "   ✅ docker-compose.yml has db service"
    fi
fi

# Summary
echo ""
echo "📋 Verification Summary"
echo "======================="
if [ ${#missing_files[@]} -eq 0 ]; then
    echo "🎉 All required files and structure are present!"
    echo "✅ Structural verification passed. Runtime and deployment readiness require separate checks."
    echo ""
    echo "Next steps:"
    echo "1. Run: chmod +x setup_kova_system.sh"
    echo "2. Run: ./setup_kova_system.sh"
    echo "3. Edit kova-ai/.env with your API keys"
    echo "4. Access the API at http://localhost:8000"
else
    echo "❌ Missing files or issues found:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi
