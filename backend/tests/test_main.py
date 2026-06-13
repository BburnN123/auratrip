"""Unit tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "Auratrip"}


def test_create_trip(client: TestClient) -> None:
    payload = {
        "destination": "Bangkok",
        "start_date": "2026-07-01",
        "end_date": "2026-07-07",
    }
    response = client.post("/trips", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Bangkok"
    assert data["start_date"] == "2026-07-01"
    assert data["end_date"] == "2026-07-07"
    assert data["status"] == "pending"
    assert "id" in data


def test_create_trip_missing_destination(client: TestClient) -> None:
    payload = {
        "destination": "",
        "start_date": "2026-07-01",
        "end_date": "2026-07-07",
    }
    response = client.post("/trips", json=payload)
    assert response.status_code == 400
    assert "Destination is required" in response.json()["detail"]


def test_get_itinerary(client: TestClient) -> None:
    response = client.get("/trips/trip-123/itinerary")
    assert response.status_code == 200
    data = response.json()
    assert data["trip_id"] == "trip-123"
    assert data["days"] == []
    assert data["status"] == "pending"
