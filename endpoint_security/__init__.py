"""Tamanna AI Endpoint Security package.
Owner: HM INSAN ALI
This package starts in monitor-only mode.
It does not kill processes, quarantine files, or modify system settings.
"""
__version__ = "1.0.0"
__author__ = "HM INSAN ALI"
PROJECT_NAME = "Tamanna AI"
COMPONENT_NAME = "Endpoint Security"
DEFAULT_MODE = "monitor_only"
__all__ = [
    "__version__",
    "__author__",
    "PROJECT_NAME",
    "COMPONENT_NAME",
    "DEFAULT_MODE",
]