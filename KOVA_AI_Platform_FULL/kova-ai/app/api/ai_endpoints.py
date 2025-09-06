from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json

router = APIRouter(prefix="/ai")

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: Optional[str] = "python"
    project_context: Optional[str] = None

class CodeGenerationResponse(BaseModel):
    generated_code: str
    language: str
    filename_suggestion: Optional[str] = None
    description: Optional[str] = None

@router.post("/command")
async def ai_command(request: Request):
    data = await request.json()
    # Basic echo for now
    return {"received": data}

@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code based on natural language prompt"""
    # This is a mock implementation - in a real system this would call AI services
    
    # Simple code generation examples based on prompt
    if "hello world" in request.prompt.lower():
        if request.language == "python":
            code = 'print("Hello, World!")'
            filename = "hello_world.py"
        elif request.language == "javascript":
            code = 'console.log("Hello, World!");'
            filename = "hello_world.js"
        else:
            code = f'// Hello World in {request.language}\n// Generated code placeholder'
            filename = f"hello_world.{request.language}"
    elif "api endpoint" in request.prompt.lower():
        code = '''from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    """Example API endpoint"""
    return {"message": "This is an example endpoint"}
'''
        filename = "example_endpoint.py"
    else:
        code = f"""# Generated code for: {request.prompt}
# Language: {request.language}
# This is a placeholder implementation

def generated_function():
    \"\"\"
    Auto-generated function based on prompt: {request.prompt}
    \"\"\"
    pass  # TODO: Implement functionality
"""
        filename = "generated_code.py"
    
    return CodeGenerationResponse(
        generated_code=code,
        language=request.language,
        filename_suggestion=filename,
        description=f"Generated {request.language} code for: {request.prompt}"
    )

@router.get("/download-formats")
async def get_download_formats():
    """Get available download formats and options"""
    return {
        "formats": [
            {
                "type": "single_file",
                "description": "Download individual code files",
                "endpoint": "/download/file",
                "parameters": ["path", "filename"]
            },
            {
                "type": "directory",
                "description": "Download directory as ZIP archive",
                "endpoint": "/download/directory", 
                "parameters": ["path", "filename"]
            },
            {
                "type": "project",
                "description": "Download entire project as ZIP",
                "endpoint": "/download/project",
                "parameters": ["filename"]
            }
        ],
        "supported_file_types": [
            "python (.py)",
            "javascript (.js)",
            "typescript (.ts)",
            "json (.json)",
            "yaml (.yml, .yaml)",
            "text (.txt)",
            "markdown (.md)",
            "dockerfile",
            "configuration files"
        ]
    }
