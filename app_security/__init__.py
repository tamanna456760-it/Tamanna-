"""Security dependencies for privileged Tamanna API routes."""

from .auth import verify_admin_key

__all__ = ["verify_admin_key"]
