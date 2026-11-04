import unittest

from tamanna_ai.capabilities.tools import calculate, run_safe_tool


class SafeToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculate("(12 + 8) * 3"), 60)
        self.assertEqual(calculate("2 ** 3"), 8)

    def test_rejects_python_execution(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').system('id')")

    def test_rejects_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculate("5 / 0")

    def test_allow_list_only(self):
        self.assertEqual(run_safe_tool("calculator", {"expression": "7*6"})["result"], 42)
        with self.assertRaises(ValueError):
            run_safe_tool("shell", {"command": "id"})


if __name__ == "__main__":
    unittest.main()
