import enum
import uuid
from datetime import datetime

from database import Base
from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RepoStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    upload_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    github_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, index=True
    )
    github_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_repo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_branch: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default="main"
    )
    github_stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    github_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[RepoStatus] = mapped_column(
        SQLEnum(RepoStatus), default=RepoStatus.pending, index=True
    )

    file_count: Mapped[int] = mapped_column(Integer, default=0)
    symbol_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    files = relationship(
        "File", back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Repository(id={self.id}, name={self.name}, status={self.status.value})>"
        )
