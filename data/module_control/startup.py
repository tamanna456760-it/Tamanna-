"""Module control startup."""

import logging

logger = logging.getLogger(__name__)


def startup_scan():
    logger.info("Module control startup scan")
    return {"status": "ok", "modules": []}


__all__ = ["startup_scan"]
