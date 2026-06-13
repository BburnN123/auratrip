"""User database model/schema."""

from pydantic import BaseModel


class User(BaseModel):
    """Represents an Auratrip user profile."""
    id: str
    email: str
    name: str | None
    preferences: dict | None
