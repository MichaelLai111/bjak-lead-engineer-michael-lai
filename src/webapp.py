from __future__ import annotations

import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPOSITORY_ROOT / "web"
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.assistant import GroundedAssistant
from src.config import Settings
from src.retrieval import KnowledgeIndex


def create_assistant() -> GroundedAssistant:
    settings = Settings.from_environment(REPOSITORY_ROOT)
    return GroundedAssistant(KnowledgeIndex(settings.index_path), settings)


def load_evaluation_summary() -> dict[str, Any]:
    results_path = REPOSITORY_ROOT / "evals" / "results.json"
    if not results_path.is_file():
        return {"available": False, "reason": "Evaluation results are not available."}
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    return {
        "available": True,
        "case_count": summary.get("case_count", 0),
        "metrics": summary.get("metrics", {}),
        "categories": summary.get("categories", {}),
        "failed_case_ids": summary.get("failed_case_ids", []),
    }


def json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class WebHandler(BaseHTTPRequestHandler):
    assistant: GroundedAssistant | None = None

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message}, status)

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/summary":
            self._send_json(load_evaluation_summary())
            return
        if parsed_path == "/api/health":
            self._send_json({"status": "ok", "service": "grounded-profile-ui"})
            return
        self._serve_static(parsed_path)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/ask":
            self._send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        if self.assistant is None:
            self._send_error(HTTPStatus.SERVICE_UNAVAILABLE, "Assistant is unavailable")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 64 * 1024:
                raise ValueError("Request body must be between 1 byte and 64 KB")
            request_body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            question = request_body.get("question")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("question must be a non-empty string")
            if len(question) > 2000:
                raise ValueError("question must be 2,000 characters or fewer")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_error(HTTPStatus.BAD_REQUEST, str(error))
            return

        response = self.assistant.answer(question.strip())
        self._send_json(response.to_dict())

    def _serve_static(self, requested_path: str) -> None:
        relative_path = requested_path.lstrip("/") or "index.html"
        candidate = (WEB_ROOT / relative_path).resolve()
        if WEB_ROOT.resolve() not in candidate.parents and candidate != WEB_ROOT.resolve():
            self._send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        if not candidate.is_file():
            self._send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if content_type == "text/html":
            content_type += "; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"[web] {self.address_string()} - {format_string % args}")


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    WebHandler.assistant = create_assistant()
    server = ThreadingHTTPServer((host, port), WebHandler)
    print(f"Open http://{host}:{port} in a browser")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    host = os.getenv("BJAK_WEB_HOST", "127.0.0.1")
    port = int(os.getenv("BJAK_WEB_PORT", "8000"))
    run_server(host, port)
