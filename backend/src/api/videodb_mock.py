"""Local VideoDB mock endpoints for development demos."""

from typing import Optional, Dict
from fastapi import APIRouter

router = APIRouter(prefix="/mock-videodb", tags=["VideoDB Mock"])


@router.get("/search")
async def mock_search(q: str, limit: int = 20, platform: Optional[str] = None) -> dict:
    return {
        "query": q,
        "limit": limit,
        "platform": platform,
        "results": [
            {
                "id": "mock-video-1",
                "title": f"Mock result for {q}",
                "platform": platform or "instagram",
                "captured_at": "2026-06-13T12:00:00Z",
            }
        ],
    }


@router.get("/alerts")
async def mock_alerts(q: str, since: Optional[str] = None) -> dict:
    return {
        "query": q,
        "since": since,
        "alerts": [
            {
                "id": "mock-alert-1",
                "message": f"Mock alert for {q}",
                "created_at": "2026-06-13T12:00:00Z",
            }
        ],
    }


@router.post("/videos/ingest")
async def mock_ingest_video(platform: str, source_url: str, title: Optional[str] = None, description: Optional[str] = None, metadata: Optional[Dict] = None) -> dict:
    return {
        "id": "mock-ingest-1",
        "platform": platform,
        "source_url": source_url,
        "title": title,
        "description": description,
        "metadata": metadata or {},
        "status": "mocked",
    }
