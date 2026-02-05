from celery_app import celery_app
from config import settings
from database import SessionLocal
from models import Embedding, File, Symbol
from utils.embeddings import generate_embeddings_batch, prepare_symbol_for_embedding


@celery_app.task(
    bind=True, name="tasks.generate_embeddings.generate_embeddings_for_repository"
)
def generate_embeddings_for_repository(self, repository_id: str):
    """
    Generate embeddings for all symbols in a repository.

    Args:
        repository_id: UUID of the repository

    Returns:
        Dictionary with statistics
    """
    if not settings.enable_embeddings:
        return {"status": "skipped", "reason": "Embeddings disabled in settings"}
    if not settings.openai_api_key:
        return {"status": "skipped", "reason": "OpenAI API key not configured"}
    db = SessionLocal()
    try:
        print(f"🤖 Generating embeddings for repository: {repository_id}")
        symbols = (
            db.query(Symbol)
            .join(File)
            .filter(File.repository_id == repository_id)
            .all()
        )
        if not symbols:
            print(f"  ✓ No symbols found")
            return {
                "repository_id": repository_id,
                "symbols_processed": 0,
                "status": "completed",
            }
        existing_embeddings = (
            db.query(Embedding.symbol_id)
            .filter(Embedding.symbol_id.in_([s.id for s in symbols]))
            .all()
        )
        existing_ids = {e.symbol_id for e in existing_embeddings}
        symbols = [s for s in symbols if s.id not in existing_ids]
        if not symbols:
            print(f"  ✓ No new symbols to embed")
            return {
                "repository_id": repository_id,
                "symbols_processed": 0,
                "status": "completed",
            }
        print(f"  📝 Found {len(symbols)} symbols to embed")
        texts = []
        for symbol in symbols:
            text = prepare_symbol_for_embedding(
                symbol.name, symbol.type.value, symbol.signature
            )
            texts.append(text)
        print(f"  🔄 Calling OpenAI API...")
        embeddings = generate_embeddings_batch(texts)
        print(f"  💾 Saving embeddings to database...")
        for symbol, embedding in zip(symbols, embeddings):
            embedding_records = Embedding(
                symbol_id=symbol.id,
                embedding=embedding,
                model=settings.openai_model,
                dimensions=settings.embedding_dimensions,
            )
            db.add(embedding_records)
        db.commit()
        print(f"  ✅ Generated {len(embeddings)} embeddings")
        return {
            "repository_id": repository_id,
            "symbols_processed": len(embeddings),
            "model": settings.openai_model,
            "status": "completed",
        }
    except Exception as e:
        print(f"  ❌ Error generating embeddings: {e}")
        db.rollback()
        raise
    finally:
        db.close()
