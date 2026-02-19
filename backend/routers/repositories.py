import os
from pathlib import Path
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

# Explicitly handle 'import' to prevent it falling into the generic {repository_id} route
@router.get("/import")
def get_import_placeholder():
    """Placeholder for potential API collision with frontend route."""
    raise HTTPException(status_code=404, detail="This is a frontend route, not an API endpoint.")


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


@router.get("/{repository_id}/files/{file_path:path}/content")
def get_file_content(
    repository_id: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    """Get content of a specific file from repository.
    
    Args:
        repository_id: UUID of the repository
        file_path: Relative path to the file within the repository
        db: Database session
        
    Returns:
        Dictionary with file content, language, line count, and metadata
        
    Raises:
        HTTPException: 404 if repository or file not found, 500 for read errors
    """
    # Get repository
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if not repo.upload_path:
        raise HTTPException(
            status_code=400,
            detail="Repository does not have an upload path"
        )
    
    # Get file metadata from database
    file_record = (
        db.query(File)
        .filter(
            File.repository_id == repository_id,
            File.file_path == file_path
        )
        .first()
    )
    
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_path}' not found in repository"
        )
    
    # Construct full file path
    full_path = Path(repo.upload_path) / file_path
    
    # Security check: ensure the resolved path is within the repository directory
    try:
        full_path = full_path.resolve()
        repo_path = Path(repo.upload_path).resolve()
        
        # Check if file is within repository directory (prevents path traversal)
        if not str(full_path).startswith(str(repo_path)):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Path traversal detected"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file path: {str(e)}"
        )
    
    # Check if file exists
    if not full_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found on disk: {file_path}"
        )
    
    if not full_path.is_file():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a file: {file_path}"
        )
    
    # Read file content
    try:
        # Try UTF-8 first, fallback to latin-1 for binary-like files
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        return {
            "repository_id": str(repository_id),
            "file_path": file_path,
            "content": content,
            "language": file_record.language,
            "line_count": file_record.line_count,
            "size_bytes": os.path.getsize(full_path),
            "file_id": str(file_record.id),
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )


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
