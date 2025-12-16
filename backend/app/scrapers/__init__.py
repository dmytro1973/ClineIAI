# Scrapers package initialization
from .base import BaseScraper, ScraperConfig, SearchResult, DocumentMetadata, ScraperFactory

# Export main classes for easy importing
__all__ = [
    'BaseScraper',
    'ScraperConfig',
    'SearchResult',
    'DocumentMetadata',
    'ScraperFactory'
]
