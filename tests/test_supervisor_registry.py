from tamanna_ai.supervisors.registry import build_supervisor_registry

def test_every_file_has_one_section_owner_and_five_specialist_reviewers(tmp_path):
    (tmp_path / "tamanna_ai" / "security").mkdir(parents=True)
    (tmp_path / "tamanna_ai" / "security" / "audit.py").write_text("pass\n")
    (tmp_path / "Main.py").write_text("pass\n")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
    (tmp_path / "deploy").mkdir()
    (tmp_path / "deploy" / "service.yml").write_text("service: api\\n")

    registry = build_supervisor_registry(tmp_path)

    assert registry["tracked_file_count"] == 4
    assert registry["specialists_per_section"] == 5
    assert set(registry["file_owners"]) == {"Main.py", "tamanna_ai/security/audit.py", ".github/workflows/ci.yml", "deploy/service.yml"}
    assert registry["file_owners"][".github/workflows/ci.yml"]["section_supervisor"] == "supervisor_ci"
    assert registry["file_owners"]["tamanna_ai/security/audit.py"]["defense_team"] == "defense"
    assert registry["file_owners"]["deploy/service.yml"]["server_operations_team"] == "server_ops"
    for owner in registry["file_owners"].values():
        assert owner["section_supervisor"].startswith("supervisor_")
        assert len(owner["specialist_reviewers"]) == 5

def test_supervisors_cannot_grant_themselves_production_permissions(tmp_path):
    registry = build_supervisor_registry(tmp_path)
    assert registry["permissions"]["read_only_by_default"] is True
    assert registry["permissions"]["self_grant_permissions"] is False
    assert registry["permissions"]["production_changes_require_separate_human_approval"] is True

def test_dedicated_teams_have_five_specialists_each(tmp_path):
    registry = build_supervisor_registry(tmp_path)
    teams = registry["cross_cutting_teams"]
    assert set(teams) == {"defense", "server_operations"}
    assert len(teams["defense"]["specialists"]) == 5
    assert len(teams["server_operations"]["specialists"]) == 5
    assert registry["runtime"]["workers_started"] is False

def test_defense_team_has_exactly_100_specialists_in_ten_squads(tmp_path):
    from tamanna_ai.supervisors.registry import DEFENSE_SPECIALISTS, DEFENSE_SQUADS
    registry = build_supervisor_registry(tmp_path)
    defense = registry["cross_cutting_teams"]["defense"]
    assert len(DEFENSE_SPECIALISTS) == 100
    assert len(DEFENSE_SQUADS) == 10
    assert all(len(squad["agents"]) == 10 for squad in DEFENSE_SQUADS)
    assert defense["specialists_count"] == 100
    assert defense["supervisor_id"] == "supervisor_defense"
    assert registry["permissions"]["production_changes_require_separate_human_approval"] is True


def test_defense_team_is_not_authorized_to_counterattack(tmp_path):
    from tamanna_ai.supervisors.registry import DEFENSE_SPECIALISTS
    assert all(capability == "defensive_analysis" for _role, _description, capability in DEFENSE_SPECIALISTS)
