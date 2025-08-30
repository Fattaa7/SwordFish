from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_private = Column(Boolean, default=True)

    # relationships
    workspace = relationship("Workspace", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    queries = relationship("Query", back_populates="conversation", cascade="all, delete")
    answers = relationship("Answer", back_populates="conversation", cascade="all, delete")
