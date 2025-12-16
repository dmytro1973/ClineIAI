from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health_router, ai_router, documents_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="VerdentMoi API",
        description="Medical AI Backend",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(ai_router)
    app.include_router(documents_router)

    return app
