from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.assistant import AssistantResponse, GroundedAssistant
from src.config import Settings
from src.retrieval import KnowledgeIndex


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXIT_WORDS = {"exit", "quit", ":q"}


def create_assistant() -> GroundedAssistant:
    settings = Settings.from_environment(REPOSITORY_ROOT)
    return GroundedAssistant(KnowledgeIndex(settings.index_path), settings)


def format_response(response: AssistantResponse) -> str:
    lines = ["", "Answer", "------", response.answer, "", "Sources", "-------"]
    if response.sources:
        for source in response.sources:
            lines.append(
                f"- {source.chunk_id} | {source.title} | "
                f"section={source.section} | score={source.score}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            f"Status: {response.status}",
            f"Latency: {response.latency_ms:.3f} ms",
        ]
    )
    if response.reason:
        lines.append(f"Reason: {response.reason}")
    return "\n".join(lines)


def ask_once(assistant: GroundedAssistant, question: str, as_json: bool) -> None:
    response = assistant.answer(question)
    if as_json:
        print(json.dumps(response.to_dict(), indent=2, ensure_ascii=False))
        return
    print(format_response(response))


def run_interactive(assistant: GroundedAssistant) -> None:
    print("Grounded Professional Assistant")
    print("Ask about documented experience, projects, technologies, or work style.")
    print("Type 'exit' to close.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if question.lower() in EXIT_WORDS:
            print("Goodbye.")
            return
        ask_once(assistant, question, as_json=False)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the grounded professional profile"
    )
    parser.add_argument("--question", help="Ask one question and exit")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Return the single-question response as JSON",
    )
    arguments = parser.parse_args()

    try:
        assistant = create_assistant()
    except (RuntimeError, ValueError) as error:
        parser.exit(2, f"Configuration error: {error}\n")

    if arguments.json and not arguments.question:
        parser.error("--json requires --question")

    if arguments.question:
        ask_once(assistant, arguments.question, arguments.json)
        return
    run_interactive(assistant)


if __name__ == "__main__":
    main()
