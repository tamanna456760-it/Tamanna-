"""Regression checks for privileged FastAPI routes."""

import Main


def _route(path, method="POST"):
    matches = [
        route for route in Main.app.routes
        if getattr(route, "path", None) == path
        and method in getattr(route, "methods", set())
    ]
    assert len(matches) == 1, f"expected one route for {method} {path}"
    return matches[0]


def _dependency_names(route):
    return {
        dependency.call.__name__
        for dependency in route.dependant.dependencies
        if getattr(dependency, "call", None) is not None
    }


def test_skill_mutation_routes_require_admin_key():
    for path in (
        "/api/skills/create",
        "/api/skills/test",
        "/api/skills/refine",
    ):
        assert "verify_admin_key" in _dependency_names(_route(path))


def test_controller_echo_route_requires_admin_key():
    assert "verify_admin_key" in _dependency_names(
        _route("/api/tamanna/echo")
    )


def test_existing_high_risk_routes_remain_protected():
    for path in (
        "/api/code-builder/apply",
        "/api/linux/run",
        "/api/linux/shell",
        "/api/self-healing/cycle",
        "/api/autonomous/build",
        "/api/autonomous/repair",
        "/api/command",
        "/api/code-builder/build",
        "/api/code-builder/compile",
    ):
        assert "verify_admin_key" in _dependency_names(_route(path))


def test_project_inspection_routes_require_admin_key():
    for path in (
        "/api/code-builder/status",
        "/api/code-builder/scan",
        "/api/code-builder/inspect",
        "/api/code-builder/propose",
        "/api/linux/tools",
        "/api/security/tools",
        "/api/tamanna/system",
        "/api/linux/shell/status",
        "/api/autonomous/think",
        "/api/autonomous/files",
        "/api/autonomous/startup",
        "/api/autonomous/plans",
        "/api/autonomous/repair/status",
        "/api/autonomous/repair/history",
        "/api/autonomous/status",
        "/api/code-builder/project",
        "/api/unified/project",
    ):
        method = "POST" if path in (
            "/api/code-builder/inspect",
            "/api/code-builder/propose",
        ) else "GET"
        assert "verify_admin_key" in _dependency_names(
            _route(path, method)
        )


def test_autonomous_planning_route_requires_admin_key():
    assert "verify_admin_key" in _dependency_names(
        _route("/api/autonomous/plan")
    )


def test_public_chat_and_health_routes_remain_available():
    assert "verify_admin_key" not in _dependency_names(
        _route("/api/chat")
    )
    assert "verify_admin_key" not in _dependency_names(
        _route("/health", "GET")
    )


def test_self_improvement_analysis_requires_admin_key():
    assert "verify_admin_key" in _dependency_names(
        _route("/api/self-improvement/analyze", "POST")
    )


def test_code_builder_plan_requires_admin_key():
    assert "verify_admin_key" in _dependency_names(
        _route("/api/code-builder/plan", "POST")
    )
