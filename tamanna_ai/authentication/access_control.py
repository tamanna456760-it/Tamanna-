"""Fail-closed access checks for sensitive API routes."""
import os
from http.cookies import SimpleCookie
from starlette.responses import JSONResponse
from tamanna_ai.authentication.router import COOKIE, current_user

USER_ROUTES = {
    "/api/chat", "/api/history",
    "/api/skills/create", "/api/skills/test", "/api/skills/refine",
    "/api/code-builder/propose",
    "/api/self-improvement/analyze", "/api/self-healing/diagnose",
    "/api/self-healing/cycle", "/api/autonomous/build",
    "/api/autonomous/repair", "/api/code-builder/apply",
    "/api/code-builder/build", "/api/code-builder/compile",
    "/api/linux/run", "/api/linux/shell", "/api/command",
    "/api/tamanna/echo", "/api/tools/execute",
}
READ_ROUTES = {"/api/history"}

BLOCKED_EXECUTION_ROUTES = {
    "/api/linux/run",
    "/api/linux/shell",
    "/api/command",
    "/api/code-builder/build",
    "/api/code-builder/compile",
    "/api/autonomous/build",
    "/api/autonomous/repair",
    "/api/self-healing/cycle",
}

ADMIN_ROUTES = {
    "/api/skills/create", "/api/skills/test", "/api/skills/refine",
    "/api/code-builder/propose", "/api/self-healing/cycle", "/api/autonomous/build",
    "/api/autonomous/repair", "/api/code-builder/apply",
    "/api/code-builder/build", "/api/code-builder/compile",
    "/api/linux/run", "/api/linux/shell", "/api/command",
    "/api/tamanna/echo",
}

class TamannaAccessControl:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        method = scope.get("method", "")
        path = scope.get("path", "")
        is_write = method in {"POST", "PUT", "PATCH", "DELETE"} and path in USER_ROUTES
        is_protected_read = method == "GET" and path in READ_ROUTES
        if not (is_write or is_protected_read):
            await self.app(scope, receive, send)
            return
        if path in BLOCKED_EXECUTION_ROUTES:
            response = JSONResponse(
                {"detail": "This command-execution endpoint is disabled for safety."},
                status_code=410,
            )
            await response(scope, receive, send)
            return
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
        try:
            user = current_user(token)
        except RuntimeError:
            response = JSONResponse({"detail": "Authentication is unavailable; configure the server session secret."}, status_code=503)
            await response(scope, receive, send)
            return
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
