from tamanna_ai.supervisors.runtime import _agent_prompt, _team_definition
from tamanna_ai.supervisors.registry import build_supervisor_registry


def test_all_six_agents_get_readonly_reviewer_or_writer_policy(tmp_path):
    registry = build_supervisor_registry(tmp_path)
    name, specialists = _team_definition(registry, "defense")
    assert name == "Tamanna Defense and Security Team"
    assert len(specialists) == 100
    assert all(capability == "defensive_analysis" for _role, _responsibility, capability in specialists)
    writer = _agent_prompt(name, "implementation", "code changes", "Fix a bug", True)
    reviewer = _agent_prompt(name, "security", "security review", "Review a bug", False)
    assert "sole implementation worker" in writer
    assert "isolated Git worktree" in writer
    assert "read-only reviewer" in reviewer
    assert "Do not edit files" in reviewer


def test_team_lookup_rejects_unknown_team(tmp_path):
    from fastapi import HTTPException
    registry = build_supervisor_registry(tmp_path)
    try:
        _team_definition(registry, "does_not_exist")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("unknown team must be rejected")
