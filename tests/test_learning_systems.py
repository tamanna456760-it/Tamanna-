import json
import tempfile
import unittest
from pathlib import Path

from data.learning_systems.preferences import export_preference_dataset
from data.learning_systems.sft import export_sft_dataset


class LearningDatasetTests(unittest.TestCase):
    def test_sft_exports_chat_messages_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "source.jsonl", root / "sft.jsonl"
            source.write_text(json.dumps({"prompt": "Explain a safe example", "response": "Use GEMINI_API_KEY=secret-value only in private environment."}) + "\n", encoding="utf-8")
            result = export_sft_dataset(source, output)
            row = json.loads(output.read_text(encoding="utf-8").strip())
            self.assertEqual(result["accepted"], 1)
            self.assertEqual(row["messages"][0]["role"], "user")
            self.assertNotIn("secret-value", row["messages"][1]["content"])

    def test_sft_accepts_conversation_history_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "history.jsonl", root / "sft.jsonl"
            source.write_text(json.dumps({"user": "How does a safe system work?", "assistant": "It uses least privilege and validation."}) + "\\n", encoding="utf-8")
            result = export_sft_dataset(source, output)
            row = json.loads(output.read_text(encoding="utf-8").strip())
            self.assertEqual(result["accepted"], 1)
            self.assertEqual(row["messages"][0]["content"], "How does a safe system work?")
            self.assertEqual(row["messages"][1]["content"], "It uses least privilege and validation.")

    def test_preferences_require_explicit_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "feedback.jsonl", root / "preferences.jsonl"
            rows = [
                {"prompt": "Question", "response_a": "Answer A", "response_b": "Answer B", "preferred": "b", "human_reviewed": True},
                {"prompt": "Question", "response_a": "Answer A", "response_b": "Answer B", "preferred": "a", "human_reviewed": False},
            ]
            source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            result = export_preference_dataset(source, output)
            exported = json.loads(output.read_text(encoding="utf-8").strip())
            self.assertEqual(result["accepted"], 1)
            self.assertEqual(result["rejected"], 1)
            self.assertEqual(exported["chosen"], "Answer B")
            self.assertEqual(exported["rejected"], "Answer A")


if __name__ == "__main__":
    unittest.main()
