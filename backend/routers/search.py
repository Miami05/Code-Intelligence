from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import Embedding, File, Symbol, embedding
from utils.embeddings import generate_embedding

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/semantic")
def semantic_search(
    query: str = Query(..., description="Natural language search query"),
    limit: int = Query(default=10, le=50),
    threshold: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    repository_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Semantic code search using natural language.

    Examples:
    - "find functions that handle user authentication"
    - "database connection classes"
    - "functions that calculate mathematical operations"
    """
    if not settings.enable_embeddings:
        raise HTTPException(status_code=503, detail="Embeddings not enabled")
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="Open API key not configured")
    print(f"🔍 Semantic search: '{query}'")
    query_embedding = generate_embedding(query)
    threshold = threshold or settings.similarity_threshold
    if repository_id:
        sql = text(
            """
            SELECT 
                s.id as symbol_id,
                s.name,
                s.type,
                s.signature,
                s.line_start,
                s.line_end,
                f.file_path,
                f.repository_id,
                1 - (e.embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM symbols s
            JOIN embeddings e ON s.id = e.symbol_id
            JOIN files f ON s.file_id = f.id
            WHERE 1 - (e.embedding <=> CAST(:query_embedding AS vector)) >= :threshold
              AND f.repository_id = :repository_id
            ORDER BY e.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """
        )
        params = {
            "query_embedding": query_embedding,
            "threshold": threshold,
            "limit": limit,
            "repository_id": repository_id,
        }
    else:
        sql = text(
            """
            SELECT 
                s.id as symbol_id,
                s.name,
                s.type,
                s.signature,
                s.line_start,
                s.line_end,
                f.file_path,
                f.repository_id,
                1 - (e.embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM symbols s
            JOIN embeddings e ON s.id = e.symbol_id
            JOIN files f ON s.file_id = f.id
            WHERE 1 - (e.embedding <=> CAST(:query_embedding AS vector)) >= :threshold
            ORDER BY e.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """
        )
        params = {
            "query_embedding": query_embedding,
            "threshold": threshold,
            "limit": limit,
        }
    results = db.execute(sql, params).fetchall()
    print(f"  ✓ Found {len(results)} results")
    return {
        "query": query,
        "threshold": threshold,
        "total_results": len(results),
        "results": [
            {
                "symbol_id": row.symbol_id,
                "name": row.name,
                "type": row.type,
                "signature": row.signature,
                "file_path": row.file_path,
                "repository_id": row.repository_id,
                "similarity": round(float(row.similarity), 4),
                "lines": (
                    f"{row.line_start}-{row.line_end}"
                    if row.line_end
                    else str(row.line_start)
                ),
            }
            for row in results
        ],
    }


@router.get("/similar/{symbol_id}")
def find_similiar_symbols(
    symbol_id: str,
    limit: int = Query(default=10, le=50),
    threshold: Optional[float] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Find symbols similar to a given symbol.

    Useful for:
    - Finding duplicate/similar code
    - Code recommendations
    - Refactoring candidates
    """
    if not settings.enable_embeddings:
        raise HTTPException(status_code=503, detail=f"Embeddings not enabled")
    embedding = db.query(Embedding).filter(Embedding.symbol_id == symbol_id).first()
    if not embedding:
        raise HTTPException(status_code=503, detail="Symbols embedding not found")
    symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
    if symbol is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    if threshold is None:
        threshold = settings.similarity_threshold
    sql = text(
        """
    SELECT 
            s.id as symbol_id,
            s.name,
            s.type,
            s.signature,
            s.line_start,
            s.line_end,
            f.file_path,
            f.repository_id,
            1 - (e.embedding <=> CAST(:query_embedding AS vector)) as similarity
        FROM symbols s
        JOIN embeddings e ON s.id = e.symbol_id
        JOIN files f ON s.file_id = f.id
        WHERE s.id != :exclude_id
          AND 1 - (e.embedding <=> CAST(:query_embedding AS vector)) >= :threshold
        ORDER BY e.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :limit
               """
    )
    results = db.execute(
        sql,
        {
            "query_embedding": embedding.embedding,
            "exclude_id": symbol_id,
            "threshold": threshold,
            "limit": limit,
        },
    ).fetchall()
    print(f"🔗 Found {len(results)} similar symbols to '{symbol.name}'")
    return {
        "source_symbol": {
            "id": symbol.id,
            "name": symbol.name,
            "type": symbol.type.value,
            "signature": symbol.signature,
        },
        "threshold": threshold,
        "total_results": len(results),
        "similar_symbols": [
            {
                "symbol_id": row.symbol_id,
                "name": row.name,
                "type": row.type,
                "signature": row.signature,
                "file_path": row.file_path,
                "repository_id": row.repository_id,
                "similarity": round(float(row.similarity), 4),
                "lines": (
                    f"{row.line_start}-{row.line_end}"
                    if row.line_end
                    else str(row.line_start)
                ),
            }
            for row in results
        ],
    }


@router.get("/stats")
def embedding_stats(db: Session = Depends(get_db)):
    """Get statistics about embeddings in the system."""
    total_symbols = db.query(func.count(Symbol.id)).scalar()
    total_embeddings = db.query(func.count(Embedding.id)).scalar()
    return {
        "total_symbols": total_symbols,
        "total_embeddings": total_embeddings,
        "coverage": (
            round(total_embeddings / total_symbols * 100, 2) if total_symbols > 0 else 0
        ),
        "model": settings.openai_model,
        "dimensions": settings.embedding_dimensions,
        "enabled": settings.enable_embeddings,
    }
