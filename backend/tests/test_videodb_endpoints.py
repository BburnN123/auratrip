"""Tests for VideoDB API routes."""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_videodb_ingest_endpoint(monkeypatch) -> None:
    expected_response = {
        "id": "video123",
        "platform": "instagram",
        "source_url": "https://example.com/video.mp4",
        "status": "ingested",
    }

    def fake_ingest_video(platform, source_url, title=None, description=None, metadata=None):
        assert platform == "instagram"
        assert source_url == "https://example.com/video.mp4"
        assert title == "Example video"
        assert description == "Example description"
        assert metadata == {"post_id": "post123", "platform": "instagram"}
        return expected_response

    monkeypatch.setattr("src.api.main.videodb_client.ingest_video", fake_ingest_video)

    response = client.post(
        "/videodb/ingest",
        json={
            "platform": "instagram",
            "source_url": "https://example.com/video.mp4",
            "title": "Example video",
            "description": "Example description",
            "metadata": {"post_id": "post123", "platform": "instagram"},
        },
    )

    assert response.status_code == 200
    assert response.json() == expected_response


def test_videodb_search_endpoint(monkeypatch) -> None:
    expected_response = {
        "results": [
            {"id": "video123", "title": "Grand Palace tour", "platform": "instagram"}
        ]
    }

    def fake_search(query, limit=20, filters=None):
        assert query == "Grand Palace"
        assert limit == 10
        assert filters == {"platform": "instagram"}
        return expected_response

    monkeypatch.setattr("src.api.main.videodb_client.search", fake_search)

    response = client.get("/videodb/search", params={"q": "Grand Palace", "limit": 10, "platform": "instagram"})
    assert response.status_code == 200
    assert response.json() == expected_response


def test_videodb_alerts_endpoint(monkeypatch) -> None:
    expected_response = {
        "alerts": [
            {"id": "alert1", "message": "New Bangkok temple video posted"}
        ]
    }

    def fake_alerts(query, since=None):
        assert query == "Bangkok temple"
        assert since == "2026-06-13T00:00:00Z"
        return expected_response

    monkeypatch.setattr("src.api.main.videodb_client.alerts", fake_alerts)

    response = client.get(
        "/videodb/alerts",
        params={"q": "Bangkok temple", "since": "2026-06-13T00:00:00Z"},
    )
    assert response.status_code == 200
    assert response.json() == expected_response
