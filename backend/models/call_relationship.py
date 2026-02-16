"""
Call relationship model for Sprint 7
Stores function call relationships for call graph analysis
"""

from database import Base
from models.base import TimestampMixin
from sqlalchemy import Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship


class CallRelationship(Base, TimestampMixin):
    """
    Represents a function call relationship.
    Stores who calls whom (caller -> callee).
    """

    __tablename__ = "call_relationship"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(String, ForeignKey("repository.id"), nullable=False)

    caller_name = Column(String, nullable=False)
    caller_file = Column(String, nullable=True)
    caller_symbol_id = Column(Integer, ForeignKey("code_symbol.id"), nullable=True)

    callee_name = Column(String, nullable=False)
    callee_file = Column(String, nullable=True)
    callee_symbol_id = Column(Integer, ForeignKey("code_symbol.id"), nullable=True)
    call_file = Column(String, nullable=False)
    call_line = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    is_external = Column(Integer, default=0)
    repository = relationship("Repository", back_populates="call_relationships")
    caller_symbol = relationship("CodeSymbol", foreign_keys=[caller_symbol_id])
    callee_symbol = relationship("CodeSymbol", foreign_keys=[callee_symbol_id])
    __table_args__ = (
        Index("idx_caller", "repository_id", "caller_name"),
        Index("idx_callee", "repository_id", "callee_name"),
        Index("idx_call_location", "repository_id", "call_file", "call_line"),
        Index("idx_caller_symbol", "caller_symbol_id"),
        Index("idx_callee_symbol", "callee_symbol_id"),
        UniqueConstraint(
            "repository_id",
            "caller_name",
            "callee_name",
            "call_file",
            "call_line",
            name="uq_call_relationship",
        ),
    )

    def __repr__(self):
        return f"<CallRelationship {self.caller_name} -> {self.callee_name} @ {self.call_file}:{self.call_line}>"
