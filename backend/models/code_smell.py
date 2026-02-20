"""Code Smell Detection Models"""

import enum
import uuid
from datetime import datetime
from pathlib import Path

from database import Base
from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLENUM
from sqlalchemy import ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SmellType(str, enum.Enum):
    """Types of code smells"""

    LONG_METHOD = "long_method"
    GOD_CLASS = "god_class"
    FEATURE_ENVY = "feature_envy"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    MISSING_DOCSTRING = "missing_docstring"  # Sprint 9: Missing documentation


class SmellSeverity(str, enum.Enum):
    """Severity levels for code smells"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CodeSmell(Base):
    """Stores detected code smells"""

    __tablename__ = "code_smells"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE")
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True
    )
    symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # native_enum=True with explicit names matches the existing PostgreSQL ENUM types in DB
    smell_type: Mapped[SmellType] = mapped_column(
        SQLENUM(SmellType, name="smelltype", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    severity: Mapped[SmellSeverity] = mapped_column(
        SQLENUM(SmellSeverity, name="smellseverity", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, nullable=True)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    metric_value: Mapped[int] = mapped_column(Integer, nullable=True)
    metric_threshold: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    repository = relationship("Repository", backref="code_smells")
    file = relationship("File", backref="code_smells")
    symbol = relationship("Symbol", backref="code_smells")

    __table_args__ = (
        Index("idx_code_smells_repo", "repository_id"),
        Index("idx_code_smells_file_id", "file_id"),
        Index("idx_code_smells_severity", "severity"),
        Index("idx_code_smells_type", "smell_type"),
    )

    def __repr__(self) -> str:
        return f"<CodeSmell(id={self.id}, type={self.smell_type.value}, severity={self.severity.value})>"
