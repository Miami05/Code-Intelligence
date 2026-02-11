"""
Code recommendations and quality metrics API.
"""

from typing import Optional
from uuid import UUID

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Embedding, File, Symbol, embedding
from models.symbol import SymbolType
from sqlalchemy import asc, case, func, join, label
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions
from sqlalchemy.sql.operators import isnot

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/similiar/{symbol_id}")
async def find_similiar_code(
    symbol_id: UUID,
    limit: int = 10,
    threshold: float = 0.7,
    db: Session = Depends(get_db),
):
    """
    Find similar code implementations based on embeddings.
    Uses cosine distance (pgvector). Similarity = 1 - distance.
    threshold is similarity threshold (0..1). Example: 0.7 means "at least 70% similar".
    """
    target_emb = db.query(Embedding).filter(Embedding.symbol_id == symbol_id).first()
    if not target_emb:
        raise HTTPException(status_code=404, detail="Symbol or embeddings not found")
    distance_expr = Embedding.embedding.cosine_distance(target_emb.embedding)
    distance_cutoff = 1 - float(threshold)
    rows = db.query(
        Symbol,
        Embedding,
        File,
        distance_expr.label("distance")
        .join(Embedding, Symbol.id == Embedding.symbol_id)
        .join(File, Symbol.file_id == File.id)
        .filter(Symbol.id != symbol_id)
        .filter(distance_expr <= distance_cutoff)
        .order_by(distance_expr.asc())
        .limit(limit)
        .all(),
    )
    result = []
    for symbol, embedding, file, distance in rows:
        similarity = 1.0 - float(distance) if distance is not None else None
        result.append(
            {
                "symbol_id": str(symbol.id),
                "name": symbol.name,
                "type": symbol.type.value,
                "signature": symbol.signature or "",
                "file_path": file.file_path,
                "repository_id": str(file.repository_id),
                "language": file.language,
                "lines": f"{symbol.line_start}-{symbol.line_end}",
                "cyclomatic_complexity": symbol.cyclomatic_complexity,
                "maintainability_index": symbol.maintainability_index,
                "similarity": round(similarity, 4) if similarity is not None else None,
            }
        )

    return result


@router.get("/complex-functions")
async def get_complex_functions(
    min_complexity: int = 20,
    limit: int = 50,
    repository_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """Get most complex functions for refactoring candidates."""
    query = (
        db.query(Symbol, File)
        .join(File, Symbol.file_id == File.id)
        .filter(Symbol.cyclomatic_complexity.isnot(None))
        .filter(Symbol.cyclomatic_complexity >= min_complexity)
        .filter(Symbol.type == SymbolType.function)
    )
    if repository_id:
        query = query.filter(File.repository_id == repository_id)
    complex_symbols = (
        query.order_by(Symbol.cyclomatic_complexity.desc()).limit(limit).all()
    )
    return [
        {
            "symbol_id": str(s.id),
            "name": s.name,
            "complexity": s.cyclomatic_complexity,
            "maintainability": s.maintainability_index,
            "lines": s.lines_of_code,
            "file_path": f.file_path,
            "signature": s.signature,
        }
        for s, f in complex_symbols
    ]


@router.get("/quality-dashboard")
async def quality_dashboard(
    repository_id: Optional[UUID] = None, db: Session = Depends(get_db)
):
    """Overall code quality dashboard metrics (computed in SQL)."""
    base = db.query(Symbol).filter(Symbol.cyclomatic_complexity.isnot(None))
    if repository_id:
        base = base.join(File, Symbol.file_id == File.id).filter(
            File.repository_id == repository_id
        )
    subq = base.subquery()
    total_symbols = db.query(func.count()).select_from(subq).scalar() or 0
    if total_symbols == 0:
        return {"message": "No quality metrics available"}
    avg_complexity = db.query(func.avg(subq.c.cyclomatic_complexity)).scalar() or 0.0
    avg_maintainability = (
        db.query(func.avg(subq.c.maintainability_index)).scalar() or 0.0
    )
    high_complexity_count = (
        db.query(func.count())
        .select_from(subq)
        .filter(subq.c.cyclomatic_complexity > 20)
        .scalar()
        or 0
    )
    low_maintainability_count = (
        db.query(func.count)
        .select_from(subq)
        .filter(subq.c.maintainability_index < 65)
        .scalar()
        or 0
    )
    complexity_dist = db.query(
        func.sum(case((subq.c.cyclomatic_complexity <= 10, 1), else_=0)).label(
            "simple"
        ),
        func.sum(
            case(
                (
                    func.and_(
                        subq.c.cyclomatic_complexity >= 11,
                        subq.c.cyclomatic_complexity <= 20,
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("moderate"),
        func.sum(
            case(
                (
                    func.and_(
                        subq.c.cyclomatic_complexity >= 21,
                        subq.c.cyclomatic_complexity <= 50,
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("complex"),
        func.sum(case((subq.c.cyclomatic_complexity > 50, 1), else_=0)).label(
            "very complex"
        ),
    ).one()
    maintainability_dist = db.query(
        func.sum(case((subq.c.maintainability_index >= 85, 1), else_=0)).label(
            "excellent"
        ),
        func.sum(
            case(
                (
                    func.and_(
                        subq.c.maintainability_index >= 65,
                        subq.c.maintainability_index < 85,
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("good"),
        func.sum(
            case(
                (
                    func.and_(
                        subq.c.maintainability_index >= 50,
                        subq.c.maintainability_index < 65,
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("fair"),
        func.sum(case((subq.c.maintainability_index < 50, 1), else_=0)).label("poor"),
    ).one()
    return {
        "total_symbols": int(total_symbols),
        "average_complexity": round(float(avg_complexity), 2),
        "average_maintainability": round(float(avg_maintainability), 2),
        "high_complexity_count": int(high_complexity_count),
        "low_maintainability_count": int(low_maintainability_count),
        "complexity_distribution": {
            "simple (1-10)": int(complexity_dist.simple or 0),
            "moderate (11-20)": int(complexity_dist.moderate or 0),
            "complex (21-50)": int(complexity_dist.complex or 0),
            "very_complex (50+)": int(complexity_dist.very_complex or 0),
        },
        "maintainability_distribution": {
            "excellent (85-100)": int(maintainability_dist.excellent or 0),
            "good (65-84)": int(maintainability_dist.good or 0),
            "fair (50-64)": int(maintainability_dist.fair or 0),
            "poor (<50)": int(maintainability_dist.poor or 0),
        },
    }


@router.get("/low-maintainability")
async def get_low_maintainability(
    max_index: float = 65.0,
    limit: int = 50,
    repository_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """Get functions with low maintainability index."""
    query = (
        db.query(Symbol, File)
        .join(File, Symbol.file_id == File.id)
        .filter(Symbol.maintainability_index.isnot(None))
        .filter(Symbol.maintainability_index <= max_index)
        .filter(Symbol.type == SymbolType.function)
        .order_by(Symbol.maintainability_index.asc())
        .limit(limit)
    )
    if repository_id:
        query = query.filter(File.repository_id == repository_id)
    rows = query.all()
    return [
        {
            "symbol_id": str(s.id),
            "name": s.name,
            "maintainability": s.maintainability_index,
            "complexity": s.cyclomatic_complexity,
            "lines": s.lines_of_code,
            "file_path": f.file_path,
            "signature": s.signature,
        }
        for s, f in rows
    ]
