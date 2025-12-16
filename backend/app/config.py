import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator

class AppSettings(BaseModel):
    """Application settings"""
    name: str = "MedBook Search AI"
    version: str = "1.1.0"
    host: str = "127.0.0.1"
    # NOTE: On this Windows machine, port 8000 is in an excluded port range
    # (netsh) and cannot be bound (WinError 10013). Use 9000 by default.
    port: int = 9000
    debug: bool = True
    environment: str = "development"

class PathSettings(BaseModel):
    """Path configuration"""
    data_dir: Path = Path("./data")
    library_dir: Path = Path("./library")
    thumbnails_dir: Path = Path("./data/thumbnails")
    chroma_dir: Path = Path("./data/chroma")
    database: Path = Path("./data/medbook.db")

    @field_validator('*', mode='before')
    @classmethod
    def expand_path(cls, v):
        """Expand relative paths"""
        if isinstance(v, str):
            return Path(v).expanduser().absolute()
        return v

class DownloadSettings(BaseModel):
    """Download manager configuration"""
    max_parallel: int = Field(3, ge=1, le=10)
    chunk_size: int = Field(1048576, ge=1024, le=10485760)
    timeout: int = Field(300, ge=30, le=3600)
    retry_attempts: int = Field(3, ge=1, le=10)
    retry_delay: int = Field(5, ge=1, le=60)

class IndexerSettings(BaseModel):
    """Document indexer configuration"""
    ocr_enabled: bool = True
    ocr_language: str = "deu+eng"
    extract_images: bool = False
    thumbnail_size: List[int] = Field([200, 280], min_items=2, max_items=2)

class TranslationSettings(BaseModel):
    """Translation service configuration"""
    default_engine: str = "deepl"
    default_source_lang: str = "en"
    default_target_lang: str = "de"
    cache_enabled: bool = True

class AISettings(BaseModel):
    """AI service configuration"""
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    reranking_enabled: bool = True
    auto_tagging_enabled: bool = True

class RateLimitSettings(BaseModel):
    """Rate limiting configuration"""
    default: int = 30
    who: int = 10
    iarc: int = 10
    springer: int = 20
    awmf: int = 60
    pubmed: int = 30
    cap: int = 15

class Settings(BaseSettings):
    """Main application settings"""
    app: AppSettings = Field(default_factory=AppSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    downloads: DownloadSettings = Field(default_factory=DownloadSettings)
    indexer: IndexerSettings = Field(default_factory=IndexerSettings)
    translation: TranslationSettings = Field(default_factory=TranslationSettings)
    ai: AISettings = Field(default_factory=AISettings)
    rate_limits: RateLimitSettings = Field(default_factory=RateLimitSettings)

    # API Keys (loaded from environment)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepl_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='MEDBOOK_',
        # Allow nested settings via env vars, e.g. MEDBOOK_APP__PORT=9000
        env_nested_delimiter='__',
        extra='ignore'
    )

    @model_validator(mode='after')
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        p = self.paths
        for path_attr in ['data_dir', 'library_dir', 'thumbnails_dir', 'chroma_dir']:
            path = getattr(p, path_attr)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        return self

    def get_database_url(self) -> str:
        """Get SQLAlchemy database URL"""
        return f"sqlite+aiosqlite:///{self.paths.database}"

    def get_chroma_path(self) -> str:
        """Get ChromaDB path"""
        return str(self.paths.chroma_dir)

# Singleton instance
settings = Settings()

if __name__ == "__main__":
    print("MedBook Search AI Configuration:")
    print(f"Environment: {settings.app.environment}")
    print(f"Host: {settings.app.host}:{settings.app.port}")
    print(f"Data Directory: {settings.paths.data_dir}")
    print(f"Database: {settings.get_database_url()}")
    print(f"Embedding Model: {settings.ai.embedding_model}")
