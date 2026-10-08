"""Master control API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/master", tags=["master"])


@router.get("/status")
async def master_status():
    return {"status": "ok"}


__all__ = ["router"]
