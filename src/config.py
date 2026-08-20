from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    index_path: Path
    top_k: int
    min_score: float
    max_answer_chunks: int

    @classmethod
    def from_environment(cls, repository_root: Path) -> "Settings":
        index_value = os.getenv("BJAK_INDEX_PATH", "knowledge/index.json")
        index_path = Path(index_value)
        if not index_path.is_absolute():
            index_path = repository_root / index_path

        settings = cls(
            index_path=index_path,
            top_k=_read_int("BJAK_TOP_K", 3, minimum=1, maximum=10),
            min_score=_read_float("BJAK_MIN_SCORE", 1.25, minimum=0.0),
            max_answer_chunks=_read_int(
                "BJAK_MAX_ANSWER_CHUNKS", 3, minimum=1, maximum=5
            ),
        )
        if settings.max_answer_chunks > settings.top_k:
            raise ValueError("BJAK_MAX_ANSWER_CHUNKS cannot exceed BJAK_TOP_K")
        return settings


def _read_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw_value = os.getenv(name)
    value = default if raw_value is None else int(raw_value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _read_float(name: str, default: float, minimum: float) -> float:
    raw_value = os.getenv(name)
    value = default if raw_value is None else float(raw_value)
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value
