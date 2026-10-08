"""System upgrade API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/upgrade", tags=["upgrade"])


@router.get("/status")
async def upgrade_status():
    return {"status": "ok"}


__all__ = ["router"]
