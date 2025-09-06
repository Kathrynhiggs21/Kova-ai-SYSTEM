# KOVA AI Platform

This is the main backend for the KOVA AI system. See `docker-compose.yml` for local dev setup. API runs on FastAPI at port 8000.

## New Download Code Functionality

The platform now includes comprehensive code download capabilities through the `/download` endpoints:

### Available Endpoints

- **`GET /download/list`** - List available files and directories
- **`GET /download/file`** - Download individual files
- **`GET /download/directory`** - Download directories as ZIP archives
- **`GET /download/project`** - Download the entire project as ZIP
- **`GET /ai/download-formats`** - Get available download formats
- **`POST /ai/generate-code`** - Generate code and get download suggestions

### Usage Examples

```bash
# List files in root directory
curl "http://localhost:8000/download/list"

# Download a specific file
curl "http://localhost:8000/download/file?path=requirements.txt" -o requirements.txt

# Download directory as ZIP
curl "http://localhost:8000/download/directory?path=app/api" -o api.zip

# Download entire project
curl "http://localhost:8000/download/project?filename=kova-ai-project.zip" -o project.zip

# Generate code with AI
curl -X POST "http://localhost:8000/ai/generate-code" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "create a hello world program", "language": "python"}'
```

### Security Features

- Path validation to prevent directory traversal attacks
- Base directory restrictions
- File type filtering for project downloads
- Proper MIME type detection
