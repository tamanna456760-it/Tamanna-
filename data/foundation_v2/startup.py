"""Foundation V2 startup."""

import logging

logger = logging.getLogger(__name__)


def startup():
    logger.info("Foundation V2 startup")
    return {"status": "ok"}


__all__ = ["startup"]
