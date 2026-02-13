"""
GitHub integration API endpoints.
"""

from typing import Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.repository import Repository, RepoStatus
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from tasks.import_github import import_github_repository, validate_github_url
from utils.github import parse_github_url, validate_github_url as validate_url_util

router = APIRouter(prefix="/api/github", tags=["github"])


class GitHubImportRequest(BaseModel):
    """Request model for importing a GitHub repository."""

    url: str = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Branch to import")
    token: Optional[str] = Field(
        default=None, description="GitHub personal access token (for private repos)"
    )


class GitHubImportResponse(BaseModel):
    """Response model for GitHub import."""

    repository_id: str
    owner: str
    repo: str
    branch: str
    status: str
    task_id: str
    message: str


class GitHubValidateResponse(BaseModel):
    """Response model for GitHub URL validation."""

    valid: bool
    owner: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None
    url: str
    error: Optional[str] = None


class GitHubRepository(BaseModel):
    """GitHub repository information."""

    id: str
    name: str
    owner: str
    repo: str
    github_url: str
    branch: str
    status: str
    file_count: int
    symbol_count: int
    github_stars: Optional[int] = None
    github_language: Optional[str] = None
    created_at: str


@router.post("/validate", response_model=GitHubValidateResponse)
async def validate_github_repo(url: str = Query(..., description="GitHub repository URL")):
    """
    Validate a GitHub repository URL.
    
    Checks if the URL is properly formatted and the repository exists.
    """
    # Parse URL
    parsed = parse_github_url(url)
    if not parsed:
        return GitHubValidateResponse(
            valid=False,
            url=url,
            error="Invalid GitHub URL format"
        )
    
    owner, repo, branch = parsed
    
    # Validate with GitHub API
    is_valid, error = validate_url_util(url)
    
    if not is_valid:
        return GitHubValidateResponse(
            valid=False,
            url=url,
            error=error
        )
    
    return GitHubValidateResponse(
        valid=True,
        owner=owner,
        repo=repo,
        branch=branch,
        url=url
    )


@router.post("/import", response_model=GitHubImportResponse)
async def import_github_repo(
    request: GitHubImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import a GitHub repository for analysis.

    The repository will be cloned and processed in the background.
    """
    try:
        owner, repo_name = validate_github_url(request.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing = (
        db.query(Repository)
        .filter(Repository.github_url == request.url)
        .filter(Repository.github_branch == request.branch)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Repository already imported: {existing.id}",
        )

    repository = Repository(
        name=f"{owner}/{repo_name}",
        github_url=request.url,
        github_owner=owner,
        github_repo=repo_name,
        github_branch=request.branch,
        status=RepoStatus.pending,
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    print(f"📦 GitHub import requested: {owner}/{repo_name}")
    print(f"   Repository ID: {repository.id}")
    print(f"   Branch: {request.branch}")

    task = import_github_repository.delay(
        str(repository.id), request.url, request.branch, request.token
    )

    return GitHubImportResponse(
        repository_id=str(repository.id),
        owner=owner,
        repo=repo_name,
        branch=request.branch,
        status="processing",
        task_id=task.id,
        message=f"Importing {owner}/{repo_name} in background",
    )


@router.get("/repositories", response_model=list[GitHubRepository])
async def list_github_repositories(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List all imported GitHub repositories.
    """
    repos = (
        db.query(Repository)
        .filter(Repository.github_url.isnot(None))
        .order_by(Repository.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [
        GitHubRepository(
            id=str(repo.id),
            name=repo.name,
            owner=repo.github_owner or "",
            repo=repo.github_repo or "",
            github_url=repo.github_url or "",
            branch=repo.github_branch or "main",
            status=repo.status.value,
            file_count=repo.file_count or 0,
            symbol_count=repo.symbol_count or 0,
            github_stars=repo.github_stars,
            github_language=repo.github_language,
            created_at=repo.created_at.isoformat(),
        )
        for repo in repos
    ]


@router.get("/repositories/{repository_id}", response_model=GitHubRepository)
async def get_github_repository(
    repository_id: str,
    db: Session = Depends(get_db),
):
    """
    Get details of a specific GitHub repository.
    """
    repo = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .filter(Repository.github_url.isnot(None))
        .first()
    )

    if not repo:
        raise HTTPException(status_code=404, detail="GitHub repository not found")

    return GitHubRepository(
        id=str(repo.id),
        name=repo.name,
        owner=repo.github_owner or "",
        repo=repo.github_repo or "",
        github_url=repo.github_url or "",
        branch=repo.github_branch or "main",
        status=repo.status.value,
        file_count=repo.file_count or 0,
        symbol_count=repo.symbol_count or 0,
        github_stars=repo.github_stars,
        github_language=repo.github_language,
        created_at=repo.created_at.isoformat(),
    )


@router.delete("/repositories/{repository_id}")
async def delete_github_repository(
    repository_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a GitHub repository and all its data.
    """
    repo = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .filter(Repository.github_url.isnot(None))
        .first()
    )

    if not repo:
        raise HTTPException(status_code=404, detail="GitHub repository not found")

    db.delete(repo)
    db.commit()

    return {"message": f"Repository {repository_id} deleted successfully"}


@router.get("/stats")
async def github_stats(db: Session = Depends(get_db)):
    """
    Get statistics about imported GitHub repositories.
    """
    total = (
        db.query(func.count(Repository.id))
        .filter(Repository.github_url.isnot(None))
        .scalar()
        or 0
    )

    completed = (
        db.query(func.count(Repository.id))
        .filter(Repository.github_url.isnot(None))
        .filter(Repository.status == RepoStatus.completed)
        .scalar()
        or 0
    )

    failed = (
        db.query(func.count(Repository.id))
        .filter(Repository.github_url.isnot(None))
        .filter(Repository.status == RepoStatus.failed)
        .scalar()
        or 0
    )

    total_files = (
        db.query(func.sum(Repository.file_count))
        .filter(Repository.github_url.isnot(None))
        .scalar()
        or 0
    )

    total_symbols = (
        db.query(func.sum(Repository.symbol_count))
        .filter(Repository.github_url.isnot(None))
        .scalar()
        or 0
    )

    return {
        "total_repositories": total,
        "completed": completed,
        "failed": failed,
        "processing": total - completed - failed,
        "total_files": total_files,
        "total_symbols": total_symbols,
    }
