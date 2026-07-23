"""
Export & Packaging API Endpoints for KOVA OS
Provides routes to download final site ZIPs, image archives, or trigger Google Drive uploads.
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Ensure parent directory is in python path
sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/api/export", tags=["export"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SITE_ZIP = PROJECT_ROOT / "site_final.zip"
IMAGES_ZIP = PROJECT_ROOT / "images.zip"

class GDriveUploadResponse(BaseModel):
    success: bool
    message: str
    site_zip_size_kb: float
    images_zip_size_kb: float
    logs: Optional[str] = None

class ExportStatusResponse(BaseModel):
    site_compiled: bool
    site_size_kb: float
    site_last_modified: Optional[str] = None
    images_compiled: bool
    images_size_kb: float
    images_last_modified: Optional[str] = None

@router.get("/status", response_model=ExportStatusResponse)
async def get_export_status():
    """Returns the compilation status and details of the packaged archives."""
    site_compiled = SITE_ZIP.exists()
    images_compiled = IMAGES_ZIP.exists()
    
    site_size = SITE_ZIP.stat().st_size / 1024 if site_compiled else 0.0
    images_size = IMAGES_ZIP.stat().st_size / 1024 if images_compiled else 0.0
    
    import datetime
    site_mtime = datetime.datetime.fromtimestamp(SITE_ZIP.stat().st_mtime).isoformat() if site_compiled else None
    images_mtime = datetime.datetime.fromtimestamp(IMAGES_ZIP.stat().st_mtime).isoformat() if images_compiled else None
    
    return ExportStatusResponse(
        site_compiled=site_compiled,
        site_size_kb=round(site_size, 2),
        site_last_modified=site_mtime,
        images_compiled=images_compiled,
        images_size_kb=round(images_size, 2),
        images_last_modified=images_mtime
    )

@router.get("/site")
async def download_site_zip():
    """Downloads the compiled website archive (site_final.zip)."""
    if not SITE_ZIP.exists():
        # Trigger compilation dynamically
        try:
            subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts/export_kova_os.py")], check=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Site compilation failed: {e}")
            
    if not SITE_ZIP.exists():
        raise HTTPException(status_code=404, detail="site_final.zip not found on system.")
        
    return FileResponse(
        path=SITE_ZIP,
        filename="site_final.zip",
        media_type="application/zip"
    )

@router.get("/images")
async def download_images_zip():
    """Downloads the compiled images archive for kovoas.com (images.zip)."""
    if not IMAGES_ZIP.exists():
        # Trigger compilation dynamically
        try:
            subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts/export_kova_os.py")], check=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Images compilation failed: {e}")
            
    if not IMAGES_ZIP.exists():
        raise HTTPException(status_code=404, detail="images.zip not found on system.")
        
    return FileResponse(
        path=IMAGES_ZIP,
        filename="images.zip",
        media_type="application/zip"
    )

@router.post("/gdrive-upload", response_model=GDriveUploadResponse)
async def upload_exports_to_gdrive():
    """
    Triggers local compilation and initiates Google Drive upload.
    Requires Google OAuth credentials.json to be set up.
    """
    env = os.environ.copy()
    env["UPLOAD_TO_GDRIVE"] = "true"
    
    try:
        # Run export script with UPLOAD_TO_GDRIVE enabled
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts/export_kova_os.py")],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        site_size = SITE_ZIP.stat().st_size / 1024 if SITE_ZIP.exists() else 0.0
        images_size = IMAGES_ZIP.stat().st_size / 1024 if IMAGES_ZIP.exists() else 0.0
        
        # Combine stdout and stderr for comprehensive log checking
        combined_output = result.stdout + result.stderr
        
        # Check for known failure markers or absence of success confirmation
        has_upload_success = "Uploaded" in combined_output or "Successfully uploaded" in combined_output
        
        # Use regex to check for error markers at line start to avoid false positives
        error_pattern = re.compile(r'^(Error:|ERROR:)', re.MULTILINE)
        has_failure_marker = (
            "Authentication failed" in combined_output or 
            "credentials.json not found" in combined_output or
            "Upload failed" in combined_output or
            error_pattern.search(combined_output) is not None
        )
        
        if has_failure_marker or not has_upload_success:
            return GDriveUploadResponse(
                success=False,
                message="Compilation succeeded, but Google Drive upload failed or was not confirmed.",
                site_zip_size_kb=round(site_size, 2),
                images_zip_size_kb=round(images_size, 2),
                logs=combined_output
            )
            
        return GDriveUploadResponse(
            success=True,
            message="Successfully compiled and uploaded KOVA OS exports to Google Drive!",
            site_zip_size_kb=round(site_size, 2),
            images_zip_size_kb=round(images_size, 2),
            logs=combined_output
        )
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export script execution failed with error code {e.returncode}. Logs: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
