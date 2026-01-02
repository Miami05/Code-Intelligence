from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import File, Repository, Symbol

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.get("")
def list_repositories(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List all repositories with pagination."""
    total = db.query(func.count(Repository.id)).scalar()
    repos = (
        db.query(Repository)
        .order_by(Repository.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "repositories": [
            {
                "id": repo.id,
                "name": repo.name,
                "status": repo.status.value,
                "file_count": repo.file_count,
                "symbol_count": repo.symbol_count,
                "created_at": repo.created_at.isoformat(),
            }
            for repo in repos
        ],
    }


@router.get("/{repository_id}")
def get_repository(repository_id: str, db: Session = Depends(get_db)):
    """Get repository details."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {
        "id": repo.id,
        "name": repo.name,
        "status": repo.status.value,
        "file_count": repo.file_count,
        "symbol_count": repo.symbol_count,
        "upload_path": repo.upload_path,
        "created_at": repo.created_at.isoformat(),
    }


@router.get("/{repository_id}/files")
def get_repository_files(
    repository_id: str,
    language: Optional[str] = Query(None),
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
):
    """Get files in repository."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    query = db.query(File).filter(File.repository_id == repository_id)
    if language:
        query = query.filter(File.language == language)
    files = query.limit(limit).all()
    return {
        "repository_id": repository_id,
        "total_files": len(files),
        "files": [
            {
                "id": file.id,
                "file_path": file.file_path,
                "language": file.language,
                "line_count": file.line_count,
                "created_at": file.created_at.isoformat(),
            }
            for file in files
        ],
    }


@router.get("/{repository_id}/symbols")
def get_repository_symbols(
    repository_id: str,
    language: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db),
):
    """Get symbols (functions, classes) from repository."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    query = (
        db.query(Symbol, File).join(File).filter(File.repository_id == repository_id)
    )
    if language:
        query = query.filter(File.language == language)
    if type:
        query = query.filter(Symbol.type == type)
    results = query.limit(limit).all()
    return {
        "repository_id": repository_id,
        "total_symbols": len(results),
        "filters": {"language": language, "type": type},
        "symbols": [
            {
                "symbol_id": symbol.id,
                "name": symbol.name,
                "type": symbol.type.value,
                "file_path": file.file_path,
                "line_start": symbol.line_start,
                "line_end": symbol.line_end,
                "signature": symbol.signature,
            }
            for symbol, file in results
        ],
    }
