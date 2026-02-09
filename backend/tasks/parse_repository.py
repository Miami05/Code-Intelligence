import os
import shutil
import zipfile
from typing import Any, cast

from celery.app.task import Task
from celery_app import celery_app
from config import settings
from database import SessionLocal
from models import File, Repository, Symbol
from models.repository import RepoStatus
from models.symbol import SymbolType
from parsers.assembly_parser import extract_assembly_symbols
from parsers.c_parser import extract_c_symbols
from parsers.cobol_parser import extract_cobol_symbols

# Import all language parsers
from parsers.python_parser import extract_python_symbols
from tasks.generate_embeddings import (
    generate_embeddings_for_repository as _generate_embeddings_for_repository,
)

generate_embeddings_for_repository = cast(Task, _generate_embeddings_for_repository)


# Language configuration
LANGUAGE_CONFIG = {
    "python": {"extensions": [".py"], "parser": extract_python_symbols, "icon": "🐍"},
    "c": {"extensions": [".c", ".h"], "parser": extract_c_symbols, "icon": "⚡"},
    "assembly": {
        "extensions": [".asm", ".s", ".S"],
        "parser": extract_assembly_symbols,
        "icon": "🔧",
    },
    "cobol": {
        "extensions": [".cob", ".COB", ".cbl", ".CBL"],
        "parser": extract_cobol_symbols,
        "icon": "📊",
    },
}


def get_language_from_extension(filename: str) -> tuple[str, Any, str] | None:
    """
    Determine language and parser from file extension.

    Returns:
        Tuple of (language_name, parser_function) or None if unsupported
    """
    for lang, config in LANGUAGE_CONFIG.items():
        for ext in config["extensions"]:
            if filename.endswith(ext):
                return lang, config["parser"], config["icon"]
    return None


@celery_app.task(bind=True, name="tasks.parse_repository.parse_repository_task")
def parse_repository_task(self, repository_id: str, zip_path: str):
    """
    Background task to parse repository and extract symbols.
    Supports: Python, C, Assembly, COBOL

    Args:
        repository_id: UUID of the repository
        zip_path: Path to uploaded ZIP file

    Returns:
        Dictionary with parsing statistics
    """
    db = SessionLocal()
    repo: Repository | None = None
    extract_dir: str | None = None

    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            return {"error": "Repository not found"}

        print(f"📦 Processing: {repo.name} (ID: {repository_id})")
        repo.status = RepoStatus.processing
        db.commit()

        extract_dir = f"/tmp/code_intel_{repository_id}"
        os.makedirs(extract_dir, exist_ok=True)
        print(f"📂 Extracting ZIP to: {extract_dir}")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        files_by_language = {lang: [] for lang in LANGUAGE_CONFIG.keys()}
        for root, dirs, files in os.walk(extract_dir):
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    ".git",
                    "__pycache__",
                    "node_modules",
                    ".venv",
                    "venv",
                    "build",
                    "dist",
                ]
            ]

            for file in files:
                lang_info = get_language_from_extension(file)
                if lang_info:
                    language, _, _ = lang_info
                    full_path = os.path.join(root, file)
                    files_by_language[language].append(full_path)

        for lang, files in files_by_language.items():
            if files:
                icon = LANGUAGE_CONFIG[lang]["icon"]
                print(f"{icon} Found {len(files)} {lang.upper()} files")

        total_files = sum(len(files) for files in files_by_language.values())
        if total_files == 0:
            print(
                "⚠️  No supported files found (looking for .py, .c, .h, .asm, .s, .cob, .COB)"
            )

        total_symbols = 0
        for language, file_paths in files_by_language.items():
            if not file_paths:
                continue

            parser_func = LANGUAGE_CONFIG[language]["parser"]

            for file_path in file_paths:
                relative_path = os.path.relpath(file_path, extract_dir)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                        line_count = len(source.splitlines())
                    file_record = File(
                        repository_id=repository_id,
                        file_path=relative_path,
                        language=language,
                        line_count=line_count,
                    )
                    db.add(file_record)
                    db.flush()
                    symbols = parser_func(source, relative_path)
                    print(f"  ✓ {relative_path}: {len(symbols)} symbols")
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
        repo.file_count = total_files
        repo.symbol_count = total_symbols
        repo.status = RepoStatus.completed
        db.commit()
        if extract_dir:
            shutil.rmtree(extract_dir, ignore_errors=True)
        print(f"✅ Repository {repository_id} completed")
        print(f"   Files: {total_files}, Symbols: {total_symbols}")
        if settings.enable_embeddings and settings.openai_api_key:
            print(f"🤖 Triggering embedding generation...")
            generate_embeddings_for_repository.delay(repository_id)

        return {
            "repository_id": repository_id,
            "files_processed": total_files,
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
