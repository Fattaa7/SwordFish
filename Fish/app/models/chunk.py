from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=True)             # Chunk title
    index = Column(Integer, nullable=False)           # Position of the chunk within the document
    text = Column(Text, nullable=False)               # The actual chunk text
    embedding = Column(Vector(1536))                  # Vector embedding
    token_count = Column(Integer, nullable=True)
    page_number = Column(Integer, nullable=True)     # Page number in the document
    meta = Column(JSONB, nullable=True)              # Metadata for the chunk

    # Source info for frontend reference
    source_uri = Column(String, nullable=True)       # Storage path or URL to the source

    document = relationship("Document", back_populates="chunks")
