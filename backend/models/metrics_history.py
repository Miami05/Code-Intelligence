"""Metrics History Models - Track code quality over time"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, false, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MetricsSnapshot(Base):
    """Historical snapshot of repository metrics"""

    __tablename__ = "metrics_snapshots"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
    )
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    total_symbols: Mapped[int] = mapped_column(Integer, default=0)
    avg_complexity: Mapped[float] = mapped_column(Float, default=0.0)
    max_complexity: Mapped[int] = mapped_column(Integer, default=0)
    high_complexity_count: Mapped[int] = mapped_column(Integer, default=0)
    duplication_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_lines: Mapped[int] = mapped_column(Integer, default=0)
    duplication_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    code_smells_count: Mapped[int] = mapped_column(Integer, default=0)
    criticals_smells: Mapped[int] = mapped_column(Integer, default=0)
    high_smells: Mapped[int] = mapped_column(Integer, default=0)
    medium_smells: Mapped[int] = mapped_column(Integer, default=0)
    low_smells: Mapped[int] = mapped_column(Integer, default=0)
    vulnerability_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_vulnerability: Mapped[int] = mapped_column(Integer, default=0)
    high_vulnerabilities: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    repository = relationship("Repository", backref="metrics_history")

    def __repr__(self) -> str:
        return f"<MetricsSnapshot(id={self.id}, repo={self.repository_id}, score={self.quality_score:.1f})>"
