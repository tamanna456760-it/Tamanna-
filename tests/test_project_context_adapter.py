from modules.tamanna.project_context_adapter import (
    build_project_context,
    format_response,
)


def test_project_context_finds_relevant_file_and_excludes_env(tmp_path):
    (tmp_path / "README.md").write_text("Tamanna project overview", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=must-not-appear", encoding="utf-8")
    (tmp_path / "config.py").write_text("APP_NAME = 'Tamanna'", encoding="utf-8")

    result = build_project_context(tmp_path, "Tamanna config")

    paths = [item["path"] for item in result["relevant_files"]]
    assert "README.md" in paths
    assert ".env" not in paths
    assert all("SECRET" not in item["content"] for item in result["relevant_files"])


def test_project_context_rejects_missing_root(tmp_path):
    try:
        build_project_context(tmp_path / "missing", "test")
    except NotADirectoryError:
        pass
    else:
        raise AssertionError("Missing project root must be rejected")


def test_format_response_normalizes_dict_and_string():
    mapped = format_response({"response": "Hello"}, "Hi")
    assert mapped["reply"] == "Hello"
    assert mapped["type"] == "chat"
    assert mapped["input"] == "Hi"

    plain = format_response("Hello", "Hi")
    assert plain["ok"] is True
    assert plain["reply"] == "Hello"
