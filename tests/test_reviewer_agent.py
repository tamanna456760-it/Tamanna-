"""Regression tests for bounded, read-only ReviewerAgent checks."""
import pytest

from tamanna_ai.agents.reviewer import ReviewerAgent


@pytest.fixture
def reviewer():
    return ReviewerAgent()


def test_accepts_safe_python_source(reviewer):
    result = reviewer.review_python("answer = 42\n")
    assert result["passed"] is True
    assert result["findings"] == []


@pytest.mark.parametrize("source", [None, 42, [], {}])
def test_rejects_non_text_source(reviewer, source):
    result = reviewer.review_python(source)
    assert result["passed"] is False
    assert result["findings"][0]["message"] == "Python source must be text."


def test_rejects_empty_source(reviewer):
    assert reviewer.review_python("  \n")["passed"] is False


def test_reports_syntax_error_location(reviewer):
    result = reviewer.review_python("def broken(:\n pass\n")
    assert result["passed"] is False
    assert result["findings"][0]["line"] == 1


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("eval(user_value)", "eval"),
        ("exec(code)", "exec"),
        ("import os\nos.system(command)", "os.system"),
        ("import subprocess\nsubprocess.run(command, shell=True)", "shell=True"),
        ("import pickle\npickle.loads(data)", "pickle"),
        ("import yaml\nyaml.load(data)", "yaml.load"),
    ],
)
def test_flags_selected_risky_calls(reviewer, source, expected):
    result = reviewer.review_python(source)
    assert result["passed"] is False
    assert any(expected in item["message"] for item in result["findings"])


def test_input_is_informational_not_blocking(reviewer):
    result = reviewer.review_python("value = input()")
    assert result["passed"] is True
    assert result["findings"][0]["severity"] == "info"


def test_rejects_oversized_source(reviewer):
    result = reviewer.review_python("x" * (reviewer.MAX_SOURCE_BYTES + 1))
    assert result["passed"] is False
    assert "byte limit" in result["findings"][0]["message"]


def test_rejects_invalid_unicode_source(reviewer):
    result = reviewer.review_python("\ud800")
    assert result["passed"] is False
    assert "Unicode" in result["findings"][0]["message"]


def test_reviews_python_file(tmp_path, reviewer):
    path = tmp_path / "sample.py"
    path.write_text("value = 3\n", encoding="utf-8")
    result = reviewer.review_file(path)
    assert result["passed"] is True
    assert result["path"] == str(path)


def test_rejects_non_python_file(tmp_path, reviewer):
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    assert reviewer.review_file(path)["passed"] is False


def test_rejects_missing_file(tmp_path, reviewer):
    assert reviewer.review_file(tmp_path / "missing.py")["passed"] is False


def test_rejects_invalid_utf8_file(tmp_path, reviewer):
    path = tmp_path / "bad.py"
    path.write_bytes(b"\xff\xfe")
    result = reviewer.review_file(path)
    assert "UTF-8" in result["findings"][0]["message"]


def test_rejects_oversized_file(tmp_path, reviewer):
    path = tmp_path / "large.py"
    path.write_bytes(b"x" * (reviewer.MAX_SOURCE_BYTES + 1))
    assert "byte limit" in reviewer.review_file(path)["findings"][0]["message"]


def test_rejects_invalid_path_type(reviewer):
    assert reviewer.review_file(123)["passed"] is False


def test_review_does_not_modify_file(tmp_path, reviewer):
    path = tmp_path / "readonly.py"
    original = b"answer = 99\n"
    path.write_bytes(original)
    reviewer.review_file(path)
    assert path.read_bytes() == original
