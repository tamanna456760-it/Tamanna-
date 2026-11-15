"""Regression checks keeping administrator tools out of the user chat UI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_admin_model_controls_are_not_embedded_in_user_chat():
    chat = (ROOT / "index.html").read_text(encoding="utf-8")
    admin = (ROOT / "admin.html").read_text(encoding="utf-8")
    for label in (
        "Host Performance Monitor",
        "Loaded Model Resource Manager",
        "Local Model Recovery Assistant",
        "Run Model Benchmark",
    ):
        assert label not in chat
        assert label in admin
    assert "/js/model-health.js" not in chat
    assert "/js/model-health.js" in admin


def test_admin_workspace_is_hidden_until_backend_verifies_role():
    admin = (ROOT / "admin.html").read_text(encoding="utf-8")
    admin_js = (ROOT / "js/admin.js").read_text(encoding="utf-8")
    assert '<section id="adminContent" hidden>' in admin
    assert "window.TamannaAdminVerified=true" in admin_js
    assert 'new Event("tamanna:admin-verified")' in admin_js
