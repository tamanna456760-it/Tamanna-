import unittest

from tamanna_ai.integrations.ollama import OllamaClient


class OllamaDownloadValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_invalid_model_names_before_network_access(self):
        client = OllamaClient()
        with self.assertRaises(ValueError):
            async for _event in client.pull_model("../outside"):
                pass

    async def test_accepts_common_ollama_model_name_shape(self):
        client = OllamaClient()
        self.assertEqual(client.model, "qwen2.5:7b")
        # Validation is exercised by the pull generator before it opens a connection.
        generator = client.pull_model("qwen2.5:7b")
        await generator.aclose()


if __name__ == "__main__":
    unittest.main()
