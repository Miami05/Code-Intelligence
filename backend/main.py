from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import repositories_router, upload_router

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


@app.get("/")
def root():
    """API information"""
    return {
        "message": settings.api_tittle,
        "version": settings.api_version,
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
    }
