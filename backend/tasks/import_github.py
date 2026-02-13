"""
GitHub repository import task.
Clones GitHub repos and triggers parsing.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Optional

from celery_app import celery_app
from config import settings
from database import SessionLocal
from models.repository import Repository, RepoStatus
from tasks.parse_repository import parse_repository_task


def validate_github_url(url: str) -> tuple[str, str]:
    """
    Validate GitHub URL and extract owner/repo.

    Returns:
        Tuple of (owner, repo_name)
    Raises:
        ValueError if URL is invalid
    """
    if not url.startswith("https://github.com/"):
        raise ValueError("URL must start with https://github.com/")
    parts = url.replace("https://github.com/", "").rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub URL format. Expected: https://github.com/owner/repo"
        )
    owner, repo = parts[0], parts[1]
    if not owner or not repo:
        raise ValueError("Owner and repository name cannot be empty")
    return owner, repo


@celery_app.task(
    bind=True,
    name="tasks.import_github.import_github_repository",
    max_retries=3,
    default_retry_delay=60,
)
def import_github_repository(
    self,
    repository_id: str,
    github_url: str,
    branch: str = "main",
    token: Optional[str] = None,
):
    """
    Clone GitHub repository and import it.

    Args:
        repository_id: UUID of the repository record
        github_url: GitHub repository URL
        branch: Git branch to clone (default: main)
        token: Optional GitHub personal access token for private repos

    Returns:
        Dictionary with import statistics
    """
    db = SessionLocal()
    repo: Repository | None = None
    clone_dir: Optional[str] = None
    zip_path: Optional[str] = None

    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            return {"error": "Repository not found", "repository_id": repository_id}

        print(f"🐙 Cloning GitHub repo: {github_url}")
        print(f"   Branch: {branch}")
        print(f"   Repository ID: {repository_id}")

        repo.status = RepoStatus.processing
        db.commit()

        owner, repo_name = validate_github_url(github_url)
        print(f"   Owner: {owner}, Repo: {repo_name}")

        clone_dir = tempfile.mkdtemp(prefix=f"github_{owner}_{repo_name}_")
        print(f"   Clone directory: {clone_dir}")

        clone_url = github_url
        if token:
            clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"

        try:
            cmd = [
                "git",
                "clone",
                "--depth=1",
                "--single-branch",
                "--branch",
                branch,
                clone_url,
                clone_dir,
            ]

            print(f"   Executing: git clone --depth=1 --branch {branch} [URL] [DIR]")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                print(f"   ❌ Git clone failed: {error_msg}")
                raise Exception(f"Git clone failed: {error_msg}")

            print(f"   ✅ Clone successful")

        except subprocess.TimeoutExpired:
            raise Exception("Git clone timed out after 5 minutes")
        except Exception as e:
            raise Exception(f"Git clone error: {str(e)}")

        git_dir = os.path.join(clone_dir, ".git")
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
            print(f"   Removed .git directory")

        file_count = sum(
            1
            for root, dirs, files in os.walk(clone_dir)
            for file in files
            if not file.startswith(".")
        )
        print(f"   Found {file_count} files")

        zip_path = os.path.join(settings.upload_dir, f"{repository_id}_github.zip")
        os.makedirs(settings.upload_dir, exist_ok=True)
        print(f"   Creating ZIP archive: {zip_path}")
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", clone_dir)
        print(f"   ✅ ZIP created")

        repo.upload_path = zip_path
        db.commit()

        if clone_dir and os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
            clone_dir = None
            print(f"   Cleaned up clone directory")

        print(f"   🚀 Triggering parse task...")
        parse_task = parse_repository_task.delay(repository_id, zip_path)

        return {
            "repository_id": repository_id,
            "github_url": github_url,
            "branch": branch,
            "owner": owner,
            "repo": repo_name,
            "status": "parsing",
            "parse_task_id": parse_task.id,
            "file_count": file_count,
        }

    except Exception as e:
        print(f"❌ GitHub import error: {e}")

        if repo:
            repo.status = RepoStatus.failed
            db.commit()

        if "timed out" in str(e).lower() or "network" in str(e).lower():
            raise self.retry(exc=e)

        raise

    finally:
        if clone_dir and os.path.exists(clone_dir):
            shutil.rmtree(clone_dir, ignore_errors=True)

        db.close()
