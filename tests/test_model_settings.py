import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tamanna_ai.integrations import model_settings


class ModelSettingsTests(unittest.TestCase):
    def test_selected_model_is_persisted_and_read_back(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "data" / "model_settings.json"
            with patch.object(model_settings, "MODEL_SETTINGS_PATH", target):
                self.assertEqual(model_settings.set_selected_model("qwen2.5:7b"), "qwen2.5:7b")
                self.assertEqual(model_settings.get_selected_model(), "qwen2.5:7b")
                self.assertEqual(
                    set(target.parent.iterdir()),
                    {target},
                )

    def test_invalid_model_name_is_rejected(self):
        with self.assertRaises(ValueError):
            model_settings.set_selected_model("../secrets")

    def test_corrupt_or_missing_settings_return_none(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "model_settings.json"
            with patch.object(model_settings, "MODEL_SETTINGS_PATH", target):
                self.assertIsNone(model_settings.get_selected_model())
                target.write_text("{broken", encoding="utf-8")
                self.assertIsNone(model_settings.get_selected_model())


if __name__ == "__main__":
    unittest.main()
