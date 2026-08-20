from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.knowledge import write_index


def main() -> None:
    manifest_path = REPOSITORY_ROOT / "knowledge" / "source_manifest.json"
    output_path = REPOSITORY_ROOT / "knowledge" / "index.json"
    index = write_index(manifest_path, output_path)
    print(
        f"Built {index['chunk_count']} chunks from "
        f"{index['source_count']} sources: {output_path}"
    )


if __name__ == "__main__":
    main()
