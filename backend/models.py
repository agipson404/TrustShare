from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    encryption_key = Column(String)

class FileShare(Base):
    __tablename__ = "file_shares"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    shared_with_id = Column(Integer, ForeignKey("users.id"))
    shared_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])
    shared_with = relationship("User", foreign_keys=[shared_with_id])
