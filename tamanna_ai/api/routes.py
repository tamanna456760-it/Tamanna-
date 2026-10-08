"""FastAPI routes for the Tamanna AI API package."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/tamanna-ai", tags=["tamanna-ai"])


@api_router.get("/status")
async def status():
    return {"status": "ok", "service": "tamanna_ai"}


@api_router.get("/health")
async def health():
    return {"status": "healthy"}


__all__ = ["api_router"]
