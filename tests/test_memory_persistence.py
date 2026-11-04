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
