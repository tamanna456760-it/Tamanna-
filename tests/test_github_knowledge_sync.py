import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.sync_github_knowledge import (
    iter_documents,
    validate_repository_url,
)


class GitHubKnowledgeSyncTests(unittest.TestCase):
    def test_accepts_public_github_https_url(self):
        self.assertEqual(
            validate_repository_url("https://github.com/example/knowledge"),
            "https://github.com/example/knowledge.git",
        )

    def test_rejects_non_github_or_non_https_url(self):
        for value in (
            "http://github.com/example/knowledge",
            "https://example.com/knowledge.git",
            "git@github.com:example/knowledge.git",
            "https://github.com/example/knowledge?token=secret",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_repository_url(value)

    def test_indexes_only_supported_non_private_text_files(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("# Hello\nKnowledge", encoding="utf-8")
            (root / "notes.txt").write_text("Local notes", encoding="utf-8")
            (root / "image.png").write_bytes(b"not text")
            private = root / "private"
            private.mkdir()
            (private / "secret.md").write_text("do not index", encoding="utf-8")
            items = list(iter_documents(root))
        self.assertEqual([name for name, _ in items], ["README.md", "notes.txt"])


if __name__ == "__main__":
    unittest.main()
