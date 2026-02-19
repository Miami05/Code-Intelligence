from config import settings
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    ai_assistant_router,
    analysis_router,
    chat_router,
    recommendations_router,
    repositories_router,
    upload_router,
)
from routers.call_graph import router as call_graph_router
from routers.github import router as github_router
from routers.search import router as search_router
from routers.security import router as security_router
from sqlalchemy import text

app = FastAPI(
    title=settings.api_tittle,
    description="AI-powered code repository analysis with GitHub integration",
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
app.include_router(recommendations_router)
app.include_router(github_router)
app.include_router(call_graph_router)
app.include_router(security_router)
app.include_router(ai_assistant_router)
app.include_router(chat_router)
app.include_router(analysis_router)


@app.on_event("startup")
def startup():
    """Ensure database tables exist."""
    if settings.enable_embeddings and engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    """API information."""
    return {
        "message": settings.api_tittle,
        "version": settings.api_version,
        "features": [
            "Code parsing",
            "Symbol extraction",
            "Semantic search",
            "Vector embeddings",
            "GitHub integration",
            "Call graph analysis",
            "Dead code detection",
            "Dependency tracking",
            "Security scanning",
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
        "api_title": settings.api_tittle,
        "api_version": settings.api_version,
        "upload_dir": settings.upload_dir,
        "max_upload_size_mb": settings.max_upload_size_mb,
        "allowed_extensions": settings.allowed_extension,
        "task_time_limit": settings.task_time_limit,
        "embeddings_enabled": settings.enable_embeddings,
        "openai_model": (
            settings.openai_model if settings.openai_api_key else "not configured"
        ),
        "embedding_dimensions": settings.embedding_dimensions,
    }
