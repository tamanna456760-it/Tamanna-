import importlib.util
import os
import subprocess
from pathlib import Path

ai_mod_path = (
    Path(__file__).resolve().parents[1]
    / "bd-king-r7"
    / "IT"
    / "apps"
    / "ai_sync_controller.py"
)
spec = importlib.util.spec_from_file_location(
    "ai_sync_controller", str(ai_mod_path))
ai_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_mod)
AIAutoSync = ai_mod.AIAutoSync


def test_load_config_defaults(tmp_path, monkeypatch):
    cfg_file = tmp_path / "missing-config.json"
    s = AIAutoSync(str(cfg_file))
    assert s.config["auto_sync"]["interval_seconds"] == 60
    assert s.config["code_fixing"]["auto_fix"] is True


def test_analyze_and_fix_runs_script_and_ai(monkeypatch, tmp_path):
    # create a dummy file
    f = tmp_path / "sample.py"
    f.write_text("print('hello')\n")

    s = AIAutoSync()

    # monkeypatch script presence and subprocess.run
    called = {}

    def fake_exists(path):
        # pretend script exists
        return True

    def fake_access(path, mode):
        return True

    def fake_run(cmd, check=False, **kwargs):
        called["ran"] = True

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(os.path, "exists", fake_exists)
    monkeypatch.setattr(os, "access", fake_access)
    monkeypatch.setattr(subprocess, "run", fake_run)

    # monkeypatch AI fixer to modify content
    def fake_ai(content, path):
        return content.replace("hello", "world")

    monkeypatch.setattr(AIAutoSync, "get_ai_fixes", staticmethod(fake_ai))

    s.analyze_and_fix_code(str(f))

    assert called.get("ran", False) is True
    assert "world" in f.read_text()
