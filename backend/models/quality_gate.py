import uuid

from database import Base
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, null
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class QualityGate(Base):
    __tablename__ = "quality_gates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    max_complexity = Column(Integer, default=10, server_default="10")
    max_code_smells = Column(Integer, default=20, server_default="20")
    max_critical_smells = Column(Integer, default=0, server_default="0")
    max_vulnerabilities = Column(Integer, default=5, server_default="5")
    max_critical_vulnerabilities = Column(Integer, default=0, server_default="0")
    min_quality_score = Column(Float, default=70.0, server_default="70.0")
    max_duplication_percentage = Column(Float, default=10.0, server_default="10.0")
    block_on_failure = Column(Boolean, default=True, server_default="true")
    repository = relationship("Repository", backref="quality_gates")
