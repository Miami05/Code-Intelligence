"""
Background task to import GitHub repository
"""

import os
import shutil
import uuid

from celery_app import celery_app
from database import SessionLocal
from models import Repository
from models.repository import RepoSource, RepoStatus
from utils.github import (
    clone_respository,
    get_github_metadata,
    get_latest_commit_sha,
    parse_github_url,
)


@celery_app.task(bind=True, name="tasks.import_github.import_github_repository")
def import_github_repository(
    self,
    repository_id: str,
    github_url: str,
    branch: str | None = None,
    token: str | None = None,
):
    """
    Import a repository from GitHub.

    Args:
        repository_id: UUID of Repository record
        github_url: GitHub repository URL
        branch: Branch to clone (optional, defaults to main)
        token: GitHub personal access token (optional, for private repos)
    """
    db = SessionLocal()
    repo = None
    clone_path = None
    try:
        repo_uuid = uuid.UUID(repository_id)
        repo = db.query(Repository).filter(Repository.id == repo_uuid).first()
        if not repo:
            raise Exception("Repository not found")
        print(f"🚀 Importing GitHub repository: {github_url}")
        repo.status = RepoStatus.processing
        db.commit()
        parsed = parse_github_url(github_url)
        if not parsed:
            raise Exception("Invalid GitHub URL")
        owner, repo_name, default_branch = parsed
        branch = branch or default_branch
        print(f"📋 Owner: {owner}, Repo: {repo_name}, Branch: {branch}")
        metadata = get_github_metadata(owner, repo_name, token)
        clone_path = clone_respository(owner, repo_name, branch, token)
        commit_sha = get_latest_commit_sha(clone_path)
        repo.github_owner = owner
        repo.github_repo = repo_name
        repo.github_url = github_url
        repo.github_branch = branch
        repo.github_stars = metadata.get("stars", 0)
        repo.github_last_commit = commit_sha
        repo.source = RepoSource.github
        if not repo.name or repo.name == "Unnamed":
            repo_name = f"{owner}/{repo_name}"
        db.commit()
        print("✅ Repository metadata updated")
        print(f"   Stars: {metadata.get('stars', 0)}")
        print(f"   Commit: {commit_sha}")
        print("📦 Creating archive from clone...")
        zip_path = f"/tmp/github_{repository_id}.zip"
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", clone_path)
        print("📦 Creating archive from clone...")
        celery_app.send_task(
            "tasks.parse_repository.parse_repository_task",
            args=[repository_id, zip_path],
        )
        return {
            "repository_id": repository_id,
            "owner": owner,
            "repo": repo_name,
            "branch": branch,
            "stars": metadata.get("stars", 0),
            "status": "processing",
        }
    except Exception as e:
        print(f"❌ GitHub import failed: {e}")
        if repo:
            repo.status = RepoStatus.failed
            db.commit()
        raise
    finally:
        if clone_path and os.path.exists(clone_path):
            shutil.rmtree(clone_path, ignore_errors=True)
        db.close()
