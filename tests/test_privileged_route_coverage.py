"""Regression tests for protected Tamanna API route coverage."""

from tamanna_ai.authentication.access_control import (
    ADMIN_ROUTES,
    BLOCKED_EXECUTION_ROUTES,
    USER_ROUTES,
)


def test_chat_and_project_planning_routes_require_authentication():
    protected = {
        "/api/chat",
        "/api/chat/master",
        "/api/history",
        "/api/skills/match",
        "/api/code-builder/inspect",
        "/api/autonomous/plan",
        "/api/code-builder/plan",
    }
    assert protected <= USER_ROUTES


def test_project_mutation_and_analysis_routes_require_admin():
    admin_only = {
        "/api/code-builder/inspect",
        "/api/autonomous/plan",
        "/api/code-builder/plan",
        "/api/self-improvement/analyze",
        "/api/code-builder/apply",
        "/api/command",
    }
    assert admin_only <= ADMIN_ROUTES


def test_command_execution_routes_remain_disabled_by_default():
    disabled = {
        "/api/linux/run",
        "/api/linux/shell",
        "/api/command",
        "/api/code-builder/build",
        "/api/code-builder/compile",
        "/api/autonomous/build",
        "/api/autonomous/repair",
        "/api/self-healing/cycle",
    }
    assert disabled <= BLOCKED_EXECUTION_ROUTES


def test_admin_routes_are_also_authenticated_routes():
    assert ADMIN_ROUTES <= USER_ROUTES
