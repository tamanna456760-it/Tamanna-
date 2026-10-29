
from pathlib import Path

from data.advanced_code_builder import AdvancedCodeBuilder


def test_discover_reports_project_root(tmp_path: Path):
    builder = AdvancedCodeBuilder(tmp_path)
    result = builder.discover()

    assert result["ok"] is True
    assert result["project_root"] == str(tmp_path.resolve())


def test_build_creates_new_python_file(tmp_path: Path):
    builder = AdvancedCodeBuilder(tmp_path)
    result = builder.build([
        {"path": "sample.py", "content": "answer = 42\n"}
    ])

    assert result.ok is True
    assert (tmp_path / "sample.py").read_text() == "answer = 42\n"


def test_build_does_not_overwrite_by_default(tmp_path: Path):
    target = tmp_path / "sample.py"
    target.write_text("original = True\n")
    builder = AdvancedCodeBuilder(tmp_path)

    result = builder.build([
        {"path": "sample.py", "content": "changed = True\n"}
    ])

    assert target.read_text() == "original = True\n"
    assert result.warnings


def test_build_rejects_invalid_python(tmp_path: Path):
    builder = AdvancedCodeBuilder(tmp_path)
    result = builder.build([
        {"path": "broken.py", "content": "def broken(:\n"}
    ])

    assert result.ok is False
    assert not (tmp_path / "broken.py").exists()


def test_build_rejects_path_traversal(tmp_path: Path):
    builder = AdvancedCodeBuilder(tmp_path)
    result = builder.build([
        {"path": "../outside.py", "content": "safe = True\n"}
    ])

    assert result.ok is False
    assert not (tmp_path.parent / "outside.py").exists()
