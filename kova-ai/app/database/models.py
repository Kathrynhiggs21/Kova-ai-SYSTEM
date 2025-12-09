from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    Boolean,
    JSON,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from .session import Base
from sqlalchemy import func
import enum


class RepositoryStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SYNCING = "syncing"
    ERROR = "error"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(Base):
    __tablename__ = "repository"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=False, unique=True, index=True)
    url = Column(Text, nullable=False)
    description = Column(Text)
    default_branch = Column(String(100), default="main")
    status = Column(Enum(RepositoryStatus), default=RepositoryStatus.ACTIVE)
    is_enabled = Column(Boolean, default=True)
    repo_type = Column(String(50))  # core, service, frontend, experimental
    sync_priority = Column(Integer, default=3)
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_synced_at = Column(TIMESTAMP)

    # Relationships
    errors = relationship("Error", back_populates="repository")
    sync_logs = relationship("SyncLog", back_populates="repository")
    webhooks = relationship("WebhookEvent", back_populates="repository")


class Error(Base):
    __tablename__ = "error"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=True)
    error_type = Column(String(100), index=True)
    severity = Column(String(50))  # critical, error, warning, info
    message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    file_path = Column(String(500))
    line_number = Column(Integer)
    context = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    repository = relationship("Repository", back_populates="errors")


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=False)
    sync_type = Column(String(50))  # manual, automatic, scheduled
    status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)
    duration_seconds = Column(Integer)
    items_synced = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    details = Column(JSON)
    claude_analysis = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    repository = relationship("Repository", back_populates="sync_logs")


class WebhookEvent(Base):
    __tablename__ = "webhook_event"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=True)
    event_type = Column(
        String(100), nullable=False, index=True
    )  # push, pull_request, issues
    event_action = Column(String(100))  # opened, closed, synchronize
    github_delivery_id = Column(String(255), unique=True)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(TIMESTAMP)
    response = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    repository = relationship("Repository", back_populates="webhooks")


class ClaudeInteraction(Base):
    __tablename__ = "claude_interaction"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=True)
    interaction_type = Column(String(100))  # sync, analyze, command
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    model = Column(String(100))
    tokens_used = Column(Integer)
    duration_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    repository = relationship("Repository")


class Artifact(Base):
    __tablename__ = "artifact"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    artifact_type = Column(String(100))  # code, document, diagram, config
    content = Column(Text, nullable=False)
    language = Column(String(50))
    repository_id = Column(Integer, ForeignKey("repository.id"), nullable=True)
    file_path = Column(String(500))
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_by = Column(String(255))  # claude, user, system
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    repository = relationship("Repository")
