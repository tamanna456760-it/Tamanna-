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
