"""
Services package initialization
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def init_services():
    """Initialize all application services"""
    logger.info("Initializing application services...")

    # Initialize AI service
    try:
        from .ai_service import ai_service
        logger.info("AI service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")

    # Initialize other services as they are implemented
    # For now, just log that services are ready
    logger.info("All services initialized successfully")

# Export main services
__all__ = [
    'init_services'
]
