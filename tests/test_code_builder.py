"""Security and regression tests for the code builder."""

from pathlib import Path

import pytest

from tamanna_ai.code_builder import IntelligentCodeBuilder


def test_apply_requires_explicit_confirmation(tmp_path: Path):
    builder = IntelligentCodeBuilder(tmp_path)

    result = builder.apply_write("src/new.py", "value = 1\n")

    assert result["status"] == "confirmation_required"
    assert result["applied"] is False
    assert not (tmp_path / "src/new.py").exists()


def test_apply_writes_valid_python_atomically(tmp_path: Path):
    builder = IntelligentCodeBuilder(tmp_path)

    result = builder.apply_write(
        "src/new.py", "value = 42\n", confirm=True
    )

    assert result["applied"] is True
    assert (tmp_path / "src/new.py").read_text() == "value = 42\n"
    assert result["bytes_written"] == len("value = 42\n".encode())


def test_apply_rejects_invalid_python_without_creating_file(tmp_path: Path):
    builder = IntelligentCodeBuilder(tmp_path)

    with pytest.raises(ValueError, match="syntax error"):
        builder.apply_write("broken.py", "def broken(:\n", confirm=True)

    assert not (tmp_path / "broken.py").exists()


@pytest.mark.parametrize(
    "path",
    ["../outside.py", "/tmp/outside.py", ".env", ".env.production", ".git/config"],
)
def test_builder_rejects_unsafe_paths(tmp_path: Path, path: str):
    builder = IntelligentCodeBuilder(tmp_path)

    with pytest.raises(ValueError):
        builder.apply_write(path, "unsafe = True\n", confirm=True)


def test_builder_rejects_oversized_content(tmp_path: Path):
    builder = IntelligentCodeBuilder(tmp_path)
    content = "x" * (builder.MAX_CONTENT_BYTES + 1)

    with pytest.raises(ValueError, match="1 MB"):
        builder.propose_write("large.txt", content)


def test_inspect_reports_real_line_and_byte_counts(tmp_path: Path):
    target = tmp_path / "sample.py"
    target.write_text("one = 1\ntwo = 2\n", encoding="utf-8")

    result = IntelligentCodeBuilder(tmp_path).inspect("sample.py")

    assert result["status"] == "ok"
    assert result["lines"] == 2
    assert result["size_bytes"] == target.stat().st_size


def test_scan_reports_actual_python_syntax_errors(tmp_path: Path):
    (tmp_path / "valid.py").write_text("answer = 42\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("not python !!!", encoding="utf-8")

    result = IntelligentCodeBuilder(tmp_path).scan_project()

    assert result["python_files"] == 2
    assert result["syntax_errors"] == 1
    assert result["errors"][0]["path"] == "broken.py"
