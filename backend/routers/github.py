"""
GitHub repository import endpoints
"""

from typing import Optional
from uuid import UUID

import celery_app
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Repository
from models.repository import RepoSource
from pydantic import BaseModel, HttpUrl
from pydantic_settings import sources
from sqlalchemy import desc
from sqlalchemy.orm import Session
from tasks.import_github import import_github_repository
from utils import github
from utils.github import parse_github_url, validate_github_url

router = APIRouter(prefix="/api/github", tags=["github"])


class GitHubImportRequest(BaseModel):
    url: str
    branch: Optional[str] = None
    token: Optional[str] = None
    name: Optional[str] = None


class GitHubImportResponse(BaseModel):
    repository_id: str
    owner: str
    repo: str
    branch: str
    status: str
    task_id: str
    message: str


@router.post("/import", response_model=GitHubImportResponse)
async def import_github_repo(
    request: GitHubImportRequest, db: Session = Depends(get_db)
):
    """
    Import a repository from GitHub.

    - **url**: GitHub repository URL (https://github.com/owner/repo)
    - **branch**: Branch to import (optional, defaults to main/master)
    - **token**: GitHub personal access token (optional, for private repos)
    - **name**: Custom name for repository (optional)
    """
    # Parse URL first
    parsed = parse_github_url(request.url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    owner, repo_name, default_branch = parsed
    branch = request.branch or default_branch
    
    # Check for duplicates BEFORE validating with GitHub API
    existing = (
        db.query(Repository)
        .filter(Repository.github_owner == owner)
        .filter(Repository.github_repo == repo_name)
        .filter(Repository.github_branch == branch)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Repository {owner}/{repo_name} (branch: {branch}) already imported",
        )
    
    # Now validate with GitHub API
    is_valid, error = validate_github_url(request.url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    repository = Repository(
        name=request.name or f"{owner}/{repo_name}",
        source=RepoSource.github,
        github_url=request.url,
        github_owner=owner,
        github_repo=repo_name,
        github_branch=branch,
    )
    db.add(repository)
    db.commit()
    db.refresh(repository)
    task = import_github_repository.delay(
        str(repository.id), request.url, branch, request.token
    )
    return GitHubImportResponse(
        repository_id=str(repository.id),
        owner=owner,
        repo=repo_name,
        branch=branch,
        status="processing",
        task_id=task.id,
        message=f"Importing {owner}/{repo_name} in background",
    )


@router.post("/validate")
async def validate_github_repo(url: str, token: Optional[str] = None):
    """
    Validate a GitHub URL without importing.
    """
    is_valid, error = validate_github_url(url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    parsed = parse_github_url(url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    owner, repo, branch = parsed
    return {"valid": True, "owner": owner, "repo": repo, "branch": branch, "url": url}


@router.get("/repositories")
async def list_github_repositories(
    page: int = 1, limit: int = 20, db: Session = Depends(get_db)
):
    """
    List all imported GitHub repositories.
    """
    offset = (page - 1) * limit
    repos = (
        db.query(Repository)
        .filter(Repository.source == RepoSource.github)
        .order_by(Repository.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Repository).filter(Repository.source == RepoSource.github).count()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "repositories": [
            {
                "id": str(r.id),
                "name": r.name,
                "owner": r.github_owner,
                "repo": r.github_repo,
                "branch": r.github_branch,
                "url": r.github_url,
                "stars": r.github_stars,
                "status": r.status.value,
                "file_count": r.file_count,
                "symbol_count": r.symbol_count,
                "created_at": r.created_at.isoformat(),
            }
            for r in repos
        ],
    }


@router.delete("/{repository_id}")
async def delete_github_repository(repository_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an imported GitHub repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.source != RepoSource.github:
        raise HTTPException(status_code=400, detail="Not a GitHub repository")
    db.delete(repo)
    db.commit()
    return {"message": f"Repository {repo.name} deleted successfully"}
