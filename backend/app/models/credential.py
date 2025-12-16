from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, UniqueConstraint
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
from datetime import datetime
from ..db_base import Base

class Credential(Base):
    """Credential storage for external services"""
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50), unique=True, nullable=False)  # openai, anthropic, deepl, who, springer, etc.
    service_name = Column(String(100), nullable=False)  # Display name
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)  # Encrypted
    api_key = Column(String(255), nullable=True)  # Encrypted
    api_secret = Column(String(255), nullable=True)  # Encrypted
    access_token = Column(String(512), nullable=True)  # Encrypted
    refresh_token = Column(String(512), nullable=True)  # Encrypted
    token_expiry = Column(DateTime, nullable=True)

    # Configuration
    base_url = Column(String(255), nullable=True)
    rate_limit = Column(Integer, nullable=True)
    custom_headers = Column(JSON, nullable=True)  # Custom HTTP headers

    # Status
    is_valid = Column(Boolean, default=False)
    last_validated = Column(DateTime, nullable=True)
    validation_error = Column(String(512), nullable=True)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Credential(service='{self.service}', is_valid={self.is_valid})>"

class TranslationCache(Base):
    """Translation cache to avoid duplicate translations"""
    __tablename__ = "translation_cache"

    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(String(1024), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(String(1024), nullable=False)
    engine = Column(String(20), nullable=False)  # deepl, claude, google, etc.
    confidence = Column(Integer, nullable=True)  # 0-100

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=1)

    __table_args__ = (
        UniqueConstraint("source_text", "source_language", "target_language", "engine", name="uq_translation_cache"),
    )

    def __repr__(self):
        return f"<TranslationCache(source_lang='{self.source_language}', target_lang='{self.target_language}')>"

class TranslationGlossary(Base):
    """Medical translation glossary"""
    __tablename__ = "translation_glossary"

    id = Column(Integer, primary_key=True, index=True)
    source_term = Column(String(255), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_term = Column(String(255), nullable=False)
    target_language = Column(String(10), nullable=False)
    context = Column(String(512), nullable=True)  # Medical context
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("source_term", "source_language", "target_language", name="uq_translation_glossary"),
    )

    def __repr__(self):
        return f"<TranslationGlossary({self.source_language} '{self.source_term}' -> {self.target_language} '{self.target_term}')>"
