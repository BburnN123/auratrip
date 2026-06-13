"""VideoDB-related request and response models."""

from typing import Dict, Optional
from pydantic import BaseModel


class VideoDBIngestRequest(BaseModel):
    """Request payload for VideoDB video ingestion."""
    platform: str
    source_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
