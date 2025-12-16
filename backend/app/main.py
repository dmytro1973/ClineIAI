import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional
from pathlib import Path

# Import configuration
from .config import settings
from .database import init_db, create_tables, close_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.app.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting MedBook Search AI application...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Create tables if they don't exist
    await create_tables()
    logger.info("Database tables verified/created")

    # Initialize services
    from .services import init_services
    init_services()

    # Start background workers (Phase 3)
    from .services.download_manager import download_manager
    await download_manager.start()

    yield

    # Cleanup on shutdown
    await download_manager.stop()
    await close_db()
    logger.info("Shutting down MedBook Search AI application...")

# Create FastAPI app
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="MedBook Search AI - Pathology Literature Library with AI Search",
    debug=settings.app.debug,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request parameters",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.app.debug else None
        }
    )

# Health endpoint is provided via `backend.app.routers.health`.
# (Avoid defining it twice to prevent duplicate-route ambiguity.)

# Include routers
from .routers import (
    health as health_router_module,
    ai as ai_router_module,
    documents as legacy_documents_router_module,
    search as search_router_module,
    library as library_router_module,
    downloads as downloads_router_module,
    credentials as credentials_router_module,
    translation as translation_router_module,
    settings as settings_router_module,
)

# Note: Some legacy routers already include their own prefixes.
app.include_router(health_router_module.router)
app.include_router(ai_router_module.router)
app.include_router(legacy_documents_router_module.router)

# New stubs / future modules
app.include_router(search_router_module.router)
app.include_router(library_router_module.router)
app.include_router(downloads_router_module.router)
app.include_router(credentials_router_module.router)
app.include_router(translation_router_module.router)
app.include_router(settings_router_module.router)

# ============================================================
# FRONTEND STATIC FILES SERVING
# ============================================================

# Determine frontend dist path (relative to backend working directory)
# In Docker: /app/backend is WORKDIR, frontend/dist is at /app/frontend/dist
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

# Mount static assets if they exist
assets_dir = FRONTEND_DIR / "assets"
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    logger.info(f"Mounted frontend assets from {assets_dir}")

# Serve index.html for all non-API routes (SPA support)
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Serve the SPA - return index.html for all non-API routes"""
    # Skip API routes
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"error": "Not found"})
    
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    
    # Fallback: return API info if no frontend
    return JSONResponse({
        "message": "MedBook Search AI API",
        "version": settings.app.version,
        "docs": "/docs",
        "health": "/api/health"
    })

# ============================================================

def run():
    """Run the application"""
    uvicorn.run(
        "backend.app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level="debug" if settings.app.debug else "info",
        workers=1
    )

if __name__ == "__main__":
    run()
