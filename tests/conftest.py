"""Shared pytest configuration for running tests from the repository root.

The CI workflow invokes pytest as a console script. Explicitly add the
repository root so top-level packages (tamanna_ai, data, modules) resolve
consistently across local and CI environments.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ROOT_STRING = str(REPOSITORY_ROOT)

if ROOT_STRING not in sys.path:
    sys.path.insert(0, ROOT_STRING)
