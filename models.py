from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .session import Base

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    url = Column(String(500))
    owner = Column(String(255))
    health_score = Column(Float, default=100.0)
    last_scan = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class Error(Base):
    __tablename__ = "errors"
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer)
    file_path = Column(String(500))
    line_number = Column(Integer)
    error_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    is_fixed = Column(Boolean, default=False)
    detected_at = Column(DateTime, server_default=func.now())
