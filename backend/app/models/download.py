from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum as PyEnum
from ..db_base import Base

class DownloadStatus(PyEnum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class DownloadPriority(PyEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class Download(Base):
    """Download queue item"""
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    source = Column(String(50), nullable=False)  # awmf, who, springer, etc.
    source_id = Column(String(100), nullable=False)  # Unique ID from source
    url = Column(String(512), nullable=False)
    file_path = Column(String(512), nullable=True)  # Target file path
    file_name = Column(String(255), nullable=True)

    # Status
    status = Column(Enum(DownloadStatus), default=DownloadStatus.PENDING, nullable=False)
    priority = Column(Enum(DownloadPriority), default=DownloadPriority.NORMAL, nullable=False)
    progress = Column(Integer, default=0)  # 0-100
    downloaded_bytes = Column(Integer, default=0)
    total_bytes = Column(Integer, nullable=True)
    speed = Column(Integer, nullable=True)  # Bytes per second

    # Attempts
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, nullable=True)
    error_message = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="downloads")

    def __repr__(self):
        return f"<Download(id={self.id}, source='{self.source}', status='{self.status}', progress={self.progress}%)>"

class DownloadCredential(Base):
    """Download credentials for authenticated sources"""
    __tablename__ = "download_credentials"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), unique=True, nullable=False)  # who, springer, cap, etc.
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)  # Encrypted
    api_key = Column(String(255), nullable=True)  # Encrypted
    token = Column(String(255), nullable=True)  # Encrypted
    session_cookie = Column(String(1024), nullable=True)  # Encrypted
    last_validated = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=False)
    validation_error = Column(String(512), nullable=True)

    def __repr__(self):
        return f"<DownloadCredential(source='{self.source}', is_valid={self.is_valid})>"

class DownloadRateLimit(Base):
    """Rate limiting configuration per source"""
    __tablename__ = "download_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), unique=True, nullable=False)
    max_requests = Column(Integer, nullable=False, default=30)
    time_window = Column(Integer, nullable=False, default=60)  # In seconds
    last_request = Column(DateTime, nullable=True)
    request_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<DownloadRateLimit(source='{self.source}', max_requests={self.max_requests})>"
