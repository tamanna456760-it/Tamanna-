import asyncio
import unittest

from tamanna_ai.capabilities.web_search import BraveSearchClient, WebSearchError


class WebSearchTests(unittest.TestCase):
    def test_search_requires_api_key(self):
        client = BraveSearchClient(api_key="")
        with self.assertRaises(WebSearchError):
            asyncio.run(client.search("latest technology news"))

    def test_search_validates_query_and_limit_before_network(self):
        client = BraveSearchClient(api_key="test-key")
        with self.assertRaises(ValueError):
            asyncio.run(client.search(" "))
        with self.assertRaises(ValueError):
            asyncio.run(client.search("valid query", limit=11))

    def test_timeout_is_bounded(self):
        with self.assertRaises(ValueError):
            BraveSearchClient(api_key="test-key", timeout=60)


if __name__ == "__main__":
    unittest.main()
