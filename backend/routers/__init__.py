from .ai_assistant import router as ai_assistant_router
from .analysis import router as analysis_router
from .chat import router as chat_router
from .github import router as github_router
from .recommendations import router as recommendations_router
from .repositories import router as repositories_router
from .security import router as security_router
from .upload import router as upload_router

__all__ = [
    "upload_router",
    "repositories_router",
    "repositories_router",
    "recommendations_router",
    "github_router",
    "security_router",
    "ai_assistant_router",
    "chat_router",
    "analysis_router",
]
