import json
import tempfile
import unittest
from pathlib import Path

from data.training_pipeline.cleaning import clean_text
from data.training_pipeline.pipeline import run_pipeline
from data.training_pipeline.quality import inspect_records


class CleaningTests(unittest.TestCase):
    def test_redacts_email_and_secret(self):
        text, flags = clean_text("Contact person@example.com and api_key=abc123")
        self.assertNotIn("person@example.com", text)
        self.assertNotIn("abc123", text)
        self.assertIn("email_redacted", flags)
        self.assertIn("possible_secret_redacted", flags)

    def test_quality_counts_duplicates_and_short_records(self):
        result = inspect_records([{"text": "A sufficiently long example record."}, {"text": "A sufficiently long example record."}, {"text": "tiny"}])
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["rejected"], 2)
        self.assertEqual(result["issues"]["duplicate"], 1)

    def test_pipeline_indexes_signature_checked_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            output = root / "output"
            source.mkdir()
            (source / "sample.png").write_bytes(b"\\x89PNG\\r\\n\\x1a\\n")
            result = run_pipeline(source, output)
            self.assertEqual(result["images_indexed"], 1)
            image_row = json.loads((output / "images_manifest.jsonl").read_text(encoding="utf-8").strip())
            self.assertEqual(image_row["format"], "png")
            self.assertEqual(len(image_row["sha256"]), 64)

    def test_pipeline_writes_clean_dataset_and_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            output = root / "output"
            source.mkdir()
            (source / "notes.txt").write_text("This is a sufficiently long training example.\n", encoding="utf-8")
            result = run_pipeline(source, output)
            self.assertEqual(result["accepted"], 1)
            rows = [json.loads(line) for line in (output / "cleaned.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertTrue((output / "quality_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
