"""Tests for fail-closed admin API authentication."""

import pytest
from fastapi import HTTPException

from app_security.auth import verify_admin_key


def test_admin_api_is_disabled_without_server_key(monkeypatch):
    monkeypatch.delenv("TAMANNA_ADMIN_API_KEY", raising=False)
    with pytest.raises(HTTPException) as exc:
        verify_admin_key(None)
    assert exc.value.status_code == 503


def test_admin_api_rejects_missing_and_invalid_keys(monkeypatch):
    monkeypatch.setenv("TAMANNA_ADMIN_API_KEY", "unit-test-admin-secret")
    with pytest.raises(HTTPException) as missing:
        verify_admin_key(None)
    assert missing.value.status_code == 401

    with pytest.raises(HTTPException) as invalid:
        verify_admin_key("wrong-unit-test-key")
    assert invalid.value.status_code == 403


def test_admin_api_accepts_configured_key(monkeypatch):
    monkeypatch.setenv("TAMANNA_ADMIN_API_KEY", "unit-test-admin-secret")
    assert verify_admin_key("unit-test-admin-secret") is True
