from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from config import settings
from database import Base, engine
from routers import repositories_router, upload_router
from routers.search import router as search_router

app = FastAPI(
    title=settings.api_tittle,
    description="AI-powered code repository analysis",
    version=settings.api_version,
    debug=settings.api_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(repositories_router)
app.include_router(search_router)


@app.on_event("startup")
def startup():
    """Ensure database tables exist."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    """API information."""
    return {
        "message": settings.api_title,
        "version": settings.api_version,
        "features": [
            "Code parsing",
            "Symbol extraction",
            "Semantic search",
            "Vector embeddings",
        ],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": settings.api_tittle.lower().replace(" ", "-"),
        "version": settings.api_version,
        "embedding_enabled": settings.enable_embeddings,
    }


@app.get("/config")
def get_config():
    """Get non-sensitive config (for debugging)."""
    return {
        "api_title": settings.api_title,
        "api_version": settings.api_version,
        "upload_dir": settings.upload_dir,
        "max_upload_size_mb": settings.max_upload_size_mb,
        "allowed_extensions": settings.allowed_extensions,
        "task_time_limit": settings.task_time_limit,
        "embeddings_enabled": settings.enable_embeddings,
        "openai_model": (
            settings.openai_model if settings.openai_api_key else "not configured"
        ),
        "embedding_dimensions": settings.embedding_dimensions,
    }
