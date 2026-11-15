from tamanna_ai.api.routes import api_router


def test_coding_assistant_api_route_is_registered():
    route = next(
        route for route in api_router.routes
        if getattr(route, "path", None) == "/tamanna-ai/coding/{action}"
    )
    assert "POST" in route.methods
