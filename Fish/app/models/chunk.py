from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    index = Column(Integer, nullable=False)  # Position of the chunk within the document
    text = Column(Text, nullable=False)  # The actual chunk text
    embedding = Column(Vector(1536))  # dimension size
    token_count = Column(Integer, nullable=True)  # Number of tokens in the chunk
    page_number = Column(Integer, nullable=True)  # Page number in the document

    meta = Column(JSONB, nullable=True)  # JSONB column for storing metadata


    document = relationship("Document", back_populates="chunks")

