"""API tests for the admin-only antivirus upload endpoint."""
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tamanna_ai.api import routes
from tamanna_ai.api.server import create_app


def _client(monkeypatch, scan_result=None, admin=True):
    monkeypatch.setattr(routes, "check_origin", lambda request: None)
    monkeypatch.setattr(routes, "rate_limit_user_action", lambda *args, **kwargs: None)
    if admin:
        monkeypatch.setattr(
            routes, "_require_model_admin",
            lambda token: {"id": "admin-user"},
        )
    else:
        def deny(token):
            raise HTTPException(status_code=403, detail="admin only")
        monkeypatch.setattr(routes, "_require_model_admin", deny)

    if scan_result is not None:
        def fake_scan(self, path):
            assert path.is_file()
            assert path.read_bytes() == b"sample upload"
            return dict(scan_result)
        monkeypatch.setattr(routes.AntivirusScanner, "scan_file", fake_scan)
    return TestClient(create_app())


def test_admin_upload_clean_file_is_scanned_and_not_stored(monkeypatch):
    client = _client(
        monkeypatch,
        {
            "scanner": "Tamanna AI Antivirus",
            "status": "clean",
            "path": "/tmp/private-temp-path",
            "message": "no malware detected by ClamAV",
        },
    )
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("../sample.txt", b"sample upload", "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["filename"] == "sample.txt"
    assert body["stored"] is False
    assert body["executed"] is False
    assert "path" not in body["scan"]


def test_infected_upload_is_reported_not_executed(monkeypatch):
    client = _client(
        monkeypatch,
        {
            "scanner": "Tamanna AI Antivirus",
            "status": "infected",
            "path": "/tmp/private-temp-path",
            "message": "Test-Malware-Signature",
        },
    )
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("sample.bin", b"sample upload", "application/octet-stream")},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["scan"]["status"] == "infected"
    assert response.json()["executed"] is False


def test_antivirus_upload_requires_admin(monkeypatch):
    client = _client(monkeypatch, admin=False)
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("sample.txt", b"sample upload", "text/plain")},
    )
    assert response.status_code == 403


def test_antivirus_upload_rejects_oversized_file(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("large.bin", b"x" * (10 * 1024 * 1024 + 1), "application/octet-stream")},
    )
    assert response.status_code == 413


def test_antivirus_upload_rejects_empty_file(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 422


def test_antivirus_upload_fails_closed_when_engine_unavailable(monkeypatch):
    client = _client(
        monkeypatch,
        {
            "scanner": "Tamanna AI Antivirus",
            "status": "engine_unavailable",
            "path": "/tmp/private-temp-path",
            "message": "ClamAV not found",
        },
    )
    response = client.post(
        "/tamanna-ai/security/antivirus/scan-upload",
        files={"file": ("sample.txt", b"sample upload", "text/plain")},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["message"] == "Antivirus scan could not be verified."
