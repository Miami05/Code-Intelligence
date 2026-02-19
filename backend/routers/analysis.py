"""Advanced Analysis Endpoints - Sprint 9"""

import uuid
from re import findall
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
    symbol,
)
from models.code_smell import SmellType
from services.auto_documentation import AutoDocumentationService
from services.code_smell_detector import CodeSmellDetector
from services.duplication_scanner import DuplicateScanner
from services.metrics_tracker import MetricsTracker
from sqlalchemy import delete, func
from sqlalchemy.orm import Session, exc, joinedload
from sqlalchemy.sql.operators import op

router = APIRouter(prefix="/api/analysis", tags=["Advanced Analysis"])


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
    repo = db.query(Repository).filter_by(repository_id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
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
        files = db.query(File).filter_by(repository_id=repository_id).all()
        file_data = []
        for file in files:
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
                print(f"Error reading file {file.path}: {e}")
                continue
        scanner = DuplicateScanner()
        duplications = scanner.scan_repository(file_data)
        db.execute(
            delete(CodeDuplication).where(
                CodeDuplication.repository_id == repository_id
            )
        )
        db.commit()
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
    file_ids = set()
    for dup in duplications:
        file_ids.add(dup.file1_id)
        file_ids.add(dup.file2_id)
    files = db.query(File).filter(File.id.in_(file_ids)).all()
    file_map = {f.id: f for f in files}
    results = []
    for dup in duplications:
        file1 = file_map.get(dup.file1_id)
        file2 = file_map.get(dup.file2_id)
        results.append(
            {
                "id": str(dup.id),
                "file1": {
                    "id": str(dup.file1_id),
                    "path": file1.path if file1 else "Unknown",
                    "start_line": dup.file1_start_line,
                    "end_line": dup.file1_end_line,
                },
                "file2": {
                    "id": str(dup.file2_id),
                    "path": file2.path if file2 else "Unknown",
                    "start_line": dup.file2_start_line,
                    "end_line": dup.file2_end_line,
                },
                "similarity": round((dup.similarity_score or 0.0) * 100, 1),
                "duplicate_lines": dup.duplicate_lines or 0,
                "duplicate_tokens": dup.duplicate_tokens or 0,
                "code_snippet": (dup.code_snippet or "")[:200],
            }
        )
    return {
        "repository_id": str(repository_id),
        "total_duplications": len(results),
        "duplications": results,
    }


@router.post("/code_smells/{repository_id}")
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
        if not files:
            raise HTTPException(status_code=404, detail="File not found")
        file_ids = [f.id for f in files]
        symbols = db.query(Symbol).filter(Symbol.file_id.in_(file_ids)).all()
        symbols_by_file: dict[uuid.UUID, list[Symbol]] = {}
        for s in symbols:
            symbols_by_file.setdefault(s.file_id, []).append(s)
        files_data = []
        for file in files:
            try:
                with open(file.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                syms = symbols_by_file.get(file.id, [])
                symbol_data = [
                    {
                        "id": s.id,
                        "name": s.name,
                        "type": (
                            s.type.value if hasattr(s.type, "value") else str(s.type)
                        ),
                        "start_line": s.line_start,
                        "end_line": s.line_end,
                    }
                    for s in syms
                ]
                files_data.append(
                    {
                        "id": file.id,
                        "path": file.path,
                        "content": content,
                        "symbols": symbol_data,
                    }
                )
            except Exception as e:
                print(f"Error reading file {file.path}: {e}")
                continue
        detector = CodeSmellDetector()
        smells = detector.scan_repository(files_data)
        db.execute(delete(CodeSmell).where(CodeSmell.repository_id == repository_id))
        db.commit()
        for smell in smells:
            db.add(
                CodeSmell(
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
            )
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
    """
    Get detected code smells for a repository.

    Query params:
      - severity: low|medium|high|critical
      - smell_type: long_method|god_class|feature_envy|large_class|long_parameter_list|duplicate_code|dead_code
    """
    query = (
        db.query(CodeSmell)
        .options(joinedload(CodeSmell.file), joinedload(CodeSmell.symbol))
        .filter(CodeSmell.repository_id == repository_id)
    )
    if severity:
        try:
            severity_enum = SmellSeverity(severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity '{severity}'. Use one of: {[e.value for e in SmellSeverity]}",
            )
        query = query.filter(CodeSmell.severity == severity_enum)
    if smell_type:
        try:
            smell_type_enum = SmellType(smell_type.lower())
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid smell_type '{smell_type}'. Use one of: {[e.value for e in SmellType]}",
            )
        query = query.filter(CodeSmell.smell_type == smell_type_enum)
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
                    "path": smell.file.path if smell.file else "Unknown",
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
                "created_at": smell.created_at.isoformat(),
            }
        )
    return {
        "repository_id": str(repository_id),
        "returned_smells": len(results),
        "limit": limit,
        "filters": {"severity": severity, "smell_type": smell_type},
        "code_smells": results,
    }


@router.post("/auto-documentation/{repository_id}")
async def generate_documents(
    repository_id: uuid.UUID, max_files: int = 10, db: Session = Depends(get_db)
):
    """Generate documentation for undocumented functions"""
    repo = db.query(Repository).filter_by(id=repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    file = db.query(File).filter_by(repository_id=repository_id).limit(max_files).all()
