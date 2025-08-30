from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspaces = relationship("Workspace", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")
    queries = relationship("Query", back_populates="users")
