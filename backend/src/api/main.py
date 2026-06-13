"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Auratrip API")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
