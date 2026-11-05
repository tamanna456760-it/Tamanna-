import unittest

from data.training_pipeline.usage_patterns import analyze_code_patterns


class CodeUsagePatternTests(unittest.TestCase):
    def test_counts_patterns_per_sample_not_per_occurrence(self):
        result = analyze_code_patterns([
            {"path": "api.py", "text": "def get_user():\n    try:\n        return requests.get('/users')"},
            {"path": "tests.py", "text": "def test_user():\n    assert True\n    assert True"},
            {"path": "empty.py", "text": ""},
        ])
        self.assertEqual(result["sample_count"], 2)
        self.assertTrue(result["not_industry_usage_statistics"])
        by_name = {item["pattern"]: item for item in result["patterns"]}
        self.assertEqual(by_name["function_definition"]["sample_count"], 2)
        self.assertEqual(by_name["automated_testing"]["sample_count"], 1)
        self.assertEqual(by_name["automated_testing"]["corpus_share"], 0.5)

    def test_empty_corpus_is_safe(self):
        result = analyze_code_patterns([])
        self.assertEqual(result["sample_count"], 0)
        self.assertEqual(result["patterns"], [])


if __name__ == "__main__":
    unittest.main()
