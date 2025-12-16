from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.download import Download, DownloadStatus, DownloadPriority
from ..services.download_manager import download_manager

router = APIRouter(prefix="/api/downloads", tags=["Downloads"])


class DownloadCreateRequest(BaseModel):
    url: str
    source: str = Field(default="manual", description="Source identifier (e.g. awmf, who, manual)")
    source_id: str = Field(default="manual", description="ID at source; for manual downloads can be 'manual'")
    document_id: Optional[int] = None
    file_name: Optional[str] = None
    priority: str = Field(default="normal", description="low|normal|high")


class DownloadOut(BaseModel):
    id: int
    document_id: Optional[int]
    source: str
    source_id: str
    url: str
    file_path: Optional[str]
    file_name: Optional[str]

    status: str
    priority: str
    progress: int
    downloaded_bytes: int
    total_bytes: Optional[int]
    speed: Optional[int]

    attempts: int
    last_attempt: Optional[datetime]
    error_message: Optional[str]

    created_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


def _to_out(d: Download) -> DownloadOut:
    return DownloadOut(
        id=d.id,
        document_id=d.document_id,
        source=d.source,
        source_id=d.source_id,
        url=d.url,
        file_path=d.file_path,
        file_name=d.file_name,
        status=d.status.value if hasattr(d.status, "value") else str(d.status),
        priority=d.priority.value if hasattr(d.priority, "value") else str(d.priority),
        progress=d.progress or 0,
        downloaded_bytes=d.downloaded_bytes or 0,
        total_bytes=d.total_bytes,
        speed=d.speed,
        attempts=d.attempts or 0,
        last_attempt=d.last_attempt,
        error_message=d.error_message,
        created_at=d.created_at,
        started_at=d.started_at,
        completed_at=d.completed_at,
    )


@router.get("/", response_model=List[DownloadOut])
async def list_downloads(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Download).order_by(Download.created_at.desc()))
    return [_to_out(d) for d in res.scalars().all()]


@router.get("/{download_id}", response_model=DownloadOut)
async def get_download(download_id: int, db: AsyncSession = Depends(get_db)):
    d = await db.get(Download, download_id)
    if not d:
        raise HTTPException(status_code=404, detail="Download not found")
    return _to_out(d)


@router.post("/", response_model=DownloadOut)
async def enqueue_download(payload: DownloadCreateRequest, db: AsyncSession = Depends(get_db)):
    priority_map = {
        "low": DownloadPriority.LOW,
        "normal": DownloadPriority.NORMAL,
        "high": DownloadPriority.HIGH,
    }
    priority = priority_map.get(payload.priority.lower())
    if priority is None:
        raise HTTPException(status_code=400, detail="Invalid priority. Use low|normal|high")

    d = Download(
        document_id=payload.document_id,
        source=payload.source,
        source_id=payload.source_id,
        url=payload.url,
        file_name=payload.file_name,
        status=DownloadStatus.PENDING,
        priority=priority,
        progress=0,
        downloaded_bytes=0,
        attempts=0,
    )

    db.add(d)
    await db.flush()
    await db.commit()  # persist immediately so worker can pick it up
    await db.refresh(d)

    # Notify worker
    download_manager.wakeup()

    return _to_out(d)


@router.post("/{download_id}/cancel", response_model=DownloadOut)
async def cancel_download(download_id: int, db: AsyncSession = Depends(get_db)):
    d = await db.get(Download, download_id)
    if not d:
        raise HTTPException(status_code=404, detail="Download not found")

    # Mark as cancelled; worker checks this periodically.
    d.status = DownloadStatus.CANCELLED
    d.error_message = None
    await db.commit()

    download_manager.wakeup()
    return _to_out(d)


@router.post("/{download_id}/retry", response_model=DownloadOut)
async def retry_download(download_id: int, db: AsyncSession = Depends(get_db)):
    d = await db.get(Download, download_id)
    if not d:
        raise HTTPException(status_code=404, detail="Download not found")

    if d.status not in {DownloadStatus.FAILED, DownloadStatus.CANCELLED}:
        raise HTTPException(status_code=400, detail="Only failed/cancelled downloads can be retried")

    d.status = DownloadStatus.PENDING
    d.progress = 0
    d.downloaded_bytes = 0
    d.total_bytes = None
    d.speed = None
    d.error_message = None
    await db.commit()

    download_manager.wakeup()
    return _to_out(d)
