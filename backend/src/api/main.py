"""FastAPI application entry point."""

from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query

from config.settings import settings
from src.client.videodb_client import VideoDBClient
from src.models.videodb import VideoDBIngestRequest
import logging

app = FastAPI(title="Auratrip API")

videodb_client = VideoDBClient(api_url=settings.videodb_api_url, api_key=settings.videodb_api_key)

logger = logging.getLogger(__name__)
if settings.videodb_mode == "mock":
    # register mock endpoints only in mock mode
    from src.api.videodb_mock import router as videodb_mock_router

    app.include_router(videodb_mock_router)
    logger.info("VideoDB mode=mock; mounted mock videodb routes")
else:
    logger.info(f"VideoDB mode=live; using endpoint {settings.videodb_api_url}")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/videodb/ingest")
async def ingest_video(request: VideoDBIngestRequest) -> dict[str, Any]:
    try:
        return videodb_client.ingest_video(
            platform=request.platform,
            source_url=request.source_url,
            title=request.title,
            description=request.description,
            metadata=request.metadata,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/videodb/search")
async def search_videos(
    q: str = Query(..., description="Search query for VideoDB"),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[str] = Query(None, description="Optional platform filter"),
) -> dict[str, Any]:
    try:
        filters = {"platform": platform} if platform else None
        return videodb_client.search(query=q, limit=limit, filters=filters)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/videodb/alerts")
async def videodb_alerts(
    q: str = Query(..., description="Alert query term"),
    since: Optional[str] = Query(None, description="ISO 8601 start time for alerts"),
) -> dict[str, Any]:
    try:
        return videodb_client.alerts(query=q, since=since)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
