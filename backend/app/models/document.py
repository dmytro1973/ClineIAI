from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..db_base import Base

class Document(Base):
    """Medical document model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # awmf, who, springer, pubmed, cap
    source_id = Column(String(100), unique=True, nullable=False)  # Unique ID from source
    url = Column(String(512), nullable=True)
    file_path = Column(String(512), nullable=True)  # Relative path in library
    file_size = Column(Integer, nullable=True)  # In bytes
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    mime_type = Column(String(50), nullable=True)

    # Metadata
    authors = Column(String(512), nullable=True)
    published_date = Column(DateTime, nullable=True)
    publisher = Column(String(100), nullable=True)
    language = Column(String(10), nullable=True)
    doi = Column(String(100), nullable=True)
    pmc_id = Column(String(50), nullable=True)
    pm_id = Column(String(50), nullable=True)

    # Content
    abstract = Column(Text, nullable=True)
    keywords = Column(String(512), nullable=True)
    content_text = Column(Text, nullable=True)  # Extracted text for search
    content_length = Column(Integer, nullable=True)  # Character count

    # Status
    is_downloaded = Column(Boolean, default=False)
    download_status = Column(String(20), nullable=True)  # pending, downloading, completed, failed
    download_error = Column(String(512), nullable=True)
    download_attempts = Column(Integer, default=0)
    last_download_attempt = Column(DateTime, nullable=True)

    # Processing
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(20), nullable=True)  # pending, processing, completed, failed
    processing_error = Column(String(512), nullable=True)
    has_ocr = Column(Boolean, default=False)
    has_thumbnail = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_accessed = Column(DateTime, nullable=True)

    # Relationships
    tags = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")
    collections = relationship("DocumentCollection", back_populates="document", cascade="all, delete-orphan")
    notes = relationship("DocumentNote", back_populates="document", cascade="all, delete-orphan")
    translations = relationship("DocumentTranslation", back_populates="document", cascade="all, delete-orphan")
    translation_jobs = relationship("TranslationJob", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"

class DocumentTag(Base):
    """Document tag association"""
    __tablename__ = "document_tags"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="documents")

    __table_args__ = (
        UniqueConstraint("document_id", "tag_id", name="uq_document_tag"),
    )

class Tag(Base):
    """Tag model"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(20), nullable=True)  # Hex color code
    is_system = Column(Boolean, default=False)  # System-generated tag

    documents = relationship("DocumentTag", back_populates="tag")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

class DocumentCollection(Base):
    """Document collection association"""
    __tablename__ = "document_collections"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)

    document = relationship("Document", back_populates="collections")
    collection = relationship("Collection", back_populates="documents")

    __table_args__ = (
        UniqueConstraint("document_id", "collection_id", name="uq_document_collection"),
    )

class Collection(Base):
    """Collection model"""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System-generated collection

    documents = relationship("DocumentCollection", back_populates="collection")

    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}')>"

class DocumentNote(Base):
    """Document note"""
    __tablename__ = "document_notes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    document = relationship("Document", back_populates="notes")

class DocumentTranslation(Base):
    """Document translation"""
    __tablename__ = "document_translations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_content = Column(Text, nullable=False)
    translation_engine = Column(String(20), nullable=False)  # deepl, claude, etc.
    translation_date = Column(DateTime, server_default=func.now())
    is_cached = Column(Boolean, default=False)

    document = relationship("Document", back_populates="translations")

    __table_args__ = (
        UniqueConstraint("document_id", "source_language", "target_language", name="uq_document_translation"),
    )

class DocumentEmbedding(Base):
    """Document embedding for vector search"""
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    embedding = Column(JSON, nullable=False)  # Vector embedding as JSON array
    chunk_text = Column(Text, nullable=False)  # Text chunk that was embedded
    chunk_index = Column(Integer, nullable=False)  # Chunk number
    embedding_model = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="embeddings")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_embedding"),
    )
