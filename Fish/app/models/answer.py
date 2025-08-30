from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base




class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    sources = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    query = relationship("Query", back_populates="answers")
    conversation = relationship("Conversation", back_populates="answers")
