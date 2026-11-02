"""Fail-closed access checks for sensitive API routes."""
import os
from http.cookies import SimpleCookie

from starlette.responses import JSONResponse

from tamanna_ai.authentication.router import COOKIE, current_user

# Every mutating or execution-capable endpoint must be listed here.
# ADMIN_ROUTES are also members of USER_ROUTES and require the configured
# TAMANNA_ADMIN_EMAIL account.
USER_ROUTES = {
    # Chat endpoints can reach action/tool orchestration and require a session.
    "/api/chat",
    "/api/chat/master",
    "/api/tamanna/echo",
    "/api/autonomous/plan",
    "/api/code-builder/plan",
    "/api/skills/create",
    "/api/skills/test",
    "/api/skills/refine",
    "/api/self-improvement/analyze",
    "/api/self-healing/diagnose",
    "/api/self-healing/cycle",
    "/api/autonomous/build",
    "/api/autonomous/repair",
    "/api/code-builder/propose",
    "/api/code-builder/apply",
    "/api/code-builder/build",
    "/api/code-builder/compile",
    "/api/linux/run",
    "/api/linux/shell",
    "/api/command",
}

# GET endpoints that disclose project inventory or internal operational state.
READ_ROUTES = {
    "/api/autonomous/think",
    "/api/autonomous/files",
    "/api/autonomous/startup",
    "/api/autonomous/plans",
    "/api/autonomous/repair/status",
    "/api/autonomous/repair/history",
    "/api/autonomous/status",
    "/api/linux/tools",
    "/api/linux/status",
    "/api/linux/shell/status",
    "/api/self-healing/status",
    "/api/code-builder/status",
    "/api/code-builder/scan",
    "/api/code-builder/project",
    "/api/unified/status",
    "/api/unified/project",
    "/api/security/tools",
}

ADMIN_ROUTES = {
    "/api/skills/create",
    "/api/skills/test",
    "/api/skills/refine",
    "/api/self-healing/cycle",
    "/api/autonomous/build",
    "/api/autonomous/repair",
    "/api/code-builder/propose",
    "/api/code-builder/apply",
    "/api/code-builder/build",
    "/api/code-builder/compile",
    "/api/linux/run",
    "/api/linux/shell",
    "/api/command",
}


def _trusted_origins() -> set[str]:
    raw = os.getenv(
        "TAMANNA_CORS_ORIGINS",
        "https://www.tamanna.com,https://tamanna.com",
    )
    return {value.strip().rstrip("/") for value in raw.split(",") if value.strip()}


class TamannaAccessControl:
    """Protect privileged write/execute routes with session and origin checks."""

    def __init__(self, app):
        self.app = app

    async def _reject(self, scope, receive, send, status: int, detail: str):
        response = JSONResponse({"detail": detail}, status_code=status)
        await response(scope, receive, send)

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "")
        mutating = method in {"POST", "PUT", "PATCH", "DELETE"}
        protected_read = method in {"GET", "HEAD"} and path in READ_ROUTES
        if (path not in USER_ROUTES and path not in READ_ROUTES) or not (mutating or protected_read):
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        origin = headers.get(b"origin", b"").decode("latin-1").strip().rstrip("/")
        # Browser state-changing requests carrying cookies must originate from
        # an explicitly trusted Tamanna frontend. Requests without Origin
        # (e.g. server-to-server clients) still require a valid session.
        if origin and origin not in _trusted_origins():
            await self._reject(scope, receive, send, 403, "Untrusted request origin.")
            return

        cookie_header = headers.get(b"cookie", b"").decode("latin-1")
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
            await self._reject(
                scope, receive, send, 503,
                "Authentication is unavailable; configure the server session secret.",
            )
            return

        if not user:
            await self._reject(scope, receive, send, 401, "Sign in required.")
            return

        if path in ADMIN_ROUTES:
            admin_email = os.getenv("TAMANNA_ADMIN_EMAIL", "").strip().lower()
            if not admin_email:
                await self._reject(
                    scope, receive, send, 503,
                    "Admin access is disabled until TAMANNA_ADMIN_EMAIL is configured.",
                )
                return
            if user.get("email", "").strip().lower() != admin_email:
                await self._reject(scope, receive, send, 403, "Administrator access required.")
                return

        await self.app(scope, receive, send)
