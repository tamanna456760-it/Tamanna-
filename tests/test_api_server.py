"""Smoke tests for Tamanna package API."""

from fastapi.testclient import TestClient
from tamanna_ai.api.server import create_app


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
