import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.repository import Repository
from models.symbol import Symbol


class File(Base):
    """File table - stores individual source code files"""

    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=0)

    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    symbols: Mapped[List["Symbol"]] = relationship(
        "Symbol",
        back_populates="file",
        cascade="all, delete-orphan",
    )
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="files",
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, path={self.file_path}, language={self.language})>"
