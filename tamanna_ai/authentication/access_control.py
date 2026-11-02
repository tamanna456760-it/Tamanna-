"""Fail-closed access checks for sensitive API routes."""
import os
from http.cookies import SimpleCookie
from starlette.responses import JSONResponse
from tamanna_ai.authentication.router import COOKIE, current_user

USER_ROUTES = {
    "/api/skills/create", "/api/skills/test", "/api/skills/refine",
    "/api/self-improvement/analyze", "/api/self-healing/diagnose",
    "/api/self-healing/cycle", "/api/autonomous/build",
    "/api/autonomous/repair", "/api/code-builder/apply",
    "/api/code-builder/build", "/api/code-builder/compile",
    "/api/linux/run", "/api/linux/shell", "/api/command",
}
ADMIN_ROUTES = {
    "/api/self-healing/cycle", "/api/autonomous/build",
    "/api/autonomous/repair", "/api/code-builder/apply",
    "/api/code-builder/build", "/api/code-builder/compile",
    "/api/linux/run", "/api/linux/shell", "/api/command",
}

class TamannaAccessControl:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("method") not in {"POST", "PUT", "PATCH", "DELETE"}:
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if path not in USER_ROUTES:
            await self.app(scope, receive, send)
            return
        cookie_header = dict(scope.get("headers", [])).get(b"cookie", b"").decode("latin-1")
        jar = SimpleCookie()
        try:
            jar.load(cookie_header)
            item = jar.get(COOKIE)
            token = item.value if item else None
        except Exception:
            token = None
        user = current_user(token)
        if not user:
            response = JSONResponse({"detail": "Sign in required."}, status_code=401)
            await response(scope, receive, send)
            return
        if path in ADMIN_ROUTES:
            admin_email = os.getenv("TAMANNA_ADMIN_EMAIL", "").strip().lower()
            if not admin_email:
                response = JSONResponse({"detail": "Admin access is disabled until TAMANNA_ADMIN_EMAIL is configured."}, status_code=503)
                await response(scope, receive, send)
                return
            if user.get("email", "").lower() != admin_email:
                response = JSONResponse({"detail": "Administrator access required."}, status_code=403)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
