"""Trip database model/schema."""

from pydantic import BaseModel


class Trip(BaseModel):
    """Represents a user trip request."""
    id: str
    user_id: str
    destination: str
    start_date: str
    end_date: str
    status: str
