"""Tests for runner build endpoint authentication and execution safety."""

import runner.python.server as runner_server


def test_health_endpoint_is_public():
    client = runner_server.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_build_endpoint_rejects_missing_token(monkeypatch):
    monkeypatch.setenv("TAMANNA_RUNNER_API_KEY", "test-only-secret")
    client = runner_server.app.test_client()
    response = client.post("/build")
    assert response.status_code == 401


def test_build_endpoint_requires_configured_token(monkeypatch):
    monkeypatch.delenv("TAMANNA_RUNNER_API_KEY", raising=False)
    client = runner_server.app.test_client()
    response = client.post("/build", headers={"X-API-KEY": "anything"})
    assert response.status_code == 401


def test_build_endpoint_does_not_fake_a_build(monkeypatch):
    monkeypatch.setenv("TAMANNA_RUNNER_API_KEY", "test-only-secret")
    client = runner_server.app.test_client()
    response = client.post("/build", headers={"X-API-KEY": "test-only-secret"})
    assert response.status_code == 501
    assert response.get_json()["status"] == "not_implemented"
