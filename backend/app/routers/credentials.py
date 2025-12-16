from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

# NOTE: Minimal stub – will be expanded.

router = APIRouter(prefix="/api/credentials", tags=["Credentials"])

class CredentialOut(BaseModel):
    service: str
    is_valid: bool = False

@router.get("/", response_model=List[CredentialOut])
async def list_credentials():
    return []

@router.post("/", response_model=Dict[str, Any])
async def create_credential(payload: Dict[str, Any]):
    return {"created": True}
