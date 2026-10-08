"""Master control startup."""

import logging

logger = logging.getLogger(__name__)


def startup():
    logger.info("Master control startup")
    return {"status": "ok"}


__all__ = ["startup"]
