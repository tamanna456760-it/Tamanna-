"""Regression tests for newly implemented core utility modules."""
import json
import zipfile

import pytest

from tamanna_ai.analysis.complexity import analyze_complexity
from tamanna_ai.analysis.performance import PerformanceMonitor
from tamanna_ai.analysis.security import scan_python_source
from tamanna_ai.backup.backup import create_backup
from tamanna_ai.backup.restore import inspect_backup, restore_backup
from tamanna_ai.learning.memory import LearningMemory
from tamanna_ai.learning.trainer import inspect_jsonl_dataset


def test_complexity_counts_branching_without_executing_source():
    result = analyze_complexity("def choose(x):\n    if x and x > 2:\n        return 1\n    return 0\n")
    assert result["functions"] == 1
    assert result["cyclomatic_complexity"] >= 3


def test_performance_monitor_records_and_bounds_samples():
    monitor = PerformanceMonitor(max_samples=2)
    monitor.record("a", 0.1)
    monitor.record("b", 0.2)
    monitor.record("c", 0.3)
    assert monitor.summary()["samples"] == 2
    assert monitor.summary()["total_seconds"] == pytest.approx(0.5)


def test_security_scan_is_static_and_reports_unsafe_calls():
    result = scan_python_source("eval(user_input)\n")
    assert result["valid"] is True
    assert result["findings"][0]["rule"] == "eval"
    assert scan_python_source("def broken(:")["valid"] is False


def test_backup_manifest_and_dry_run_restore(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "note.txt").write_text("safe note", encoding="utf-8")
    (source / ".env").write_text("SECRET=not-backed-up", encoding="utf-8")
    archive = tmp_path / "backup.zip"
    result = create_backup(source, archive)
    assert result["files"] == 1
    assert inspect_backup(archive)["status"] == "valid"
    destination = tmp_path / "restore"
    dry = restore_backup(archive, destination)
    assert dry["dry_run"] is True
    assert not destination.exists()
    restored = restore_backup(archive, destination, dry_run=False)
    assert restored["restored"] == 1
    assert (destination / "note.txt").read_text(encoding="utf-8") == "safe note"
    assert not (destination / ".env").exists()


def test_restore_rejects_path_traversal_archive(tmp_path):
    archive = tmp_path / "malicious.zip"
    with zipfile.ZipFile(archive, "w") as item:
        item.writestr("../escape.txt", "no")
        item.writestr("MANIFEST.json", json.dumps({
            "version": 1,
            "files": [{"path": "../escape.txt", "sha256": "bad"}],
        }))
    with pytest.raises(ValueError, match="Unsafe path"):
        inspect_backup(archive)


def test_learning_memory_is_user_scoped_and_deduplicates():
    class FakeStore:
        def __init__(self):
            self.rows = {1: [], 2: []}
            self.next_id = 1

        def list_memory_records(self, *, user_id, limit):
            return self.rows[user_id][-limit:]

        def add_memory(self, content, *, user_id, metadata):
            item = {"id": self.next_id, "content": content, "metadata": metadata}
            self.next_id += 1
            self.rows[user_id].append(item)
            return item["id"]

        def delete_memory(self, memory_id, *, user_id):
            before = len(self.rows[user_id])
            self.rows[user_id] = [row for row in self.rows[user_id] if row["id"] != memory_id]
            return len(self.rows[user_id]) != before

    store = FakeStore()
    memory = LearningMemory(store)
    assert memory.remember("বাংলা পছন্দ", user_id=1)["status"] == "created"
    assert memory.remember("বাংলা পছন্দ", user_id=1)["status"] == "duplicate"
    assert memory.recall(user_id=2) == []


def test_training_dataset_inspector_does_not_train_or_modify(tmp_path):
    path = tmp_path / "chat.jsonl"
    row = {"messages": [
        {"role": "user", "content": "Question"},
        {"role": "assistant", "content": "Answer"},
    ]}
    path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    result = inspect_jsonl_dataset(path)
    assert result["accepted"] == 1
    assert result["duplicates"] == 1
    assert result["model_training_performed"] is False
