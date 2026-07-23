#!/usr/bin/env python3
"""
KOVA OS Export Tool
Packages the website and compiled images into ZIP archives and provides
integrations to download locally or upload directly to Google Drive.
"""

import os
import sys
import zipfile
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = PROJECT_ROOT / "site"
IMAGES_DIR = SITE_DIR / "images"

def log(msg, success=True):
    prefix = "✅" if success else "⚠️"
    print(f"{prefix} {msg}")

def package_zip(source_dir: Path, target_zip: Path, include_parent=False):
    """
    Zips a directory recursively using Python's standard zipfile module.
    
    Args:
        source_dir (Path): The directory to package into the ZIP.
        target_zip (Path): The destination path for the ZIP archive.
        include_parent (bool): If True, includes the parent directory name 
                               in the archive structure. If False, packages 
                               only the contents of the source_dir.
    """
    if not source_dir.exists():
        log(f"Source directory does not exist: {source_dir}", False)
        return False
        
    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                # Determine relative path in the archive
                if include_parent:
                    arc_name = file_path.relative_to(source_dir.parent)
                else:
                    arc_name = file_path.relative_to(source_dir)
                zipf.write(file_path, arc_name)
    return True

def export_kova_os():
    print("=" * 60)
    print("🚀 KOVA OS COMPILATION & EXPORT SYSTEM")
    print("=" * 60)
    
    # 1. Generate/verify SVG images exist
    if not IMAGES_DIR.exists() or not any(IMAGES_DIR.iterdir()):
        log("No image assets found. Generating SVGs...", False)
        try:
            sys.path.append(str(Path(__file__).resolve().parent))
            from generate_svg_assets import create_svg_assets
            create_svg_assets(IMAGES_DIR)
        except ImportError:
            # Fallback inline execution using subprocess
            import subprocess
            subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts/generate_svg_assets.py"), str(IMAGES_DIR)], check=True)
    
    # 2. Package site_final.zip
    site_zip = PROJECT_ROOT / "site_final.zip"
    log(f"Compiling entire site into {site_zip}...")
    if package_zip(SITE_DIR, site_zip):
        log(f"Successfully packaged site_final.zip ({site_zip.stat().st_size / 1024:.1f} KB)")
    else:
        log("Failed to package site_final.zip", False)
        
    # 3. Package images.zip (only the compiled SVGs/images)
    images_zip = PROJECT_ROOT / "images.zip"
    log(f"Compiling image assets into {images_zip} for kovoas.com...")
    if package_zip(IMAGES_DIR, images_zip):
        log(f"Successfully packaged images.zip ({images_zip.stat().st_size / 1024:.1f} KB)")
    else:
        log("Failed to package images.zip", False)
        
    # 4. Google Drive integration support
    upload_to_gdrive = os.getenv("UPLOAD_TO_GDRIVE", "false").lower() == "true"
    if upload_to_gdrive:
        log("Initiating Google Drive integration upload...")
        try:
            sys.path.append(str(Path(__file__).resolve().parent))
            from gdrive_import import GoogleDriveImporter
            # We reuse the credentials/auth from the existing importer or use credentials
            importer = GoogleDriveImporter()
            if importer.authenticate():
                # We can perform the upload of these ZIP files
                drive_service = importer.service
                
                # Check for existing folder or upload to root/canonical folders
                from googleapiclient.http import MediaFileUpload
                
                for zip_path in [site_zip, images_zip]:
                    file_metadata = {
                        'name': zip_path.name,
                        'mimeType': 'application/zip'
                    }
                    media = MediaFileUpload(str(zip_path), mimetype='application/zip', resumable=True)
                    uploaded_file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id, webViewLink'
                    ).execute()
                    log(f"Uploaded {zip_path.name} to Google Drive! File ID: {uploaded_file.get('id')}")
                    log(f"Link: {uploaded_file.get('webViewLink')}")
            else:
                log("Google Drive Authentication failed or credentials.json not present. Skip auto-upload.", False)
                log("Files are stored locally in the repository root and available for direct download via MCP / API.", False)
                sys.exit(2)
        except Exception as e:
            log(f"Google Drive upload encountered an error: {e}", False)
            log("Fallback: Files are ready for download via MCP or API.", False)
            sys.exit(2)
    else:
        log("Google Drive upload is disabled by default (use UPLOAD_TO_GDRIVE=true env var).")
        log("Files are fully compiled and ready to download locally or via MCP!")

if __name__ == "__main__":
    export_kova_os()
