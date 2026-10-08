"""Module control API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/module-control", tags=["modules"])


@router.get("/status")
async def module_status():
    return {"status": "ok", "modules": []}


@router.get("/scan")
async def module_scan():
    return {"status": "ok", "modules": []}


__all__ = ["router"]
