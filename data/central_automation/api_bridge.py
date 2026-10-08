"""Central automation API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.get("/status")
async def automation_status():
    return {"status": "ok"}


__all__ = ["router"]
