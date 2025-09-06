from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from .session import Base

class Repository(Base):
    __tablename__ = "repository"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)

class Error(Base):
    __tablename__ = "error"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
