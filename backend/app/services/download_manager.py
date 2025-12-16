import asyncio
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy import select

from ..config import settings
from ..database import init_db, AsyncSessionLocal
from ..models.download import Download, DownloadStatus
from ..models.document import Document

logger = logging.getLogger(__name__)


def _safe_filename(name: str) -> str:
    name = name.strip() or "download"
    # Replace windows-illegal characters and collapse whitespace
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    name = re.sub(r"\s+", " ", name)
    return name


def _default_filename_from_url(url: str) -> str:
    try:
        path = urlparse(url).path
        base = os.path.basename(path)
        return base or "download.bin"
    except Exception:
        return "download.bin"


def _priority_rank(value: str) -> int:
    # stored values: low/normal/high
    return {"high": 3, "normal": 2, "low": 1}.get(str(value), 0)


@dataclass
class DownloadManagerConfig:
    max_parallel: int
    chunk_size: int
    timeout: int


class DownloadManager:
    """Simple async download worker.

    Phase 3 scope:
    - Poll DB for pending downloads
    - Download files via HTTP(S)
    - Update progress + status in DB

    Notes:
    - Cancellation is DB-driven: set status=CANCELLED.
    - We avoid keeping DB sessions open across the entire download; instead we
      open short-lived sessions for updates.
    """

    def __init__(self, cfg: Optional[DownloadManagerConfig] = None) -> None:
        if cfg is None:
            cfg = DownloadManagerConfig(
                max_parallel=settings.downloads.max_parallel,
                chunk_size=settings.downloads.chunk_size,
                timeout=settings.downloads.timeout,
            )
        self.cfg = cfg

        self._stop_event = asyncio.Event()
        self._wakeup = asyncio.Event()
        self._runner_task: Optional[asyncio.Task] = None
        self._active: dict[int, asyncio.Task] = {}

    async def start(self) -> None:
        if self._runner_task and not self._runner_task.done():
            return

        init_db()
        self._stop_event.clear()
        self._wakeup.set()
        self._runner_task = asyncio.create_task(self._run_loop())
        logger.info("DownloadManager started")

    async def stop(self) -> None:
        if not self._runner_task:
            return

        logger.info("Stopping DownloadManager...")
        self._stop_event.set()
        self._wakeup.set()

        # Cancel active tasks
        for task in list(self._active.values()):
            task.cancel()

        try:
            await self._runner_task
        finally:
            self._runner_task = None
            self._active.clear()
            logger.info("DownloadManager stopped")

    def wakeup(self) -> None:
        self._wakeup.set()

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            # Cleanup finished tasks
            for download_id, task in list(self._active.items()):
                if task.done():
                    self._active.pop(download_id, None)

            capacity = max(self.cfg.max_parallel - len(self._active), 0)
            if capacity > 0:
                queued = await self._spawn_pending(capacity)
                if queued:
                    # try to immediately pick up more work
                    continue

            # Wait for new work
            self._wakeup.clear()
            try:
                await asyncio.wait_for(self._wakeup.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

    async def _spawn_pending(self, capacity: int) -> bool:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(Download).where(Download.status == DownloadStatus.PENDING)
            )
            downloads = list(res.scalars().all())

        # Filter out those already active
        downloads = [d for d in downloads if d.id not in self._active]

        # Sort by priority (high -> low) and then by created time
        downloads.sort(
            key=lambda d: (_priority_rank(getattr(d.priority, "value", d.priority)), d.created_at or datetime.min),
            reverse=True,
        )

        for d in downloads[:capacity]:
            self._active[d.id] = asyncio.create_task(self._download_one(d.id))

        return bool(downloads[:capacity])

    async def _download_one(self, download_id: int) -> None:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        # Mark as DOWNLOADING
        async with AsyncSessionLocal() as session:
            d = await session.get(Download, download_id)
            if not d:
                return
            if d.status != DownloadStatus.PENDING:
                return

            d.status = DownloadStatus.DOWNLOADING
            d.started_at = datetime.utcnow()
            d.progress = 0
            d.downloaded_bytes = 0
            d.error_message = None
            d.last_attempt = datetime.utcnow()
            d.attempts = (d.attempts or 0) + 1
            await session.commit()

            url = d.url
            target_path = self._build_target_path(d)
            d.file_path = str(target_path)
            await session.commit()

        tmp_path = Path(str(target_path) + ".part")
        tmp_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            timeout = httpx.Timeout(self.cfg.timeout)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    total = resp.headers.get("content-length")
                    total_bytes = int(total) if total and total.isdigit() else None

                    downloaded = 0
                    started = asyncio.get_running_loop().time()
                    last_db_update = started

                    with open(tmp_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(self.cfg.chunk_size):
                            # Check for cancel request
                            if await self._is_cancelled(download_id):
                                raise asyncio.CancelledError()

                            f.write(chunk)
                            downloaded += len(chunk)

                            now = asyncio.get_running_loop().time()
                            if now - last_db_update >= 1.0:
                                speed = int(downloaded / max(now - started, 0.001))
                                progress = (
                                    int(downloaded * 100 / total_bytes)
                                    if total_bytes
                                    else min(int(downloaded / 1024 / 1024), 99)
                                )
                                await self._update_progress(download_id, downloaded, total_bytes, speed, progress)
                                last_db_update = now

                    # Final update
                    await self._mark_completed(download_id, downloaded, total_bytes, target_path)

        except asyncio.CancelledError:
            await self._mark_cancelled(download_id)
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
        except Exception as e:
            logger.exception("Download %s failed: %s", download_id, e)
            await self._mark_failed(download_id, str(e))
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass

    def _build_target_path(self, d: Download) -> Path:
        library_dir = settings.paths.library_dir
        source_dir = library_dir / _safe_filename(d.source)
        source_dir.mkdir(parents=True, exist_ok=True)

        filename = d.file_name or _default_filename_from_url(d.url)
        filename = _safe_filename(filename)

        # Prefix with DB id to avoid collisions
        return source_dir / f"{d.id}-{filename}"

    async def _is_cancelled(self, download_id: int) -> bool:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Download.status).where(Download.id == download_id))
            status = res.scalar_one_or_none()
            return status == DownloadStatus.CANCELLED

    async def _update_progress(
        self,
        download_id: int,
        downloaded_bytes: int,
        total_bytes: Optional[int],
        speed: Optional[int],
        progress: int,
    ) -> None:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            d = await session.get(Download, download_id)
            if not d:
                return

            d.downloaded_bytes = downloaded_bytes
            d.total_bytes = total_bytes
            d.speed = speed
            d.progress = max(0, min(progress, 99))
            await session.commit()

    async def _mark_completed(
        self,
        download_id: int,
        downloaded_bytes: int,
        total_bytes: Optional[int],
        target_path: Path,
    ) -> None:
        # Move tmp to final
        tmp_path = Path(str(target_path) + ".part")
        if tmp_path.exists():
            tmp_path.replace(target_path)

        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            d = await session.get(Download, download_id)
            if not d:
                return

            d.status = DownloadStatus.COMPLETED
            d.completed_at = datetime.utcnow()
            d.progress = 100
            d.downloaded_bytes = downloaded_bytes
            d.total_bytes = total_bytes
            d.speed = None
            d.error_message = None
            await session.commit()

            # Optionally update linked document
            if d.document_id:
                doc = await session.get(Document, d.document_id)
                if doc:
                    doc.is_downloaded = True
                    doc.download_status = "completed"
                    doc.file_path = d.file_path
                    doc.file_size = d.downloaded_bytes
                    await session.commit()

    async def _mark_failed(self, download_id: int, message: str) -> None:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            d = await session.get(Download, download_id)
            if not d:
                return

            d.status = DownloadStatus.FAILED
            d.error_message = message[:512]
            d.completed_at = datetime.utcnow()
            d.speed = None
            await session.commit()

            if d.document_id:
                doc = await session.get(Document, d.document_id)
                if doc:
                    doc.download_status = "failed"
                    doc.download_error = d.error_message
                    doc.last_download_attempt = d.last_attempt
                    doc.download_attempts = d.attempts
                    await session.commit()

    async def _mark_cancelled(self, download_id: int) -> None:
        if AsyncSessionLocal is None:
            init_db()
        assert AsyncSessionLocal is not None

        async with AsyncSessionLocal() as session:
            d = await session.get(Download, download_id)
            if not d:
                return

            d.status = DownloadStatus.CANCELLED
            d.completed_at = datetime.utcnow()
            d.speed = None
            await session.commit()


download_manager = DownloadManager()
