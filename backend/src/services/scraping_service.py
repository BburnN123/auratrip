"""Core scraping business service."""

from src.client.videodb_client import VideoDBClient
from src.models.scraped_post import ScrapedPost


class ScrapingService:
    """Orchestrates social media scraping workflows."""

    def __init__(self, videodb_client: VideoDBClient) -> None:
        self.videodb_client = videodb_client

    def ingest_scraped_post(self, post: ScrapedPost) -> dict[str, object]:
        """Ingest a scraped social media post into VideoDB."""
        if not post.media_urls:
            raise ValueError("Scraped post must contain at least one media URL to ingest")

        source_url = post.media_urls[0]
        metadata = {
            "post_id": post.id,
            "platform": post.platform,
        }
        if post.caption:
            metadata["caption"] = post.caption

        return self.videodb_client.ingest_video(
            platform=post.platform,
            source_url=source_url,
            title=f"{post.platform} content",
            description=post.caption,
            metadata=metadata,
        )
