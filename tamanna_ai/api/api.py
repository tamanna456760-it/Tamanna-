"""Compatibility entry point for the package FastAPI application."""
from .server import app, create_app

__all__ = ["app", "create_app"]
