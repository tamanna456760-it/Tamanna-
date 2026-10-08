"""Foundation V2 API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/foundation", tags=["foundation"])


@router.get("/status")
async def foundation_status():
    return {"status": "ok"}


__all__ = ["router"]
