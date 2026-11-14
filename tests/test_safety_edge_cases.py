import json
import zipfile
import pytest
from tamanna_ai.learning.trainer import inspect_jsonl_dataset
from tamanna_ai.backup.restore import inspect_backup

def test_training_inspector_rejects_non_object_message_without_crashing(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"messages": ["not-an-object", {}]}) + "\n", encoding="utf-8")
    result = inspect_jsonl_dataset(path)
    assert result["accepted"] == 0
    assert result["issues"][0]["reason"] == "invalid_chat_messages"

def test_backup_rejects_duplicate_zip_entries(tmp_path):
    path = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("x.txt", "one")
        archive.writestr("x.txt", "two")
        archive.writestr("MANIFEST.json", json.dumps({"version": 1, "files": []}))
    with pytest.raises(ValueError, match="duplicate entry"):
        inspect_backup(path)
