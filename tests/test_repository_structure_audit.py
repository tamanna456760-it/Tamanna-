from pathlib import Path
from scripts.repository_structure_audit import audit_repository, render_markdown


def test_detects_misplaced_workflow_and_empty_python(tmp_path: Path):
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "ci.yml").write_text("name: ci\n", encoding="utf-8")
    (workflow / "helper.py").write_text("print('not a workflow')\n", encoding="utf-8")
    package = tmp_path / "sample"
    package.mkdir()
    (package / "empty.py").write_text("", encoding="utf-8")
    report = audit_repository(tmp_path)
    assert report["summary"]["files"] == 3
    assert report["workflow_non_workflow_files"] == [".github/workflows/helper.py"]
    assert report["empty_python_files"] == ["sample/empty.py"]


def test_ignores_generated_cache_directories(tmp_path: Path):
    cache = tmp_path / "sample" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.pyc").write_bytes(b"compiled")
    (tmp_path / "module.py").write_text("x = 1\n", encoding="utf-8")
    report = audit_repository(tmp_path)
    assert report["summary"]["files"] == 1
    assert report["summary"]["pyc_count"] == 0


def test_markdown_report_states_read_only_policy(tmp_path: Path):
    rendered = render_markdown(audit_repository(tmp_path))
    assert "Read-only report" in rendered
    assert "never moves" in rendered
