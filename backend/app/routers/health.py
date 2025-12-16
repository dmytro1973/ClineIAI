from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Health"])

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "service": "VerdentMoi API",
        "version": "1.0.0"
    }

@router.get("/status", response_model=dict)
async def detailed_status():
    return {
        "status": "operational",
        "backend": "healthy",
        "database": "connected",
        "ai_models": ["gpt-4", "claude-3"],
        "timestamp": "2023-12-16T18:00:00Z"
    }
