from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    path: str
    format: str
    source_type: str
    title: str
    updated_at: str
    redacted: bool
    synthetic: bool


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    source_id: str
    source_type: str
    title: str
    section: str
    text: str
    source_path: str
    updated_at: str
    redacted: bool
    synthetic: bool
    metadata: dict[str, Any]


def _stable_chunk_id(source_id: str, section: str, position: int, text: str) -> str:
    digest_input = f"{source_id}|{section}|{position}|{text}".encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()[:12]
    return f"{source_id}:{section}:{digest}"


def _make_chunk(
    source: SourceDefinition,
    section: str,
    position: int,
    text: str,
    metadata: dict[str, Any] | None = None,
) -> KnowledgeChunk:
    cleaned_text = " ".join(text.split())
    return KnowledgeChunk(
        chunk_id=_stable_chunk_id(source.source_id, section, position, cleaned_text),
        source_id=source.source_id,
        source_type=source.source_type,
        title=source.title,
        section=section,
        text=cleaned_text,
        source_path=source.path,
        updated_at=source.updated_at,
        redacted=source.redacted,
        synthetic=source.synthetic,
        metadata=metadata or {},
    )


def load_markdown(path: Path, source: SourceDefinition) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    current_section = "document"
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph = " ".join(paragraph_lines).strip()
        paragraph_lines.clear()
        if paragraph:
            chunks.append(
                _make_chunk(source, current_section, len(chunks), paragraph)
            )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            flush_paragraph()
            current_section = line.lstrip("#").strip().lower().replace(" ", "_")
            continue
        if not line:
            flush_paragraph()
            continue
        paragraph_lines.append(line.lstrip("- "))

    flush_paragraph()
    return chunks


def load_json(path: Path, source: SourceDefinition) -> list[KnowledgeChunk]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError(f"JSON source must contain a records list: {path}")

    chunks: list[KnowledgeChunk] = []
    for position, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("text"), str):
            raise ValueError(f"Invalid record at position {position} in {path}")
        section = str(record.get("section", "record"))
        metadata = {key: value for key, value in record.items() if key != "text"}
        chunks.append(
            _make_chunk(source, section, position, record["text"], metadata)
        )
    return chunks


Loader = Callable[[Path, SourceDefinition], list[KnowledgeChunk]]
LOADERS: dict[str, Loader] = {
    "markdown": load_markdown,
    "json": load_json,
}


def load_manifest(manifest_path: Path) -> tuple[int, list[SourceDefinition]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema_version = payload.get("schema_version")
    if schema_version != 1:
        raise ValueError(f"Unsupported manifest schema version: {schema_version}")

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ValueError("Manifest must contain at least one source")

    sources = [SourceDefinition(**raw_source) for raw_source in raw_sources]
    source_ids = [source.source_id for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Manifest source_id values must be unique")
    return schema_version, sources


def build_index(manifest_path: Path) -> dict[str, Any]:
    schema_version, sources = load_manifest(manifest_path)
    knowledge_root = manifest_path.parent
    chunks: list[KnowledgeChunk] = []

    for source in sources:
        loader = LOADERS.get(source.format)
        if loader is None:
            raise ValueError(f"Unsupported source format: {source.format}")
        source_path = (knowledge_root / source.path).resolve()
        if knowledge_root.resolve() not in source_path.parents:
            raise ValueError(f"Source path escapes knowledge directory: {source.path}")
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file not found: {source.path}")
        chunks.extend(loader(source_path, source))

    return {
        "schema_version": schema_version,
        "source_count": len(sources),
        "chunk_count": len(chunks),
        "sources": [asdict(source) for source in sources],
        "chunks": [asdict(chunk) for chunk in chunks],
    }


def write_index(manifest_path: Path, output_path: Path) -> dict[str, Any]:
    index = build_index(manifest_path)
    output_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return index
