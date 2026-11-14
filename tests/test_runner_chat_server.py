import importlib.util
import json
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "runner" / "python" / "AI_CHAT" / "chat_server.py"
)
spec = importlib.util.spec_from_file_location("tamanna_local_chat_server", MODULE_PATH)
chat_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat_server)


class LocalChatServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = chat_server.ThreadingHTTPServer(("127.0.0.1", 0), chat_server.ChatHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def post(self, payload):
        request = Request(
            self.base_url + "/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_endpoint(self):
        with urlopen(self.base_url + "/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["status"], "ok")

    def test_valid_message_returns_local_reply(self):
        status, payload = self.post({"message": "hello"})
        self.assertEqual(status, 200)
        self.assertIn("Hi!", payload["reply"])
        self.assertEqual(payload["mode"], "local-demo")

    def test_missing_or_non_string_message_is_rejected(self):
        self.assertEqual(self.post({})[0], 400)
        self.assertEqual(self.post({"message": 12})[0], 400)

    def test_blank_message_is_rejected(self):
        self.assertEqual(self.post({"message": "   "})[0], 400)

    def test_unknown_route_is_not_found(self):
        request = Request(self.base_url + "/unknown", method="POST")
        with self.assertRaises(HTTPError) as context:
            urlopen(request, timeout=3)
        self.assertEqual(context.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
