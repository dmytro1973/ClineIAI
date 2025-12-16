# Models package initialization
# NOTE: Import order matters where relationships are referenced by string.

from .document import (
    Document,
    DocumentTag,
    Tag,
    DocumentCollection,
    Collection,
    DocumentNote,
    DocumentTranslation,
    DocumentEmbedding,
)

from .download import (
    Download,
    DownloadCredential,
    DownloadRateLimit,
    DownloadStatus,
    DownloadPriority,
)

from .credential import (
    Credential,
    TranslationCache,
    TranslationGlossary,
)

from .translation import (
    TranslationJob,
    TranslationEngine,
    TranslationHistory,
)

# Export all models for easy importing
__all__ = [
    # Document models
    'Document',
    'DocumentTag',
    'Tag',
    'DocumentCollection',
    'Collection',
    'DocumentNote',
    'DocumentTranslation',
    'DocumentEmbedding',

    # Download models
    'Download',
    'DownloadCredential',
    'DownloadRateLimit',
    'DownloadStatus',
    'DownloadPriority',

    # Credential models
    'Credential',
    'TranslationCache',
    'TranslationGlossary',

    # Translation models
    'TranslationJob',
    'TranslationEngine',
    'TranslationHistory',
]
