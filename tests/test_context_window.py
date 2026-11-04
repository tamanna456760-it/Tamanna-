from tamanna_ai.capabilities.context_window import estimate_tokens, fit_context_window


def test_estimate_tokens_is_positive_and_utf8_aware():
    assert estimate_tokens("hello") >= 1
    assert estimate_tokens("বাংলা") >= estimate_tokens("abc")


def test_context_window_preserves_system_and_current_request():
    result = fit_context_window(
        "SYSTEM RULES",
        [("old_history", "old " * 1000), ("recent_history", "recent " * 1000)],
        "CURRENT REQUEST",
        max_tokens=256,
    )
    prompt = result["prompt"]
    assert prompt.startswith("SYSTEM RULES")
    assert "CURRENT REQUEST" in prompt
    assert result["estimated_tokens"] <= result["max_tokens"]
    assert result["truncated_sections"]


def test_context_window_rejects_too_small_or_invalid_budget():
    import pytest

    with pytest.raises(ValueError):
        fit_context_window("system", [], "hello", max_tokens=10)
    with pytest.raises(TypeError):
        estimate_tokens(123)
