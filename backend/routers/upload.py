import os
import shutil

from config import settings
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from models import Repository
from sqlalchemy.orm import Session
from tasks.parse_repository import parse_repository_task

router = APIRouter(prefix="/api", tags=["upload"])
os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload")
async def upload_respository(
    file: UploadFile = File(..., description="ZIP file containing source code"),
    db: Session = Depends(get_db),
):
    """
    Upload ZIP file for analysis.

    Creates repository record and triggers background parsing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extension:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(settings.allowed_extension)} files supported",
        )
    repo = Repository(name=file.filename)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    print(f"📤 Uploading: {file.filename} (ID: {repo.id})")
    zip_path = os.path.join(settings.upload_dir, f"{repo.id}.zip")
    try:
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        db.delete(repo)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to save: {str(e)}")
    repo.upload_path = zip_path
    task = parse_repository_task.delay(repo.id, zip_path)
    db.commit()
    print(f"🚀 Task started: {task.id}")
    return {
        "repository_id": repo.id,
        "filename": file.filename,
        "status": "processing",
        "task_id": task.id,
        "message": "Upload successful. Processing in background.",
    }


@router.get("/upload/status")
def upload_status():
    """Upload endpoint health check."""
    return {
        "status": "operational",
        "upload_dir": settings.upload_dir,
        "max_size_mb": settings.max_upload_size_mb,
        "allowed_extensions": settings.allowed_extension,
    }
