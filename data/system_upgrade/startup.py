"""System upgrade startup."""

import logging

logger = logging.getLogger(__name__)


def startup():
    logger.info("System upgrade startup")
    return {"status": "ok"}


__all__ = ["startup"]
