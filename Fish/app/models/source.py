from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class SourceStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class SourceType(enum.Enum):
    FILE = "file"
    URL = "url"


class MimeType(enum.Enum):
    TEXT = "text/plain"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    HTML = "text/html"
    CSV = "text/csv"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    type = Column(Enum(SourceType), nullable=False)
    status = Column(Enum(SourceStatus), nullable=False, default=SourceStatus.UPLOADED)

    url = Column(String, nullable=True)             # required if type = URL
    storage_path = Column(String, nullable=True)    # required if type = FILE

    mime_type = Column(Enum(MimeType), nullable=True)  # Updated to use MimeType enum
    checksum = Column(String(64), nullable=True)       # SHA256, MD5, etc.
    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # __table_args__ = (
    #     CheckConstraint(
    #         f"(type = '{SourceType.URL.value}' AND url IS NOT NULL) OR (type = '{SourceType.FILE.value}' AND storage_path IS NOT NULL)",
    #         name="check_source_path_or_url"
    #     ),
    # )

    workspace = relationship("Workspace", back_populates="sources")
    documents = relationship("Document", back_populates="source")
