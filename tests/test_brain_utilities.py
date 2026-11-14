import hashlib
import pytest
from tamanna_ai.brain.analyzer import analyze_source
from tamanna_ai.brain.decision import choose_action
from tamanna_ai.brain.fixer import replace_text
from tamanna_ai.brain.optimizer import suggest_optimizations
from tamanna_ai.brain.planner import create_plan

def test_analyzer_is_static_and_reports_eval():
    result = analyze_source("def f(x):\n    return eval(x)\n")
    assert result["syntax_valid"]
    assert result["security"]["count"] == 1
    assert not analyze_source("def broken(:")["syntax_valid"]

def test_decision_skips_disabled_and_uses_priority():
    result = choose_action([{"name":"off","priority":9,"enabled":False},{"name":"best","priority":3}])
    assert result["name"] == "best"
    assert choose_action([]) is None

def test_plan_is_pending_and_not_executed():
    plan = create_plan("Fix CI", ["inspect", "test"])
    assert plan["execution_started"] is False
    assert [x["status"] for x in plan["steps"]] == ["pending", "pending"]
    with pytest.raises(ValueError):
        create_plan(" ")

def test_optimizer_only_suggests():
    result = suggest_optimizations("items=[]\nfor i in range(5):\n items.append(i)\n")
    assert result["valid"] and result["modified_source"] is False
    assert result["suggestions"]

def test_fixer_dry_run_and_digest_guard(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("hello world", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    preview = replace_text(path, "world", "Tamanna", expected_sha256=digest)
    assert preview["dry_run"] and path.read_text() == "hello world"
    applied = replace_text(path, "world", "Tamanna", dry_run=False, expected_sha256=digest)
    assert applied["status"] == "updated" and path.read_text() == "hello Tamanna"
