from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, DECIMAL, ForeignKey, func
from sqlalchemy.orm import relationship
from .session import Base

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    errors = relationship("Error", back_populates="repository")

class Error(Base):
    __tablename__ = "errors"
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    message = Column(Text, nullable=False)
    error_type = Column(String(100))
    file_path = Column(Text)
    line_number = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="errors")
    auto_fixes = relationship("AutoFix", back_populates="error")

class AutoFix(Base):
    __tablename__ = "auto_fixes"
    id = Column(Integer, primary_key=True, index=True)
    error_id = Column(Integer, ForeignKey("errors.id"))
    fix_description = Column(Text, nullable=False)
    fix_code = Column(Text)
    confidence_score = Column(DECIMAL(3,2))
    applied = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    error = relationship("Error", back_populates="auto_fixes")

class AICommand(Base):
    __tablename__ = "ai_commands"
    id = Column(Integer, primary_key=True, index=True)
    command = Column(Text, nullable=False)
    response = Column(Text)
    status = Column(String(50), default="pending", index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    completed_at = Column(TIMESTAMP)
