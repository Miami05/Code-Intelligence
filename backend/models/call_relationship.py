"""
Call relationship model for function call tracking.
"""

from database import Base
from sqlalchemy import Column, ForeignKey, Index, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CallRelationship(Base):
    """
    Tracks function call relationships (who calls whom).
    """

    __tablename__ = "call_relationships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    repository_id = Column(
        UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False, index=True
    )

    caller_symbol_id = Column(
        UUID(as_uuid=True), ForeignKey("symbols.id"), nullable=False, index=True
    )
    caller_name = Column(String, nullable=False)
    caller_file = Column(String, nullable=False)

    callee_name = Column(String, nullable=False)
    callee_file = Column(String, nullable=True)

    callee_symbol_id = Column(
        UUID(as_uuid=True), ForeignKey("symbols.id"), nullable=True, index=True
    )

    call_line = Column(Integer, nullable=False)
    is_external = Column(Boolean, default=False, nullable=False)

    caller_symbol = relationship("Symbol", foreign_keys=[caller_symbol_id])
    callee_symbol = relationship("Symbol", foreign_keys=[callee_symbol_id])

    __table_args__ = (
        Index("idx_caller_symbol_id", "caller_symbol_id"),
        Index("idx_callee_symbol_id", "callee_symbol_id"),
        Index("idx_repository_calls", "repository_id"),
        # Sprint 10: additional performance indexes
        Index("idx_callrel_caller_name", "caller_name"),
        Index("idx_callrel_callee_name", "callee_name"),
        Index("idx_callrel_is_external", "is_external"),
    )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "repository_id": str(self.repository_id),
            "caller_name": self.caller_name,
            "caller_file": self.caller_file,
            "caller_symbol_id": str(self.caller_symbol_id) if self.caller_symbol_id else None,
            "callee_name": self.callee_name,
            "callee_file": self.callee_file,
            "callee_symbol_id": str(self.callee_symbol_id) if self.callee_symbol_id else None,
            "call_line": self.call_line,
            "is_external": self.is_external,
        }
