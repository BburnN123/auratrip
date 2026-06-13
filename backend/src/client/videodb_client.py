"""VideoDB client integration."""

import json
from typing import Any, Dict, Optional

import requests
from requests import RequestException


class VideoDBClient:
    """Manages video ingestion, indexing, and semantic search."""

    def __init__(self, api_url: str, api_key: Optional[str] = None) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, endpoint: str, method: str = "GET", body: Optional[Any] = None, params: Optional[Dict[str, str]] = None) -> Any:
        url = f"{self.api_url}/{endpoint.lstrip('/') }"

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._build_headers(),
                json=body,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            if not response.text:
                return {}
            return response.json()
        except RequestException as exc:
            message = f"VideoDB request failed: {exc}"
            if hasattr(exc, "response") and exc.response is not None:
                try:
                    body_text = exc.response.text
                    if body_text:
                        message = f"VideoDB request failed: {exc} - response={body_text}"
                except Exception:
                    pass
            raise RuntimeError(message) from exc

    def ingest_video(
        self,
        platform: str,
        source_url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "platform": platform,
            "source_url": source_url,
            "title": title or "",
            "description": description or "",
            "metadata": metadata or {},
        }
        return self._request("/videos/ingest", method="POST", body=payload)

    def search(self, query: str, limit: int = 20, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        params = {"q": query, "limit": str(limit)}
        if filters:
            params.update(filters)
        return self._request("/videos/search", method="GET", params=params)

    def alerts(self, query: str, since: Optional[str] = None) -> Dict[str, Any]:
        params = {"q": query}
        if since:
            params["since"] = since
        return self._request("/alerts", method="GET", params=params)

    def extract_clip(self, video_id: str, start_time: str, end_time: str) -> Dict[str, Any]:
        payload = {"start_time": start_time, "end_time": end_time}
        return self._request(f"/videos/{video_id}/clips", method="POST", body=payload)
