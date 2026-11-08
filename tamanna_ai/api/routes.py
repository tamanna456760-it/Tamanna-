"""FastAPI routes for the Tamanna AI API package."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tamanna_ai.integrations.provider import (
    ModelConfigurationError,
    ModelProviderError,
    get_model_provider,
)

api_router = APIRouter(prefix="/tamanna-ai", tags=["tamanna-ai"])


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)


class ChatResponse(BaseModel):
    response: str
    provider: str


@api_router.get("/status")
async def status():
    return {"status": "ok", "service": "tamanna_ai"}


@api_router.get("/health")
async def health():
    return {"status": "healthy"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate a reply with the configured local model provider."""
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be blank.")

    try:
        provider = get_model_provider()
        answer = await provider.generate(prompt)
    except (ModelConfigurationError, ModelProviderError) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Tamanna AI local model is unavailable.",
                "reason": str(exc),
            },
        ) from exc

    return ChatResponse(response=answer, provider=provider.name)


__all__ = ["api_router", "ChatRequest", "ChatResponse"]
