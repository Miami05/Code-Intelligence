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
from models.repository import Repository, RepoStatus, RepoSource
from tasks.parse_repository import parse_repository_task
from utils.github import get_github_metadata


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
    
    # Remove https://github.com/ and trailing slash
    url_path = url.replace("https://github.com/", "").rstrip("/")
    
    # Remove .git suffix if present (proper way, not rstrip!)
    if url_path.endswith(".git"):
        url_path = url_path[:-4]
    
    parts = url_path.split("/")
    
    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub URL format. Expected: https://github.com/owner/repo"
        )
    
    owner, repo = parts[0], parts[1]
    
    # Additional cleanup - proper suffix removal (not rstrip!)
    # rstrip(".git") removes ANY char in {'.','g','i','t'}, not the substring!
    # This caused "So-Long" to become "So-Lon" (removed the 'g')
    if repo.endswith(".git"):
        repo = repo[:-4]
    
    if not owner or not repo:
        raise ValueError("Owner and repository name cannot be empty")
    
    return owner, repo


def try_clone_with_fallback_branches(
    clone_url: str, clone_dir: str, preferred_branch: str, timeout: int = 300
) -> tuple[bool, Optional[str], str]:
    """
    Try to clone repository with multiple branch fallbacks.

    Args:
        clone_url: Git clone URL
        clone_dir: Target directory
        preferred_branch: First branch to try
        timeout: Timeout in seconds

    Returns:
        Tuple of (success: bool, error_message: str | None, actual_branch: str)
    """
    # Try branches in order: specified branch, then fallbacks
    branches_to_try = [preferred_branch]
    
    # Add common fallback branches if not already in list
    for fallback in ["main", "master", "develop"]:
        if fallback not in branches_to_try:
            branches_to_try.append(fallback)
    
    last_error = None
    
    for branch in branches_to_try:
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

            print(f"   Trying branch: {branch}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                print(f"   ✅ Successfully cloned branch: {branch}")
                return (True, None, branch)
            else:
                error_msg = result.stderr or result.stdout
                last_error = error_msg
                
                # If directory was created but clone failed, clean it up
                if os.path.exists(clone_dir) and not os.listdir(clone_dir):
                    os.rmdir(clone_dir)
                
                # Check if it's a branch not found error
                if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                    print(f"   ⚠️  Branch '{branch}' not found, trying next...")
                    continue
                else:
                    # Other error (auth, network, etc.) - don't try other branches
                    print(f"   ❌ Clone failed with error: {error_msg}")
                    return (False, error_msg, branch)

        except subprocess.TimeoutExpired:
            print(f"   ❌ Clone timed out for branch: {branch}")
            return (False, f"Git clone timed out after {timeout} seconds", branch)
        except Exception as e:
            print(f"   ❌ Exception during clone: {e}")
            last_error = str(e)
            continue
    
    # All branches failed
    return (False, f"Failed to clone any branch. Tried: {', '.join(branches_to_try)}. Last error: {last_error}", branches_to_try[0])


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
    actual_branch = branch

    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            return {"error": "Repository not found", "repository_id": repository_id}

        print(f"🐙 Cloning GitHub repo: {github_url}")
        print(f"   Preferred Branch: {branch}")
        print(f"   Repository ID: {repository_id}")

        repo.status = RepoStatus.processing
        repo.source = RepoSource.github  # Set source to github
        db.commit()

        owner, repo_name = validate_github_url(github_url)
        print(f"   Owner: {owner}, Repo: {repo_name}")

        # Fetch GitHub metadata (stars, language, etc.)
        print(f"   📊 Fetching GitHub metadata...")
        metadata = get_github_metadata(owner, repo_name, token)
        if metadata:
            repo.github_stars = metadata.get("stars", 0)
            repo.github_language = metadata.get("language", "")
            print(f"   ✅ Metadata: {repo.github_stars} stars, Language: {repo.github_language}")
            db.commit()
        else:
            print(f"   ⚠️  Could not fetch metadata")

        clone_dir = tempfile.mkdtemp(prefix=f"github_{owner}_{repo_name}_")
        print(f"   Clone directory: {clone_dir}")

        # Build clone URL - always use .git suffix for git command
        if token:
            clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
        elif settings.github_token:
            clone_url = f"https://{settings.github_token}@github.com/{owner}/{repo_name}.git"
        else:
            clone_url = f"https://github.com/{owner}/{repo_name}.git"

        # Try cloning with branch fallbacks
        success, error_msg, actual_branch = try_clone_with_fallback_branches(
            clone_url, clone_dir, branch, timeout=300
        )

        if not success:
            print(f"   ❌ All clone attempts failed: {error_msg}")
            raise Exception(f"Git clone failed: {error_msg}")

        print(f"   ✅ Clone successful (branch: {actual_branch})")

        # Remove .git directory to save space
        git_dir = os.path.join(clone_dir, ".git")
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
            print(f"   Removed .git directory")

        # Count files
        file_count = sum(
            1
            for root, dirs, files in os.walk(clone_dir)
            for file in files
            if not file.startswith(".")
        )
        print(f"   Found {file_count} files")

        # Create ZIP archive
        zip_path = os.path.join(settings.upload_dir, f"{repository_id}_github.zip")
        os.makedirs(settings.upload_dir, exist_ok=True)
        print(f"   Creating ZIP archive: {zip_path}")
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", clone_dir)
        print(f"   ✅ ZIP created")

        repo.upload_path = zip_path
        db.commit()

        # Clean up clone directory
        if clone_dir and os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
            clone_dir = None
            print(f"   Cleaned up clone directory")

        # Trigger parsing task
        print(f"   🚀 Triggering parse task...")
        parse_task = parse_repository_task.delay(repository_id, zip_path)

        return {
            "repository_id": repository_id,
            "github_url": github_url,
            "branch": actual_branch,
            "requested_branch": branch,
            "owner": owner,
            "repo": repo_name,
            "status": "parsing",
            "parse_task_id": parse_task.id,
            "file_count": file_count,
            "stars": repo.github_stars,
            "language": repo.github_language,
        }

    except Exception as e:
        print(f"❌ GitHub import error: {e}")

        if repo:
            repo.status = RepoStatus.failed
            db.commit()

        # Retry on timeout/network errors
        if "timed out" in str(e).lower() or "network" in str(e).lower():
            raise self.retry(exc=e)

        raise

    finally:
        # Cleanup
        if clone_dir and os.path.exists(clone_dir):
            shutil.rmtree(clone_dir, ignore_errors=True)

        db.close()
