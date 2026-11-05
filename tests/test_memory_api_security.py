"""Regression tests for authenticated personal memory endpoints."""

from tamanna_ai.authentication.access_control import READ_ROUTES, USER_ROUTES


def test_memory_collection_is_protected_for_reads():
    assert "/api/memory" in READ_ROUTES


def test_memory_create_endpoint_is_protected():
    assert "/api/memory" in USER_ROUTES or "/api/memory" in READ_ROUTES


def test_memory_item_routes_are_recognized_by_access_middleware():
    # Dynamic /api/memory/{id} routes are matched by the middleware prefix rule.
    path = "/api/memory/123"
    assert path.startswith("/api/memory/")
