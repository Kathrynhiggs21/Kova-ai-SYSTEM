from fastapi import APIRouter, UploadFile, File, HTTPException
import zipfile
import os
import shutil
import subprocess

router = APIRouter()

UPLOAD_DIR = "/tmp/uploaded_zip"
EXTRACT_DIR = "/tmp/extracted_zip"

@router.post("/unzip-to-git")
async def unzip_to_git(zip_file: UploadFile = File(...)):
    # Clean temp dirs
    for d in (UPLOAD_DIR, EXTRACT_DIR):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # Save uploaded ZIP
    zip_path = os.path.join(UPLOAD_DIR, zip_file.filename)
    with open(zip_path, "wb") as outfile:
        outfile.write(await zip_file.read())

    # Extract ZIP
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file.")

    # Detect repo root (assumes this file is in app/api/)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    # Copy extracted files into repo, overwriting existing ones
    def copytree_overwrite(src, dst):
        for item in os.listdir(src):
            s_item = os.path.join(src, item)
            d_item = os.path.join(dst, item)
            if os.path.isdir(s_item):
                if os.path.exists(d_item):
                    shutil.rmtree(d_item)
                shutil.copytree(s_item, d_item)
            else:
                shutil.copy2(s_item, d_item)

    copytree_overwrite(EXTRACT_DIR, repo_root)

    # Stage and commit all changes
    subprocess.run(["git", "add", "."], cwd=repo_root)
    subprocess.run(["git", "commit", "-m", f"Unzip upload: {zip_file.filename}"], cwd=repo_root)

    return {"status": "success", "detail": f"Extracted and committed {zip_file.filename}"}