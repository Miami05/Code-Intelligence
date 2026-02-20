"""
Celery task for parsing individual large files with batched DB inserts.
Used as a complement to parse_repository.py for 100k+ line files.
"""

import asyncio
from typing import Dict, List

from celery_app import celery_app
from database import SessionLocal
from models.symbol import Symbol, SymbolType
from parsers.streaming_parsers import StreamingParser

streaming_parsers = StreamingParser()


@celery_app.task(bind=True, name="tasks.parse_file")
def parse_file_task(self, file_id: int, file_path: str, repository_id: str):
    """
    Parse a single file with batched DB inserts.
    Used for large files (100k+ lines) identified during repository parsing.
    """
    stats = streaming_parsers.get_file_stats(file_path)
    print(
        f"📄 Parsing file: {file_path} "
        f"({stats.get('line_count', '?')} lines, "
        f"{stats.get('size_bytes', 0) // 1024} KB)"
    )
    total_symbols = 0
    for batch in streaming_parsers.parse_in_batches(file_path, repository_id):
        _batch_insert_symbols(file_id, batch)
        total_symbols += len(batch)
        print(f"  ✓ Inserted batch of {len(batch)} symbols (total: {total_symbols})")
    print(f"✅ Finished parsing {file_path}: {total_symbols} symbols")
    return {
        "file_id": file_id,
        "file_path": file_path,
        "symbols_extracted": total_symbols,
        "status": "completed",
    }


def _batch_insert_symbols(file_id: int, symbols: List[Dict]):
    """Insert a batch of symbols into the database efficiently."""
    db = SessionLocal()
    try:
        for sym in symbols:
            raw_type = (sym.get("type") or "").strip()
            if raw_type == "class":
                raw_type = "class_"
            if raw_type not in SymbolType.__members__:
                raw_type = "function"
            symbol_record = Symbol(
                file_id=file_id,
                name=sym.get("name", "unknown"),
                type=SymbolType[raw_type],
                line_start=sym.get("line_start", 1),
                line_end=sym.get("line_end"),
                signature=sym.get("signature"),
            )
            db.add(symbol_record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Batch insert failed: {e}")
    finally:
        db.close()
