"""Tests for private TI-SERVER runtime configuration loading."""
import json

import pytest

from tamanna_ai.private_runtime_config import (
    PrivateRuntimeConfigError,
    load_private_runtime_config,
    private_runtime_summary,
)


def _write_config(tmp_path, data):
    path = tmp_path / "private-runtime.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid_config():
    return {
        "schema_version": 1,
        "backend": {
            "base_url": "https://api.example.test",
            "health_path": "/health",
        },
        "admin": {"overview_path": "/api/admin/overview"},
        "timeouts": {"connect_seconds": 5, "read_seconds": 20},
    }


def test_missing_private_config_uses_safe_defaults(tmp_path):
    result = load_private_runtime_config(tmp_path / "missing.json")
    assert result["status"] == "not_configured"
    assert result["loaded"] is False
    assert result["backend"]["health_path"] == "/health"


def test_valid_private_runtime_config_loads(tmp_path):
    path = _write_config(tmp_path, _valid_config())
    result = load_private_runtime_config(path)
    assert result["status"] == "loaded"
    assert result["backend"]["base_url"] == "https://api.example.test"
    assert result["timeouts"] == {"connect_seconds": 5, "read_seconds": 20}


def test_summary_does_not_expose_backend_url_or_local_path(tmp_path):
    path = _write_config(tmp_path, _valid_config())
    summary = private_runtime_summary(load_private_runtime_config(path))
    serialized = json.dumps(summary)
    assert summary["loaded"] is True
    assert summary["backend_url_configured"] is True
    assert summary["secrets_exposed"] is False
    assert "api.example.test" not in serialized
    assert str(tmp_path) not in serialized


@pytest.mark.parametrize("url", [
    "http://api.example.test",
    "https://user:password@api.example.test",
    "https://api.example.test/path?token=abc",
    "file:///etc/passwd",
])
def test_rejects_unsafe_backend_urls(tmp_path, url):
    data = _valid_config()
    data["backend"]["base_url"] = url
    with pytest.raises(PrivateRuntimeConfigError):
        load_private_runtime_config(_write_config(tmp_path, data))


@pytest.mark.parametrize("field,value", [
    ("health_path", "//evil.example/health"),
    ("health_path", "/health/../admin"),
    ("health_path", "https://evil.example/health"),
])
def test_rejects_unsafe_backend_paths(tmp_path, field, value):
    data = _valid_config()
    data["backend"][field] = value
    with pytest.raises(PrivateRuntimeConfigError):
        load_private_runtime_config(_write_config(tmp_path, data))


def test_rejects_secret_material_in_runtime_config(tmp_path):
    data = _valid_config()
    data["credentials"] = {"api_key": "must-not-be-here"}
    with pytest.raises(PrivateRuntimeConfigError, match="Secret-like field"):
        load_private_runtime_config(_write_config(tmp_path, data))


@pytest.mark.parametrize("timeout", [0, -1, 31, True, "5"])
def test_rejects_invalid_connect_timeout(tmp_path, timeout):
    data = _valid_config()
    data["timeouts"]["connect_seconds"] = timeout
    with pytest.raises(PrivateRuntimeConfigError):
        load_private_runtime_config(_write_config(tmp_path, data))


def test_rejects_unknown_schema_and_invalid_json(tmp_path):
    path = _write_config(tmp_path, {"schema_version": 2})
    with pytest.raises(PrivateRuntimeConfigError, match="schema"):
        load_private_runtime_config(path)
    path.write_text("{invalid", encoding="utf-8")
    with pytest.raises(PrivateRuntimeConfigError, match="valid UTF-8 JSON"):
        load_private_runtime_config(path)
