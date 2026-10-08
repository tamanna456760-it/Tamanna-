"""Tamanna V3 API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/tamanna-v3", tags=["tamanna-v3"])


@router.get("/status")
async def v3_status():
    return {"status": "ok"}


__all__ = ["router"]
