from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[.+#-][a-z0-9]+)*")
STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "can",
    "did",
    "do",
    "does",
    "for",
    "from",
    "have",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
    "you",
    "your",
}
QUERY_ALIASES = {
    "ai": {"artificial", "intelligence", "rag", "retrieval", "automation"},
    "api": {"apis", "rest", "service", "services"},
    "aws": {"cloud", "cloudwatch"},
    "backend": {"api", "apis", "rest", "postgresql", "redis"},
    "current": {"latest", "present", "now", "today"},
    "database": {"postgresql", "redis", "query", "data"},
    "education": {"degree", "university", "study"},
    "frontend": {"react", "typescript", "javascript", "redux", "tailwind"},
    "insurance": {"claims", "claim", "policy", "coverage", "insurtech"},
    "latency": {"performance", "speed", "caching", "optimization"},
    "payments": {"payment", "refund", "settlement", "transaction", "bnpl"},
    "reliability": {"monitoring", "logging", "retry", "validation"},
    "skills": {"technologies", "technology", "stack", "tools"},
}


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    source_id: str
    title: str
    section: str
    text: str
    score: float
    metadata: dict[str, Any]


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOP_WORDS and len(token) > 1
    ]


def expand_query(tokens: list[str]) -> list[str]:
    expanded = list(tokens)
    token_set = set(tokens)
    for key, aliases in QUERY_ALIASES.items():
        if key in token_set or token_set.intersection(aliases):
            expanded.extend(sorted(aliases | {key}))
    return expanded


class KnowledgeIndex:
    def __init__(self, index_path: Path) -> None:
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise RuntimeError(
                f"Knowledge index not found at {index_path}. "
                "Run python scripts/build_knowledge.py."
            ) from error
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Knowledge index is invalid JSON: {index_path}") from error

        chunks = payload.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise RuntimeError("Knowledge index does not contain searchable chunks")

        self._chunks = chunks
        self._document_tokens = [tokenize(chunk["text"]) for chunk in chunks]
        self._document_frequencies = self._build_document_frequencies()

    def _build_document_frequencies(self) -> Counter[str]:
        frequencies: Counter[str] = Counter()
        for tokens in self._document_tokens:
            frequencies.update(set(tokens))
        return frequencies

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        query_tokens = expand_query(tokenize(query))
        if not query_tokens:
            return []

        query_counts = Counter(query_tokens)
        result_rows: list[SearchResult] = []
        total_documents = len(self._chunks)

        for chunk, document_tokens in zip(self._chunks, self._document_tokens):
            document_counts = Counter(document_tokens)
            score = 0.0
            for token, query_frequency in query_counts.items():
                term_frequency = document_counts.get(token, 0)
                if not term_frequency:
                    continue
                document_frequency = self._document_frequencies[token]
                inverse_document_frequency = math.log(
                    1 + (total_documents + 1) / (document_frequency + 1)
                )
                score += (
                    (1 + math.log(term_frequency))
                    * inverse_document_frequency
                    * (1 + math.log(query_frequency))
                )

            if score <= 0:
                continue
            result_rows.append(
                SearchResult(
                    chunk_id=chunk["chunk_id"],
                    source_id=chunk["source_id"],
                    title=chunk["title"],
                    section=chunk["section"],
                    text=chunk["text"],
                    score=round(score, 4),
                    metadata=chunk.get("metadata", {}),
                )
            )

        result_rows.sort(key=lambda result: (-result.score, result.chunk_id))
        return result_rows[:top_k]
