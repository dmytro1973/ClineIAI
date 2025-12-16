from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# NOTE: Minimal stub – will be expanded in Phase 2/3.

router = APIRouter(prefix="/api/search", tags=["Search"])

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total: int
    sources: List[str]

@router.get("/sources", response_model=List[str])
async def get_sources():
    return ["awmf"]

@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    sources: Optional[str] = Query(None, description="Comma-separated sources"),
    max_results: int = Query(20, ge=1, le=200)
):
    # Placeholder: will call ScraperFactory + persistence later
    selected_sources = [s.strip() for s in sources.split(",")] if sources else ["awmf"]
    return SearchResponse(query=q, results=[], total=0, sources=selected_sources)

@router.get("/details", response_model=Dict[str, Any])
async def details(url: str = Query(..., description="Document URL")):
    # Placeholder
    return {"url": url, "details": {}}
