
"""Tamanna AI package API server."""
from fastapi import FastAPI

from .routes import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tamanna AI Package API",
        version="1.0.0",
    )

    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health():
        return {
            "status": "healthy",
            "service": "tamanna-ai-package-api",
        }

    return app


app = create_app()
