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


@api_router.get("/model/status")
async def model_status():
    """Report local runtime availability and installed model names."""
    try:
        provider = get_model_provider()
        list_models = getattr(provider, "list_models", None)
        if list_models is None:
            raise ModelProviderError("Configured provider does not expose model discovery.")
        models = await list_models()
    except (ModelConfigurationError, ModelProviderError) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "message": "Tamanna AI local model runtime is unavailable.",
                "reason": str(exc),
            },
        ) from exc

    return {
        "status": "ready" if models else "no_models_installed",
        "provider": provider.name,
        "selected_model": getattr(getattr(provider, "client", None), "model", None),
        "installed_models": models,
    }


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
