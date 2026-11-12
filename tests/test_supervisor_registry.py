from tamanna_ai.supervisors.registry import build_supervisor_registry

def test_every_file_has_one_section_owner_and_five_specialist_reviewers(tmp_path):
    (tmp_path / "tamanna_ai" / "security").mkdir(parents=True)
    (tmp_path / "tamanna_ai" / "security" / "audit.py").write_text("pass\n")
    (tmp_path / "Main.py").write_text("pass\n")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")

    registry = build_supervisor_registry(tmp_path)

    assert registry["tracked_file_count"] == 3
    assert registry["specialists_per_section"] == 5
    assert set(registry["file_owners"]) == {"Main.py", "tamanna_ai/security/audit.py", ".github/workflows/ci.yml"}
    assert registry["file_owners"][".github/workflows/ci.yml"]["section_supervisor"] == "supervisor_ci"
    for owner in registry["file_owners"].values():
        assert owner["section_supervisor"].startswith("supervisor_")
        assert len(owner["specialist_reviewers"]) == 5

def test_supervisors_cannot_grant_themselves_production_permissions(tmp_path):
    registry = build_supervisor_registry(tmp_path)
    assert registry["permissions"]["read_only_by_default"] is True
    assert registry["permissions"]["self_grant_permissions"] is False
    assert registry["permissions"]["production_changes_require_separate_human_approval"] is True
