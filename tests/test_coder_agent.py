"""Regression tests for the read-only CoderAgent."""
import pytest

from tamanna_ai.agents.coder import CoderAgent


@pytest.fixture
def coder():
    return CoderAgent()


def test_validates_python_without_execution(coder):
    result = coder.validate_python("value = 42\n")
    assert result["valid"] is True
    assert result["error"] is None


@pytest.mark.parametrize("source", [None, 42, [], {}])
def test_rejects_non_text_source(coder, source):
    result = coder.validate_python(source)
    assert result["valid"] is False
    assert result["error"] == "Python source must be text."


def test_rejects_empty_source(coder):
    assert coder.validate_python("  \n")["error"] == "Python source is empty."


def test_reports_syntax_error_location(coder):
    result = coder.validate_python("def broken(:\n    pass\n")
    assert result["valid"] is False
    assert result["line"] == 1
    assert isinstance(result["column"], int)


def test_rejects_oversized_source(coder):
    result = coder.validate_python("x" * (coder.MAX_SOURCE_BYTES + 1))
    assert result["valid"] is False
    assert "byte limit" in result["error"]


def test_validates_python_file(tmp_path, coder):
    path = tmp_path / "sample.py"
    path.write_text("answer = 42\n", encoding="utf-8")
    result = coder.validate_file(path)
    assert result["valid"] is True
    assert result["path"] == str(path)


def test_rejects_non_python_file(tmp_path, coder):
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    result = coder.validate_file(path)
    assert result["valid"] is False
    assert result["error"] == "Only Python files are supported."


def test_rejects_missing_file(tmp_path, coder):
    result = coder.validate_file(tmp_path / "missing.py")
    assert result["valid"] is False
    assert result["error"] == "Python file was not found."


def test_rejects_invalid_utf8_file(tmp_path, coder):
    path = tmp_path / "bad.py"
    path.write_bytes(b"\xff\xfe")
    result = coder.validate_file(path)
    assert result["valid"] is False
    assert result["error"] == "Python file must use UTF-8 encoding."


def test_rejects_oversized_file(tmp_path, coder):
    path = tmp_path / "large.py"
    path.write_bytes(b"x" * (coder.MAX_SOURCE_BYTES + 1))
    result = coder.validate_file(path)
    assert result["valid"] is False
    assert "byte limit" in result["error"]


def test_rejects_invalid_path_type(coder):
    result = coder.validate_file(123)
    assert result["valid"] is False
    assert result["error"] == "File path must be text or a Path."


def test_validation_does_not_modify_file(tmp_path, coder):
    path = tmp_path / "readonly.py"
    original = b"value = 10\n"
    path.write_bytes(original)
    coder.validate_file(path)
    assert path.read_bytes() == original
