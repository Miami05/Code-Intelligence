"""
Call relationship model for function call tracking.
"""

from database import Base
from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship


class CallRelationship(Base):
    """
    Tracks function call relationships (who calls whom).
    """

    __tablename__ = "call_relationship"
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(
        String, ForeignKey("repositories.id"), nullable=False, index=True
    )
    caller_symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    caller_name = Column(String, nullable=False)
    caller_file = Column(String, nullable=False)
    callee_name = Column(String, nullable=False)
    callee_file = Column(String, nullable=True)
    callee_symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=True)
    call_line = Column(Integer, nullable=False)
    is_external = Column(Integer, default=0)
    caller_symbol = relationship("Symbol", foreign_keys=[caller_symbol_id])
    callee_symbol = relationship("Symbol", foreign_keys=[callee_symbol_id])
    __table_args__ = (
        Index("idx_caller_symbol", "caller_symbol_id"),
        Index("idx_caller_symbol", "calle_symbol_id"),
        Index("idx_repository_calls", "repository_id"),
    )

    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "caller_name": self.caller_name,
            "caller_file": self.caller_file,
            "caller_symbol_id": self.caller_symbol_id,
            "callee_name": self.callee_name,
            "callee_file": self.callee_file,
            "callee_symbol_id": self.callee_symbol_id,
            "call_line": self.call_line,
            "is_external": bool(self.is_external),
        }
