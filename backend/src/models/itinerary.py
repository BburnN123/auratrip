"""Itinerary database model/schema."""

from pydantic import BaseModel


class Itinerary(BaseModel):
    """Represents a generated day-by-day itinerary."""
    id: str
    trip_id: str
    days: list[dict]
