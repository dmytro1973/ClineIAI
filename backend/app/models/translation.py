from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
from datetime import datetime
from ..db_base import Base

class TranslationJob(Base):
    """Translation job for documents"""
    __tablename__ = "translation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    engine = Column(String(20), nullable=False)  # deepl, claude, google, etc.
    status = Column(String(20), nullable=False)  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100

    # Result
    translated_content = Column(Text, nullable=True)
    translation_date = Column(DateTime, nullable=True)
    error_message = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="translation_jobs")

    def __repr__(self):
        return f"<TranslationJob(id={self.id}, {self.source_language}->{self.target_language}, status='{self.status}')>"

class TranslationEngine(Base):
    """Available translation engines"""
    __tablename__ = "translation_engines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=True)
    requires_api_key = Column(Boolean, default=False)
    supports_languages = Column(JSON, nullable=False)  # List of supported languages
    max_length = Column(Integer, nullable=True)  # Max characters per request
    rate_limit = Column(Integer, nullable=True)  # Requests per minute

    def __repr__(self):
        return f"<TranslationEngine(name='{self.name}', enabled={self.is_enabled})>"

class TranslationHistory(Base):
    """Translation history for auditing"""
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # If user system is implemented
    source_text = Column(String(1024), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(String(1024), nullable=False)
    engine = Column(String(20), nullable=False)
    confidence = Column(Integer, nullable=True)  # 0-100
    cost = Column(Integer, nullable=True)  # Cost in credits/cents
    duration = Column(Integer, nullable=True)  # Duration in milliseconds

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<TranslationHistory({self.source_language}->{self.target_language}, cost={self.cost})>"
