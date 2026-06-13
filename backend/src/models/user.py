"""User database model/schema."""

from typing import Dict, Optional
from pydantic import BaseModel


class User(BaseModel):
    """Represents an Auratrip user profile."""
    id: str
    email: str
    name: Optional[str]
    preferences: Optional[Dict[str, object]]
