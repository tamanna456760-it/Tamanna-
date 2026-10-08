"""Control center API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/control", tags=["control"])


@router.get("/status")
async def control_status():
    return {"status": "ok"}


@router.get("/permissions")
async def permissions_status():
    return {"status": "ok", "protected_actions": []}


__all__ = ["router"]
