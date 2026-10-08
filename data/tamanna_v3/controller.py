"""Tamanna V3 startup."""

import logging

logger = logging.getLogger(__name__)


def startup():
    logger.info("Tamanna V3 startup")
    return {"status": "ok"}


__all__ = ["startup"]
