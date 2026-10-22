import os
from fastapi import Header, HTTPException, status


def verify_admin_key(x_api_key: str = Header(None)):
    """Verify X-API-KEY header matches TAMANNA_ADMIN_API_KEY environment variable.

    - If TAMANNA_ADMIN_API_KEY is not set, the admin API is considered disabled (503).
    - If header missing -> 401.
    - If header invalid -> 403.

    Safe, minimal implementation. Does not log secrets.
    """

    admin_key = os.getenv("TAMANNA_ADMIN_API_KEY")

    if not admin_key:
        # Admin API disabled by configuration
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API disabled",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if x_api_key != admin_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return True
