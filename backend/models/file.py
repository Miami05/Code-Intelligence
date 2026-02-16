import uuid

from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class File(Base):
    """File table - stores individual source code files"""

    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(String(1000), nullable=False)
    language = Column(String(50), nullable=False)
    line_count = Column(Integer, default=0)
    source = Column(Text, nullable=True)  # Store file content for call graph analysis
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    symbols = relationship(
        "Symbol", back_populates="file", cascade="all, delete-orphan"
    )
    repository = relationship("Repository", back_populates="files")

    def __repr__(self) -> str:
        return f"<File(id={self.id}, path={self.file_path}, language={self.language}"
