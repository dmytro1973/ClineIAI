from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List

# NOTE: Minimal stub – will be expanded in Phase 5.

router = APIRouter(prefix="/api/translation", tags=["Translation"])

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "de"
    engine: str = "deepl"

class TranslateResponse(BaseModel):
    translated_text: str
    engine: str

@router.get("/engines", response_model=List[str])
async def engines():
    return ["deepl", "claude"]

@router.post("/translate", response_model=TranslateResponse)
async def translate(req: TranslateRequest):
    # Placeholder
    return TranslateResponse(translated_text=req.text, engine=req.engine)
