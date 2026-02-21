import uuid
from datetime import datetime
from typing import Any, Optional

from database import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class CICDRun(Base):
    __tablename__ = "cicd_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pr_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    triggered_by: Mapped[str] = mapped_column(
        String(50), default="manual", server_default="manual"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending"
    )
    quality_gate_passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    quality_gate_details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    report_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    repository = relationship("Repository", backref="cicd_runs")
