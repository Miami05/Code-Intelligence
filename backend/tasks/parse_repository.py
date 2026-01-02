import os
import shutil
import zipfile
from typing import cast

from celery import Task

from celery_app import celery_app
from database import SessionLocal
from models import File, Repository, Symbol
from models.repository import RepoStatus
from models.symbol import SymbolType
from parsers.python_parser import extract_python_symbols


def _parse_repository_task(self, repository_id: str, zip_path: str):
    """
    Background task to parse repository and extract symbols.

    Args:
        repository_id: UUID of the repository
        zip_path: Path to uploaded ZIP file

    Returns:
        Dictionary with parsing statistics
    """
    db = SessionLocal()
    repo: Repository | None = None
    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            return {"error": "Repository not found"}
        print(f"📦 Processing: {repo.name} (ID: {repository_id}")
        repo.status = RepoStatus.processing
        db.commit()
        extract_dir = f"/tmp/code_intel_{repository_id}"
        os.makedirs(extract_dir, exist_ok=True)
        print(f"📂 Extracting ZIP to: {extract_dir}")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        python_files = []
        for root, dirs, files in os.walk(extract_dir):
            dirs[:] = [
                d
                for d in dirs
                if d not in [".git", "__pycache__", "node_modules", ".venv", "venv"]
            ]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        print(f"🐍 Found {len(python_files)} Python files")
        total_symbols = 0
        for py_file_path in python_files:
            relative_path = os.path.relpath(py_file_path, extract_dir)
            try:
                with open(py_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                    line_count = len(source.splitlines())
                file_record = File(
                    repository_id=repository_id,
                    file_path=relative_path,
                    language="python",
                    line_count=line_count,
                )
                db.add(file_record)
                db.flush()
                symbols = extract_python_symbols(source, relative_path)
                print(f" ✓ {relative_path}: {len(symbols)} symbols")
                for sym in symbols:
                    symbol_record = Symbol(
                        file_id=file_record.id,
                        name=sym["name"],
                        type=SymbolType[sym["type"]],
                        line_start=sym["line_start"],
                        line_end=sym["line_end"],
                        signature=sym.get("signature"),
                    )
                    db.add(symbol_record)
                    total_symbols += 1
            except Exception as e:
                print(f"  ⚠️  Error processing {relative_path}: {e}")
                continue
        repo.file_count = len(python_files)
        repo.symbol_count = total_symbols
        repo.status = RepoStatus.completed
        db.commit()
        shutil.rmtree(extract_dir, ignore_errors=True)
        print(f"✅ Repository {repository_id} completed")
        print(f"   Files: {len(python_files)}, Symbols: {total_symbols}")
        return {
            "repository_id": repository_id,
            "files_processed": len(python_files),
            "symbols_extracted": total_symbols,
            "status": "completed",
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        if repo:
            repo.status = RepoStatus.failed
            db.commit()
        raise
    finally:
        db.close()


parse_repository_task = celery_app.task(
    bind=True,
    name="tasks.parse_repository.parse_repository_task",
)(_parse_repository_task)

parse_repository_task = cast(Task, parse_repository_task)
