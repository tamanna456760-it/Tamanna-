import json

from modules.tamanna.message_memory import search_message_fast


def test_search_returns_exact_approved_entry(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text(json.dumps({"entries": [
        {"question": "How do I reset my password?", "reply": "Use account recovery.", "category": "account", "approved": True},
    ]}), encoding="utf-8")

    result = search_message_fast("HOW do I reset my password?", path)

    assert result is not None
    assert result["reply"] == "Use account recovery."
    assert result["category"] == "account"
    assert result["score"] == 1.0


def test_search_ignores_unapproved_entries(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text(json.dumps([
        {"question": "What is Tamanna?", "reply": "Private draft", "approved": False},
    ]), encoding="utf-8")

    assert search_message_fast("What is Tamanna?", path) is None


def test_search_rejects_weak_match_and_invalid_file(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text(json.dumps([
        {"question": "Tamanna project server setup", "reply": "Answer", "approved": True},
    ]), encoding="utf-8")

    assert search_message_fast("weather tomorrow", path) is None
    assert search_message_fast("Tamanna", tmp_path / "missing.json") is None


def test_search_handles_malformed_json(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text("{broken", encoding="utf-8")

    assert search_message_fast("hello", path) is None
