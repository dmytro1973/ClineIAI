from .health import router as health_router
from .ai import router as ai_router
from .documents import router as documents_router

__all__ = ['health_router', 'ai_router', 'documents_router']
