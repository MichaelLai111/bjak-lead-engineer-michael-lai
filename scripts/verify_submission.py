from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def main() -> None:
    python = sys.executable
    run([python, "scripts/build_knowledge.py"])
    run([python, "-m", "unittest", "discover", "-s", "tests", "-v"])

    with tempfile.TemporaryDirectory(prefix="bjak-evaluation-") as temporary_directory:
        temporary_path = Path(temporary_directory)
        run(
            [
                python,
                "evals/run_eval.py",
                "--json-output",
                str(temporary_path / "results.json"),
                "--markdown-output",
                str(temporary_path / "results.md"),
            ]
        )

    print("\nSubmission verification passed.")


if __name__ == "__main__":
    main()
