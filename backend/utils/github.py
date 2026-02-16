"""
GitHub repository utilities
"""

import os
import re
import shutil
from typing import Optional, Tuple

import git
import requests
from config import settings
from git.exc import GitCommandError


def parse_github_url(url: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse GitHub URL to extract owner, repo, and branch.

    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo/tree/branch
    - git@github.com:owner/repo.git

    Returns:
        (owner, repo, branch) or None if invalid
    """
    # Pattern to match GitHub URLs - Fixed: Changed +? to + for greedy matching
    http_pattern = r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?(?:/tree/([^/\s]+))?/?$"
    
    # First try: Match with explicit .git handling
    # This ensures "So-Long.git" captures "So-Long" not "So-Lon"
    git_pattern = r"github\.com[:/]([^/]+)/(.+?)\.git(?:/tree/([^/\s]+))?/?$"
    match = re.search(git_pattern, url)
    
    if match:
        owner = match.group(1)
        repo = match.group(2)
        branch = match.group(3) or "main"
        return owner, repo, branch
    
    # Second try: Match without .git suffix
    no_git_pattern = r"github\.com[:/]([^/]+)/([^/\s.]+)(?:/tree/([^/\s]+))?/?$"
    match = re.search(no_git_pattern, url)
    
    if match:
        owner = match.group(1)
        repo = match.group(2)
        branch = match.group(3) or "main"
        
        # Defensively remove .git suffix if somehow still present
        if repo.endswith(".git"):
            repo = repo[:-4]
        
        return owner, repo, branch
    
    return None


def get_github_metadata(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """
    Fetch repository metadata from GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name (without .git suffix)
        token: Optional GitHub personal access token

    Returns:
        Dictionary with stars, last_commit, default_branch, etc.
    """
    # Ensure repo doesn't have .git suffix for API call
    repo = repo.rstrip(".git") if repo.endswith(".git") else repo
    
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {}

    # Use provided token or fall back to settings
    auth_token = token or settings.github_token
    if auth_token:
        headers["Authorization"] = f"token {auth_token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "stars": data.get("stargazers_count", 0),
            "default_branch": data.get("default_branch", "main"),
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "last_push": data.get("pushed_at", ""),
        }
    except Exception as e:
        print(f"⚠️  Failed to fetch GitHub metadata: {e}")
        return {}


def clone_respository(
    owner: str,
    repo: str,
    branch: str = "main",
    token: Optional[str] = None,
    target_dir: Optional[str] = None,
):
    """
    Clone a GitHub repository.

    Args:
        owner: Repository owner
        repo: Repository name (without .git suffix)
        branch: Branch to clone (default: main)
        token: Optional GitHub token for private repos
        target_dir: Target directory (default: /tmp/repo_<random>)

    Returns:
        Path to cloned repository

    Raises:
        Exception if clone fails
    """
    # Ensure repo doesn't have .git suffix
    repo = repo.rstrip(".git") if repo.endswith(".git") else repo
    
    if target_dir is None:
        target_dir = f"/tmp/github_clone_{owner}_{repo}"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Use provided token or fall back to settings
    auth_token = token or settings.github_token
    if auth_token:
        clone_url = f"https://{auth_token}@github.com/{owner}/{repo}.git"
    else:
        clone_url = f"https://github.com/{owner}/{repo}.git"

    print(f"📥 Cloning {owner}/{repo} (branch: {branch})...")
    try:
        git.Repo.clone_from(clone_url, target_dir, branch=branch, depth=1)
        print(f"✅ Cloned to {target_dir}")
        return target_dir
    except GitCommandError as e:
        raise Exception(f"Failed to clone repository: {e}")


def get_latest_commit_sha(clone_path: str) -> str:
    """Get SHA of latest commit in cloned repo."""
    try:
        repo = git.Repo(clone_path)
        return repo.head.commit.hexsha[:7]
    except:
        return "unknown"


def validate_github_url(url: str) -> Tuple[bool, str]:
    """
    Validate if URL is a valid GitHub repository.

    Returns:
        (is_valid, error_message)
    """
    parsed = parse_github_url(url)
    if not parsed:
        return False, "Invalid GitHub URL format"

    owner, repo, _ = parsed
    
    # Ensure repo doesn't have .git suffix for API call
    repo = repo.rstrip(".git") if repo.endswith(".git") else repo

    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=5
        )

        if response.status_code == 404:
            return False, "Repository not found"
        elif response.status_code == 403:
            rate_limit = response.headers.get("X-RateLimit-Remaining", "0")
            if rate_limit == "0":
                return (
                    False,
                    "GitHub API rate limit exceeded. Please add GITHUB_TOKEN to .env",
                )
            return False, "Private repository (token required)"
        elif response.status_code != 200:
            return False, f"GitHub API error: {response.status_code}"

        return True, ""

    except requests.Timeout:
        return False, "GitHub API timeout"
    except Exception as e:
        return False, f"Failed to validate: {e}"
