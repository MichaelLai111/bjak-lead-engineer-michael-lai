from __future__ import annotations

import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

from src.webapp import WebHandler, create_assistant
from http.server import ThreadingHTTPServer


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WebHandler.assistant = create_assistant()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), WebHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body: dict | None = None):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=5)
        encoded_body = None
        headers = {}
        if body is not None:
            encoded_body = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        connection.request(method, path, body=encoded_body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        content_type = response.getheader("Content-Type", "")
        connection.close()
        return response.status, content_type, payload

    def test_health_endpoint(self) -> None:
        status, content_type, payload = self.request("GET", "/api/health")
        self.assertEqual(200, status)
        self.assertIn("application/json", content_type)
        self.assertEqual("ok", json.loads(payload)["status"])

    def test_summary_endpoint_exposes_metrics(self) -> None:
        status, _, payload = self.request("GET", "/api/summary")
        summary = json.loads(payload)
        self.assertEqual(200, status)
        self.assertTrue(summary["available"])
        self.assertIn("groundedness_percent", summary["metrics"])

    def test_ask_endpoint_returns_sources(self) -> None:
        status, _, payload = self.request(
            "POST", "/api/ask", {"question": "What experience do you have with AI?"}
        )
        result = json.loads(payload)
        self.assertEqual(200, status)
        self.assertEqual("answered", result["status"])
        self.assertTrue(result["sources"])

    def test_ask_endpoint_returns_safe_fallback(self) -> None:
        status, _, payload = self.request(
            "POST", "/api/ask", {"question": "What salary are you expecting?"}
        )
        result = json.loads(payload)
        self.assertEqual(200, status)
        self.assertEqual("not_found", result["status"])
        self.assertEqual([], result["sources"])

    def test_ask_endpoint_validates_input(self) -> None:
        status, _, payload = self.request("POST", "/api/ask", {"question": ""})
        self.assertEqual(400, status)
        self.assertIn("question", json.loads(payload)["error"])

    def test_static_page_is_available(self) -> None:
        status, content_type, payload = self.request("GET", "/")
        self.assertEqual(200, status)
        self.assertIn("text/html", content_type)
        self.assertIn(b"Grounded Profile Lab", payload)


if __name__ == "__main__":
    unittest.main()
