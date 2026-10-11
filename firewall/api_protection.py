"""
Tamanna AI — API Protection Layer
Owner: HM INSAN ALI
Purpose:
- Validate API request metadata.
- Apply request-size and content-type limits.
- Apply rate limiting.
- Require authentication for sensitive routes.
- Avoid trusting unverified forwarded client IP headers.
IMPORTANT:
This module provides security checks for integration into the API.
It does not protect FastAPI endpoints until the application calls it.
It does not modify operating-system firewall rules.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any, Optional
DEFAULT_MAX_BODY_BYTES = 1_048_576  # 1 MiB
DEFAULT_ALLOWED_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
}
DEFAULT_PROTECTED_PREFIXES = (
    "/api/admin",
    "/api/security",
    "/api/firewall",
)
_SAFE_PATH_RE = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/\-]*$")
@dataclass(frozen=True)
class APIProtectionResult:
    allowed: bool
    status_code: int
    code: str
    message: str
    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "status_code": self.status_code,
            "code": self.code,
            "message": self.message,
        }
def _result(
    allowed: bool,
    status_code: int,
    code: str,
    message: str,
) -> APIProtectionResult:
    return APIProtectionResult(
        allowed=allowed,
        status_code=status_code,
        code=code,
        message=message,
    )
def is_protected_path(
    path: str,
    protected_prefixes: tuple[str, ...] = DEFAULT_PROTECTED_PREFIXES,
) -> bool:
    """Return True when a path belongs to a sensitive API prefix."""
    normalized = path.rstrip("/") or "/"
    for prefix in protected_prefixes:
        prefix = prefix.rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False
def validate_api_request(
    *,
    method: str,
    path: str,
    content_type: Optional[str] = None,
    content_length: Optional[int] = None,
    authenticated: bool = False,
    client_id: Optional[str] = None,
    rate_limiter: Any = None,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    allowed_methods: Optional[set[str]] = None,
    protected_prefixes: tuple[str, ...] = DEFAULT_PROTECTED_PREFIXES,
    require_json_for_write_methods: bool = True,
) -> APIProtectionResult:
    """
    Validate request metadata before an API endpoint processes a request.
    The caller must supply authenticated=True only after its real
    authentication mechanism has verified the request.
    client_id should come from trusted server-side connection metadata
    or an authenticated identity—not an arbitrary client header.
    """
    if not isinstance(method, str) or not isinstance(path, str):
        return _result(
            False, 400, "invalid_request", "Invalid request metadata."
        )
    method = method.upper()
    methods = allowed_methods or DEFAULT_ALLOWED_METHODS
    methods = {item.upper() for item in methods}
    if method not in methods:
        return _result(
            False, 405, "method_not_allowed", "HTTP method is not allowed."
        )
    if (
        not path.startswith("/")
        or "\\" in path
        or "\x00" in path
        or ".." in path.split("/")
        or not _SAFE_PATH_RE.fullmatch(path)
    ):
        return _result(
            False, 400, "invalid_path", "Request path is invalid."
        )
    if not isinstance(max_body_bytes, int) or max_body_bytes < 0:
        return _result(
            False, 500, "invalid_security_config",
            "Request-size policy is incorrectly configured."
        )
    if content_length is not None:
        if (
            isinstance(content_length, bool)
            or not isinstance(content_length, int)
            or content_length < 0
        ):
            return _result(
                False, 400, "invalid_content_length",
                "Content-Length is invalid."
            )
        if content_length > max_body_bytes:
            return _result(
                False, 413, "request_too_large",
                "Request body exceeds the configured size limit."
            )
    write_methods = {"POST", "PUT", "PATCH"}
    normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
    if (
        require_json_for_write_methods
        and method in write_methods
        and path.startswith("/api/")
        and normalized_type != "application/json"
    ):
        return _result(
            False, 415, "unsupported_media_type",
            "This API endpoint requires application/json."
        )
    if is_protected_path(path, protected_prefixes) and not authenticated:
        return _result(
            False, 401, "authentication_required",
            "Authentication is required for this endpoint."
        )
    if rate_limiter is not None:
        if not isinstance(client_id, str) or not client_id.strip():
            return _result(
                False, 400, "missing_client_identity",
                "A trusted client identity is required for rate limiting."
            )
        try:
            rate_result = rate_limiter.check(client_id.strip())
        except Exception:
            # Fail closed if the configured limiter is broken.
            return _result(
                False, 503, "rate_limiter_unavailable",
                "Request protection is temporarily unavailable."
            )
        if not getattr(rate_result, "allowed", False):
            return _result(
                False, 429, "rate_limit_exceeded",
                "Too many requests. Please try again later."
            )
    return _result(
        True, 200, "request_allowed",
        "Request passed the configured metadata checks."
    )
def get_trusted_client_id(
    *,
    direct_client_host: Optional[str],
) -> Optional[str]:
    """
    Use the direct connection host supplied by the ASGI server.
    Do not pass X-Forwarded-For or other client-controlled headers here
    unless a trusted reverse proxy has validated and normalized them.
    """
    if not isinstance(direct_client_host, str):
        return None
    host = direct_client_host.strip()
    if not host or len(host) > 255:
        return None
    if any(character in host for character in ("\r", "\n", "\x00")):
        return None
    return host
def protect_api_request(**kwargs: Any) -> dict[str, Any]:
    """
    Dictionary-returning wrapper for applications that prefer plain
    dictionaries instead of APIProtectionResult objects.
    """
    return validate_api_request(**kwargs).to_dict()
if __name__ == "__main__":
    # Local self-test only. No network requests are made.
    valid = validate_api_request(
        method="GET",
        path="/api/chat",
        authenticated=False,
    )
    assert valid.allowed
    blocked_method = validate_api_request(
        method="TRACE",
        path="/api/chat",
    )
    assert not blocked_method.allowed
    assert blocked_method.status_code == 405
    blocked_admin = validate_api_request(
        method="GET",
        path="/api/admin/status",
        authenticated=False,
    )
    assert not blocked_admin.allowed
    assert blocked_admin.status_code == 401
    oversized = validate_api_request(
        method="POST",
        path="/api/chat",
        content_type="application/json",
        content_length=DEFAULT_MAX_BODY_BYTES + 1,
    )
    assert not oversized.allowed
    assert oversized.status_code == 413
    invalid_path = validate_api_request(
        method="GET",
        path="/api/../admin",
    )
    assert not invalid_path.allowed
    print("PASS: API protection self-tests completed.")