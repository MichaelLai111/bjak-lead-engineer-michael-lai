from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter

from src.config import Settings
from src.retrieval import KnowledgeIndex, SearchResult, tokenize


INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "reveal secret",
    "print environment",
    "show api key",
)
OUT_OF_SCOPE_MARKERS = (
    "bank transfer",
    "send money",
    "medical advice",
    "legal advice",
    "password",
    "api key",
    "secret key",
)
CURRENT_STATUS_MARKERS = ("current", "currently", "present", "now", "today")
FABRICATED_EMPLOYMENT_MARKERS = (
    "pretend you worked",
    "pretend i worked",
    "invent an employer",
    "make up an employer",
)
STRICT_EVIDENCE_MARKERS = ("certification", "certifications", "certified")


@dataclass(frozen=True)
class AnswerSource:
    chunk_id: str
    source_id: str
    title: str
    section: str
    score: float


@dataclass(frozen=True)
class AssistantResponse:
    status: str
    answer: str
    sources: list[AnswerSource]
    latency_ms: float
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class GroundedAssistant:
    def __init__(self, index: KnowledgeIndex, settings: Settings) -> None:
        self._index = index
        self._settings = settings

    def answer(self, question: str) -> AssistantResponse:
        started_at = perf_counter()
        normalized_question = " ".join(question.lower().split())

        if not tokenize(question):
            return self._response(
                started_at,
                status="refused",
                answer="Please ask a specific question about the documented professional profile.",
                sources=[],
                reason="empty_or_unspecific_question",
            )

        if any(marker in normalized_question for marker in INJECTION_MARKERS):
            return self._response(
                started_at,
                status="refused",
                answer=(
                    "I cannot follow instructions that change the assistant's scope or expose "
                    "configuration. Ask about the documented professional profile instead."
                ),
                sources=[],
                reason="prompt_injection",
            )

        if any(marker in normalized_question for marker in OUT_OF_SCOPE_MARKERS):
            return self._response(
                started_at,
                status="refused",
                answer=(
                    "That request is outside this assistant's scope. I can only answer questions "
                    "about the committed professional profile."
                ),
                sources=[],
                reason="out_of_scope",
            )

        if any(
            marker in normalized_question for marker in FABRICATED_EMPLOYMENT_MARKERS
        ):
            return self._response(
                started_at,
                status="not_found",
                answer=(
                    "The committed professional sources do not contain enough evidence to answer "
                    "that question. I will not invent an employer or role."
                ),
                sources=[],
                reason="unsupported_employment_claim",
            )

        search_query = question
        if any(marker in normalized_question for marker in CURRENT_STATUS_MARKERS):
            search_query = f"{question} current latest stale fact November 2025"

        results = self._index.search(search_query, self._settings.top_k)
        asks_for_certification = any(
            phrase in normalized_question
            for phrase in (
                "which certification",
                "which cloud certification",
                "what certification",
                "do you hold",
            )
        ) and any(marker in normalized_question for marker in STRICT_EVIDENCE_MARKERS)
        if asks_for_certification:
            has_literal_evidence = any(
                any(marker in result.text.lower() for marker in STRICT_EVIDENCE_MARKERS)
                for result in results
            )
            if not has_literal_evidence:
                return self._response(
                    started_at,
                    status="not_found",
                    answer=(
                        "The committed professional sources do not contain enough evidence to "
                        "answer that question."
                    ),
                    sources=[],
                    reason="strict_evidence_missing",
                )
        relevant_results = [
            result for result in results if result.score >= self._settings.min_score
        ][: self._settings.max_answer_chunks]

        if not relevant_results:
            return self._response(
                started_at,
                status="not_found",
                answer=(
                    "The committed professional sources do not contain enough evidence to answer "
                    "that question. Try naming a role, project area, technology, or date range."
                ),
                sources=[],
                reason="insufficient_evidence",
            )

        answer = self._compose_extract(relevant_results)
        sources = [
            AnswerSource(
                chunk_id=result.chunk_id,
                source_id=result.source_id,
                title=result.title,
                section=result.section,
                score=result.score,
            )
            for result in relevant_results
        ]
        return self._response(
            started_at,
            status="answered",
            answer=answer,
            sources=sources,
        )

    @staticmethod
    def _compose_extract(results: list[SearchResult]) -> str:
        unique_text: list[str] = []
        for result in results:
            if result.text not in unique_text:
                unique_text.append(result.text)
        return "\n\n".join(unique_text)

    @staticmethod
    def _response(
        started_at: float,
        status: str,
        answer: str,
        sources: list[AnswerSource],
        reason: str | None = None,
    ) -> AssistantResponse:
        return AssistantResponse(
            status=status,
            answer=answer,
            sources=sources,
            latency_ms=round((perf_counter() - started_at) * 1000, 3),
            reason=reason,
        )
