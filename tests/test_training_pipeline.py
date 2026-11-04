import json
import tempfile
import unittest
from pathlib import Path

from data.training_pipeline.cleaning import clean_text
from data.training_pipeline.pipeline import run_pipeline
from data.training_pipeline.quality import inspect_records
from data.training_pipeline.provenance import load_provenance


class CleaningTests(unittest.TestCase):
    def test_redacts_email_and_secret(self):
        text, flags = clean_text("Contact person@example.com and GEMINI_API_KEY=abc123")
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
            (source / "sample.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            result = run_pipeline(source, output)
            self.assertEqual(result["images_indexed"], 1)
            image_row = json.loads((output / "images_manifest.jsonl").read_text(encoding="utf-8").strip())
            self.assertEqual(image_row["format"], "png")
            self.assertEqual(len(image_row["sha256"]), 64)

    def test_pipeline_indexes_audio_video_and_pdf_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "source", root / "output"
            source.mkdir()
            (source / "sample.wav").write_bytes(b"RIFF" + b"\x00\x00\x00\x00" + b"WAVE" + b"data")
            (source / "sample.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom")
            (source / "sample.pdf").write_bytes(b"%PDF-1.7 sample")
            result = run_pipeline(source, output)
            self.assertEqual(result["audio_indexed"], 1)
            self.assertEqual(result["video_indexed"], 1)
            self.assertEqual(result["documents_indexed"], 1)
            rows = [json.loads(line) for line in (output / "media_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual({row["kind"] for row in rows}, {"audio", "video", "document"})

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


    def test_provenance_manifest_requires_explicit_training_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "sources.json"
            manifest.write_text(json.dumps([{
                "file": "article.md", "category": "article",
                "source_url": "https://example.org/article",
                "license": "CC-BY-4.0", "training_use_allowed": True
            }]), encoding="utf-8")
            entries = load_provenance(manifest)
            self.assertEqual(entries["article.md"]["license"], "CC-BY-4.0")
            manifest.write_text(json.dumps([{
                "file": "article.md", "category": "article",
                "source_url": "https://example.org/article",
                "license": "unknown", "training_use_allowed": False
            }]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_provenance(manifest)

    def test_pipeline_skips_files_without_provenance_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "source", root / "output"
            source.mkdir()
            (source / "article.md").write_text(
                "A sufficiently long article content.", encoding="utf-8"
            )
            manifest = root / "sources.json"
            manifest.write_text("[]", encoding="utf-8")
            result = run_pipeline(source, output, provenance_path=manifest)
            self.assertEqual(result["accepted"], 0)
            self.assertEqual(result["files_skipped"], 1)

    def test_redacts_government_ids_and_labelled_personal_fields(self):
        from data.training_pipeline.privacy import redact_sensitive_data
        emirates_id = "784-" + "1990" + "-" + "1234567" + "-" + "1"
        sample = (
            "Emirates ID: " + emirates_id + "\\n"
            "Passport Number: " + "AB" + "12345678" + "\\n"
            "Name: " + "Jane Example" + "\\n"
            "Address: " + "12 Example Street, Sample City"
        )
        cleaned, flags = redact_sensitive_data(sample)
        for secret in (emirates_id, "AB12345678", "Jane Example", "12 Example Street"):
            self.assertNotIn(secret, cleaned)
        self.assertIn("government_id_redacted", flags)
        self.assertIn("labelled_name_redacted", flags)
        self.assertIn("labelled_address_redacted", flags)

    def test_luhn_checker_rejects_invalid_card_candidate(self):
        from data.training_pipeline.privacy import _luhn_valid
        self.assertFalse(_luhn_valid("1234567890123456"))

if __name__ == "__main__":
    unittest.main()
