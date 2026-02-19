"""Advanced Analysis Endpoints - Sprint 9"""

import uuid
from typing import Dict, List, Optional

from database import SessionLocal, get_db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models import (
    CodeDuplication,
    CodeSmell,
    File,
    MetricsSnapshot,
    Repository,
    SmellSeverity,
    Symbol,
)
from models.code_smell import SmellType
from models.symbol import SymbolType
from services.auto_documentation import AutoDocumentationService
from services.code_smell_detector import CodeSmellDetector
from services.duplication_scanner import DuplicateScanner
from services.metrics_tracker import MetricsTracker
from sqlalchemy import delete
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/api/analysis", tags=["Advanced Analysis"])


# ----- Code Duplication Endpoints -----


@router.post("/duplications/{repository_id}")
async def scan_duplications(
    repository_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Scan repository for code duplications.
    Runs asynchronously in background.
    """
    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Queue background task
    background_tasks.add_task(scan_duplications_task, repository_id)

    return {
        "status": "started",
        "message": "Duplication scan started in background",
        "repository_id": str(repository_id),
    }


async def scan_duplications_task(repository_id: uuid.UUID):
    """Background task to scan for duplications"""
    db: Session = SessionLocal()
    try:
        # Fetch all files with content
        files = db.query(File).filter_by(repository_id=repository_id).all()

        file_data = []
        for file in files:
            # Read file content (assuming files are stored)
            try:
                with open(file.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                file_data.append(
                    {
                        "id": file.id,
                        "path": file.file_path,
                        "content": content,
                        "language": file.language or "python",
                    }
                )
            except Exception as e:
                print(f"Error reading file {file.file_path}: {e}")
                continue

        # Run duplication scanner
        scanner = DuplicateScanner()
        duplications = scanner.scan_repository(file_data)

        # Clear existing duplications for this repo
        db.execute(
            delete(CodeDuplication).where(
                CodeDuplication.repository_id == repository_id
            )
        )
        db.commit()

        # Save to database
        for dup in duplications:
            db_dup = CodeDuplication(
                repository_id=repository_id,
                file1_id=dup["file1_id"],
                file1_start_line=dup["file1_start_line"],
                file1_end_line=dup["file1_end_line"],
                file2_id=dup["file2_id"],
                file2_start_line=dup["file2_start_line"],
                file2_end_line=dup["file2_end_line"],
                similarity_score=dup["similarity_score"],
                duplicate_lines=dup["duplicate_lines"],
                duplicate_tokens=dup["duplicate_tokens"],
                code_snippet=dup["code_snippet"],
                hash_signature=dup["hash_signature"],
            )
            db.add(db_dup)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"scan_duplications_task failed for repo {repository_id}: {e}")
    finally:
        db.close()


@router.get("/duplications/{repository_id}")
async def get_duplications(
    repository_id: uuid.UUID,
    min_similarity: float = 0.8,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get detected code duplications for a repository"""

    duplications = (
        db.query(CodeDuplication)
        .filter(
            CodeDuplication.repository_id == repository_id,
            CodeDuplication.similarity_score >= min_similarity,
        )
        .order_by(CodeDuplication.similarity_score.desc())
        .limit(limit)
        .all()
    )

    results = []
    # Optimization: batch fetch files
    file_ids = set()
    for dup in duplications:
        file_ids.add(dup.file1_id)
        file_ids.add(dup.file2_id)

    files = db.query(File).filter(File.id.in_(file_ids)).all()
    file_map = {f.id: f for f in files}

    for dup in duplications:
        file1 = file_map.get(dup.file1_id)
        file2 = file_map.get(dup.file2_id)

        results.append(
            {
                "id": str(dup.id),
                "file1": {
                    "id": str(dup.file1_id),
                    "path": file1.file_path if file1 else "Unknown",
                    "start_line": dup.file1_start_line,
                    "end_line": dup.file1_end_line,
                },
                "file2": {
                    "id": str(dup.file2_id),
                    "path": file2.file_path if file2 else "Unknown",
                    "start_line": dup.file2_start_line,
                    "end_line": dup.file2_end_line,
                },
                "similarity": round((dup.similarity_score or 0) * 100, 1),
                "duplicate_lines": dup.duplicate_lines,
                "duplicate_tokens": dup.duplicate_tokens,
                "code_snippet": (dup.code_snippet or "")[:200],
            }
        )

    return {
        "repository_id": str(repository_id),
        "total_duplications": len(results),
        "duplications": results,
    }


# ----- Code Smell Endpoints -----


@router.post("/code-smells/{repository_id}")
async def scan_code_smells(
    repository_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Scan repository for code smells"""

    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    background_tasks.add_task(scan_code_smells_task, repository_id)

    return {
        "status": "started",
        "message": "Code smell scan started in background",
        "repository_id": str(repository_id),
    }


async def scan_code_smells_task(repository_id: uuid.UUID):
    """Background task to scan for code smells"""
    db: Session = SessionLocal()
    try:
        files = db.query(File).filter_by(repository_id=repository_id).all()

        file_data = []
        for file in files:
            try:
                with open(file.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Get symbols for this file
                symbols = db.query(Symbol).filter_by(file_id=file.id).all()
                symbol_data = [
                    {
                        "id": s.id,
                        "name": s.name,
                        "type": (
                            s.type.value if hasattr(s.type, "value") else str(s.type)
                        ),
                        "start_line": s.line_start,
                        "end_line": s.line_end,
                        "parent_id": s.parent_id,
                    }
                    for s in symbols
                ]

                file_data.append(
                    {
                        "id": file.id,
                        "path": file.file_path,
                        "content": content,
                        "symbols": symbol_data,
                    }
                )
            except Exception as e:
                print(f"Error reading file {file.file_path}: {e}")
                continue

        # Run code smell detector
        detector = CodeSmellDetector()
        smells = detector.scan_repository(file_data)

        # Clear existing smells
        db.execute(delete(CodeSmell).where(CodeSmell.repository_id == repository_id))
        db.commit()

        # Save to database
        for smell in smells:
            db_smell = CodeSmell(
                repository_id=repository_id,
                file_id=smell.file_id,
                symbol_id=smell.symbol_id,
                smell_type=smell.smell_type,
                severity=smell.severity,
                title=smell.title,
                description=smell.description,
                suggestion=smell.suggestion,
                start_line=smell.start_line,
                end_line=smell.end_line,
                metric_value=smell.metric_value,
                metric_threshold=smell.metric_threshold,
            )
            db.add(db_smell)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"scan_code_smells_task failed for repo {repository_id}: {e}")
    finally:
        db.close()


@router.get("/code-smells/{repository_id}")
async def get_code_smells(
    repository_id: uuid.UUID,
    severity: Optional[str] = None,
    smell_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get detected code smells for a repository"""

    query = (
        db.query(CodeSmell)
        .options(joinedload(CodeSmell.file), joinedload(CodeSmell.symbol))
        .filter(CodeSmell.repository_id == repository_id)
    )

    if severity:
        try:
            severity_enum = SmellSeverity(severity.lower())
            query = query.filter(CodeSmell.severity == severity_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity")
    if smell_type:
        try:
            smell_type_enum = SmellType(smell_type.lower())
            query = query.filter(CodeSmell.smell_type == smell_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid smell_type")

    smells = (
        query.order_by(CodeSmell.severity.desc(), CodeSmell.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []
    for smell in smells:
        results.append(
            {
                "id": str(smell.id),
                "smell_type": smell.smell_type.value,
                "severity": smell.severity.value,
                "title": smell.title,
                "description": smell.description,
                "suggestion": smell.suggestion,
                "file": {
                    "id": str(smell.file_id),
                    "path": smell.file.file_path if smell.file else "Unknown",
                },
                "symbol": (
                    {
                        "id": str(smell.symbol_id),
                        "name": smell.symbol.name if smell.symbol else None,
                    }
                    if smell.symbol_id
                    else None
                ),
                "location": {
                    "start_line": smell.start_line,
                    "end_line": smell.end_line,
                },
                "metrics": {
                    "value": smell.metric_value,
                    "threshold": smell.metric_threshold,
                },
            }
        )

    return {
        "repository_id": str(repository_id),
        "total_smells": len(results),
        "code_smells": results,
    }


@router.get("/undocumented/{repository_id}")
async def get_undocumented_symbols(
    repository_id: uuid.UUID, limit: int = 100, db: Session = Depends(get_db)
):
    """List symbols that are missing documentation (Sprint 9)"""
    symbols = (
        db.query(Symbol)
        .join(File)
        .filter(
            File.repository_id == repository_id,
            Symbol.has_docstring == False,
            Symbol.type.in_([SymbolType.function, SymbolType.class_]),
        )
        .limit(limit)
        .all()
    )

    return {
        "repository_id": str(repository_id),
        "count": len(symbols),
        "undocumented_symbols": [
            {
                "id": str(s.id),
                "name": s.name,
                "type": (s.type.value if hasattr(s.type, "value") else str(s.type)),
                "file": s.file.file_path,
                "line": s.line_start,
            }
            for s in symbols
        ],
    }


@router.post("/auto-document/{repository_id}")
async def generate_documentation(
    repository_id: uuid.UUID, max_files: int = 10, db: Session = Depends(get_db)
):
    """Generate documentation for undocumented functions"""

    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    files = (
        db.query(File)
        .join(Symbol)
        .filter(
            File.repository_id == repository_id,
            Symbol.has_docstring == False,
            Symbol.type.in_([SymbolType.function, SymbolType.class_]),
        )
        .limit(max_files)
        .all()
    )

    file_data = []
    for file in files:
        try:
            with open(file.file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            symbols = db.query(Symbol).filter_by(file_id=file.id).all()
            symbol_data = [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.type,
                    "start_line": s.line_start,
                    "end_line": s.line_end,
                }
                for s in symbols
                if hasattr(s.type, "value")
                and s.type.value in ["function", "method", "class"]
            ]

            file_data.append(
                {
                    "id": file.id,
                    "path": file.file_path,
                    "content": content,
                    "symbols": symbol_data,
                    "language": file.language or "python",
                }
            )
        except Exception:
            continue

    doc_service = AutoDocumentationService()
    documentation = await doc_service.document_repository(
        file_data, max_files=max_files
    )

    return {
        "repository_id": str(repository_id),
        "files_processed": len(file_data),
        "functions_documented": len(documentation),
        "documentation": documentation,
    }


@router.post("/metrics/{repository_id}/snapshot")
async def create_metrics_snapshot(
    repository_id: uuid.UUID, db: Session = Depends(get_db)
):
    """Create a new metrics snapshot"""

    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    tracker = MetricsTracker(db)
    snapshot = await tracker.create_snapshot(repository_id)

    return {
        "id": str(snapshot.id),
        "repository_id": str(repository_id),
        "quality_score": round(snapshot.quality_score or 0, 1),
        "metrics": {
            "files": snapshot.total_files,
            "lines": snapshot.total_lines,
            "symbols": snapshot.total_symbols,
            "avg_complexity": round(snapshot.avg_complexity or 0, 2),
            "duplications": snapshot.duplication_count,
            "code_smells": snapshot.code_smells_count,
            "vulnerabilities": snapshot.vulnerability_count,
        },
        "created_at": snapshot.created_at.isoformat(),
    }


@router.get("/metrics/{repository_id}/history")
async def get_metrics_history(
    repository_id: uuid.UUID, limit: int = 30, db: Session = Depends(get_db)
):
    """Get metrics history for a repository"""

    tracker = MetricsTracker(db)
    history = tracker.get_history(repository_id, limit=limit)

    return {
        "repository_id": str(repository_id),
        "snapshots": [
            {
                "id": str(s.id),
                "quality_score": round(s.quality_score or 0, 1),
                "total_files": s.total_files,
                "total_lines": s.total_lines,
                "avg_complexity": round(s.avg_complexity or 0, 2),
                "duplication_percentage": round(s.duplication_percentage or 0, 2),
                "code_smells_count": s.code_smells_count,
                "vulnerability_count": s.vulnerability_count,
                "created_at": s.created_at.isoformat(),
            }
            for s in history
        ],
    }


@router.post("/full-scan/{repository_id}")
async def run_full_analysis(
    repository_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Run complete analysis suite:
    - Code duplication detection
    - Code smell detection
    - Create metrics snapshot
    """

    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    background_tasks.add_task(scan_duplications_task, repository_id)
    background_tasks.add_task(scan_code_smells_task, repository_id)
    background_tasks.add_task(create_snapshot_task, repository_id)

    return {
        "status": "started",
        "message": "Full analysis started in background",
        "repository_id": str(repository_id),
        "tasks": ["duplications", "code_smells", "metrics_snapshot"],
    }


async def create_snapshot_task(repository_id: uuid.UUID):
    """Background task to create metrics snapshot"""
    db: Session = SessionLocal()
    try:
        tracker = MetricsTracker(db)
        await tracker.create_snapshot(repository_id)
    except Exception as e:
        print(f"create_snapshot_task failed: {e}")
    finally:
        db.close()
