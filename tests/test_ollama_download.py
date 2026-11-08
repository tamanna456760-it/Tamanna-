import unittest

from tamanna_ai.integrations.ollama import OllamaClient


class OllamaDownloadValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_invalid_model_names_before_network_access(self):
        client = OllamaClient()
        with self.assertRaises(ValueError):
            async for _event in client.pull_model("../outside"):
                pass


if __name__ == "__main__":
    unittest.main()
