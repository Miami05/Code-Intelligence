from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation and type safety.
    """

    # --- Database ---
    database_url: str = "postgresql://codeuser:codepass123@localhost:5432/codedb"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    # --- Redis/Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # --- Uploads ---
    upload_dir: str = "/tmp/upload"
    max_upload_size_mb: int = 100
    allowed_extension: list[str] = [".zip"]

    # --- Tasks ---
    task_time_limit: int = 300
    task_soft_time_limit: int = 270

    # --- API ---
    api_tittle: str = "Code Intelligence Platform"
    api_version: str = "0.2.0"
    api_debug: bool = True
    cors_origins: list[str] = ["*"]

    # --- OpenAI (Sprint 3) ---
    openai_api_key: str = ""
    openai_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # --- GitHub (Sprint 6) ---
    github_token: Optional[str] = None

    # --- Vector Search ---
    enable_embeddings: bool = True
    similarity_threshold: float = 0.7
    max_search_results: int = 20

    # --- AI & RAG (Sprint 12) ---
    ai_rate_limit: int = 60
    rag_similarity_threshold: float = 0.6
    rag_max_context_tokens: int = 4000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = Settings()
