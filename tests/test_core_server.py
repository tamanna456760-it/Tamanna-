
from fastapi.testclient import TestClient
from tamanna_ai.api.server import app


def test_package_api_health():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
