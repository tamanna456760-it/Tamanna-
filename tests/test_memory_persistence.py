import tempfile
import unittest
from pathlib import Path

from tamanna_ai.persistence.database import Database


class PersistentMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "memory.sqlite3"
        self.db = Database(url="sqlite:///" + str(db_path))
        self.db.init()
        self.user_a = self.db.ensure_user("a@example.test", "A")
        self.user_b = self.db.ensure_user("b@example.test", "B")

    def tearDown(self):
        self.db.engine.dispose()
        self.temp_dir.cleanup()

    def test_memories_are_isolated_by_user(self):
        self.db.add_memory("A private preference", user_id=self.user_a)
        self.db.add_memory("B private preference", user_id=self.user_b)
        self.assertEqual(self.db.list_memories(user_id=self.user_a), ["A private preference"])
        self.assertEqual(self.db.list_memories(user_id=self.user_b), ["B private preference"])
        self.assertEqual(self.db.list_memories(user_id=None), [])

    def test_memory_update_and_delete_require_owner(self):
        memory_id = self.db.add_memory("Original", user_id=self.user_a)
        self.assertFalse(self.db.update_memory(memory_id, "Intrusion", user_id=self.user_b))
        self.assertTrue(self.db.update_memory(memory_id, "Updated", user_id=self.user_a))
        self.assertEqual(self.db.list_memories(user_id=self.user_a), ["Updated"])
        self.assertFalse(self.db.delete_memory(memory_id, user_id=self.user_b))
        self.assertTrue(self.db.delete_memory(memory_id, user_id=self.user_a))
        self.assertEqual(self.db.list_memories(user_id=self.user_a), [])

    def test_profile_and_custom_settings_are_persisted_per_user(self):
        self.db.update_user_profile(
            user_id=self.user_a, name="Alice Updated", email="alice@example.test"
        )
        self.db.update_user_settings(
            user_id=self.user_a, language="bn",
            usage_pattern="Uses Tamanna for coding and study",
            custom_instructions="বাংলায় উত্তর দেবে; প্রয়োজন হলে উদাহরণ দেবে।",
            preferences={"tone": "concise", "theme": "dark"},
        )
        profile = self.db.get_user_settings(user_id=self.user_a)
        self.assertEqual(profile["name"], "Alice Updated")
        self.assertEqual(profile["email"], "alice@example.test")
        self.assertEqual(profile["language"], "bn")
        self.assertEqual(profile["usage_pattern"], "Uses Tamanna for coding and study")
        self.assertIn("বাংলায় উত্তর", profile["custom_instructions"])
        self.assertEqual(profile["preferences"]["theme"], "dark")
        other = self.db.get_user_settings(user_id=self.user_b)
        self.assertEqual(other["language"], "auto")
        self.assertEqual(other["custom_instructions"], "")

    def test_custom_settings_validate_language_and_length(self):
        with self.assertRaises(ValueError):
            self.db.update_user_settings(user_id=self.user_a, language="xx")
        with self.assertRaises(ValueError):
            self.db.update_user_settings(user_id=self.user_a, custom_instructions="x" * 4001)

    def test_profile_email_must_be_unique(self):
        with self.assertRaises(ValueError):
            self.db.update_user_profile(
                user_id=self.user_a, name="Alice", email="b@example.test"
            )

    def test_history_is_scoped_and_bounded(self):
        self.db.save_chat_pair("first question", "first answer", "chat-a", self.user_a)
        self.db.save_chat_pair("second question", "second answer", "chat-a", self.user_a)
        self.db.save_chat_pair("other user question", "other user answer", "chat-b", self.user_b)
        rows = self.db.load_history(conversation_id="chat-a", user_id=self.user_a, limit_pairs=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["user"], "second question")
        self.assertEqual(self.db.load_history(conversation_id="chat-a", user_id=self.user_b), [])


if __name__ == "__main__":
    unittest.main()
