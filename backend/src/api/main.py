"""Minimal deployable FastAPI application for Auratrip."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan hooks."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint used by Daytona and load balancers."""
    return {"status": "ok", "app": settings.app_name}


@app.post("/trips")
async def create_trip(request: TripRequest) -> dict:
    """Create a new trip request."""
    if not request.destination:
        raise HTTPException(status_code=400, detail="Destination is required")
    return {
        "id": "trip-placeholder",
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "status": "pending",
    }


@app.get("/trips/{trip_id}/itinerary")
async def get_itinerary(trip_id: str) -> dict:
    """Retrieve a generated itinerary for a trip."""
    return {
        "trip_id": trip_id,
        "days": [],
        "status": "pending",
    }
