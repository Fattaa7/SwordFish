from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base



class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)

    query_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="queries")
    workspaces = relationship("Workspace", back_populates="queries")
    conversation = relationship("Conversation", back_populates="queries")
    answers = relationship("Answer", back_populates="query")
