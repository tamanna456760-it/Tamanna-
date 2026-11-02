"""Regression tests for the Docker/Nginx deployment preflight."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_deployment_preflight_matches_current_compose_architecture():
    result = subprocess.run(
        [sys.executable, str(ROOT / "deploy" / "preflight.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: Docker Compose defines" in result.stdout
    assert "DNS, certificate issuance" in result.stdout
    assert "API rate limits" in result.stdout
