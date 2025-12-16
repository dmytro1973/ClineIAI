from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

# NOTE: Minimal stub – will be expanded.

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingsOut(BaseModel):
    app_name: str = "MedBook Search AI"

@router.get("/", response_model=SettingsOut)
async def get_settings():
    return SettingsOut()

@router.post("/api-key", response_model=Dict[str, Any])
async def save_api_key(payload: Dict[str, Any]):
    # Placeholder endpoint for the frontend Settings GUI
    return {"saved": True}
