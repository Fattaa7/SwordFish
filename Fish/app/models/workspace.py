from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base



class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    plan = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="workspaces")
    sources = relationship("Source", back_populates="workspace")
    conversations = relationship("Conversation", back_populates="workspace")
    queries = relationship("Query", back_populates="workspaces")
