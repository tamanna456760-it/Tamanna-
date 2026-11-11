import unittest

from tamanna_ai.emotion import detect_emotion, response_guidance


class EmotionDetectionTests(unittest.TestCase):
    def test_detects_bengali_sadness(self):
        result = detect_emotion("আজ আমার মন খারাপ", language="bn")
        self.assertEqual(result.emotion, "sadness")

    def test_detects_english_joy(self):
        self.assertEqual(detect_emotion("I am so happy today").emotion, "joy")

    def test_detects_hindi_anxiety(self):
        self.assertEqual(detect_emotion("मुझे बहुत चिंता है", language="hi").emotion, "anxiety")

    def test_unknown_for_neutral_text(self):
        self.assertEqual(detect_emotion("Please explain photosynthesis").emotion, "unknown")

    def test_empty_input(self):
        self.assertEqual(detect_emotion(" ").emotion, "unknown")

    def test_style_guidance_supports_all_personalities(self):
        result = detect_emotion("thank you", language="en")
        for style in ("balanced", "warm", "professional", "calm", "friendly", "emotional"):
            self.assertIn("Do not diagnose", response_guidance(result, style))

    def test_invalid_style_rejected(self):
        with self.assertRaises(ValueError):
            response_guidance(detect_emotion("hello"), "clingy")

    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):
            detect_emotion("hello", min_confidence=2)


if __name__ == "__main__":
    unittest.main()
