from __future__ import annotations

import unittest

from src.assistant import AssistantResponse, AnswerSource
from src.cli import format_response


class CliFormattingTests(unittest.TestCase):
    def test_answer_format_includes_source(self) -> None:
        response = AssistantResponse(
            status="answered",
            answer="Documented answer.",
            sources=[
                AnswerSource(
                    chunk_id="source:section:123",
                    source_id="source",
                    title="Source title",
                    section="section",
                    score=2.5,
                )
            ],
            latency_ms=1.5,
        )
        output = format_response(response)
        self.assertIn("Documented answer.", output)
        self.assertIn("source:section:123", output)
        self.assertIn("Status: answered", output)

    def test_fallback_format_shows_no_sources(self) -> None:
        response = AssistantResponse(
            status="not_found",
            answer="No evidence.",
            sources=[],
            latency_ms=0.5,
            reason="insufficient_evidence",
        )
        output = format_response(response)
        self.assertIn("- none", output)
        self.assertIn("Reason: insufficient_evidence", output)


if __name__ == "__main__":
    unittest.main()
