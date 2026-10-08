"""FastAPI router for message memory APIs."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/")
async def list_messages():
    return {"messages": []}


__all__ = ["router"]
