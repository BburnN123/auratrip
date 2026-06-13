"""Scraped post database model/schema."""

from pydantic import BaseModel


class ScrapedPost(BaseModel):
    """Represents metadata and content references for a social media post."""
    id: str
    platform: str
    url: str
    caption: str | None
    media_urls: list[str]
