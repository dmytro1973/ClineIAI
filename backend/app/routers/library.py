from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# NOTE: Minimal stub – will be expanded in Phase 3/4.

router = APIRouter(prefix="/api/library", tags=["Library"])

class DocumentOut(BaseModel):
    id: int
    title: str
    source: str

@router.get("/documents", response_model=List[DocumentOut])
async def list_documents():
    return []

@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(document_id: int):
    return {"id": document_id}
