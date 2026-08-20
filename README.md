# bjak-test

Grounded professional-profile assistant for the BJAK Lead Engineer practical exercise.

This repository contains a small, runnable vertical slice of a professional-background assistant. It ingests redacted profile sources, retrieves evidence locally, returns only source-backed text, exposes the result through a CLI and a Python web UI, and evaluates its safety and retrieval behavior with a committed dataset.

## Reviewer Quick Start

### Requirements

- Python 3.11 or newer
- No third-party Python packages
- No API key
- No database or external service

### Install and build

From the repository root:

```bash
python scripts/build_knowledge.py
```

Expected output:

```text
Built 19 chunks from 3 sources
```

### Run the visual UI

```bash
python -m src.webapp
```

Open `http://127.0.0.1:8000` in a browser.

The dashboard lets a reviewer:

- ask questions about the profile,
- inspect the source chunks behind an answer,
- see `not_found` and `refused` behavior,
- view evaluation metrics and known failures,
- follow the request flow from question to evidence or refusal.

### Run one CLI question

```bash
python -m src.cli --question "What experience do you have with AI?"
```

### Run the tests and evaluation

```bash
python -m unittest discover -s tests -v
python evals/run_eval.py
```

The test suite covers the knowledge assistant, CLI formatting, web API, input validation, static page serving, answer sources, and safe fallbacks.

## What This Builds

The assistant answers questions about the committed professional profile. It must not invent:

- employers,
- roles,
- projects,
- qualifications,
- achievements,
- current employment status,
- salary, team size, budget, or other unsupported facts.

The current implementation is deliberately extractive. When evidence passes the retrieval threshold, the assistant returns source text unchanged and includes stable source identifiers. When evidence is missing, it returns a deterministic fallback rather than asking a model to guess.

## Repository Map

```text
src/assistant.py             Request validation, refusal, answer composition
src/retrieval.py            Local weighted retrieval
src/knowledge.py             Source manifest and knowledge indexing
src/cli.py                   Command-line interface
src/webapp.py                Python HTTP server and JSON API
web/index.html               Visual dashboard
web/styles.css               Local UI styling
web/app.js                   UI interactions and rendering
knowledge/                   Redacted sources and generated index
evals/dataset.json           25 labeled evaluation questions
evals/run_eval.py            Reproducible evaluation command
evals/results.json           Committed evaluation output
evals/results.md             Human-readable evaluation table
tests/                       Unit and web API tests
docs/architecture.md         Architecture and security trade-offs
docs/evaluation.md           Metric definitions and continuous evaluation plan
docs/error-analysis.md       Honest analysis of remaining failures
docs/decisions.md            Rejected alternatives and design decisions
docs/web-ui.md               Visual UI instructions
docs/ai-usage.md             AI-use and reuse disclosure
```

## Architecture

```text
Question
  -> input and scope validation
  -> prompt-injection and out-of-scope checks
  -> local weighted retrieval
  -> minimum evidence threshold
  -> extractive answer with source IDs
  -> deterministic not-found or refusal fallback
```

The knowledge pipeline reads `knowledge/source_manifest.json`, loads Markdown or JSON sources, normalizes them into chunks, and writes `knowledge/index.json`. Each chunk keeps a stable ID, source ID, section, source path, update date, and redaction flags.

The assistant uses local weighted lexical retrieval instead of a hosted generative model. This was selected because the primary failure to prevent is an invented career fact. The local approach keeps profile data on the machine, has zero provider cost, has no API-key requirement, and makes every answer predictable from the committed index and code.

The rejected alternatives and their trade-offs are documented in `docs/decisions.md` and `docs/architecture.md`.

## Knowledge and Privacy

The GitHub repository is public, so the committed profile source is redacted. The repository does not contain:

- the original `Michael-Lai-Resume.pdf`,
- email address or phone number,
- LinkedIn URL,
- employer names,
- university name,
- API keys or other secrets.

The committed source still includes redacted but real role dates, responsibilities, technologies, and measured outcomes from the supplied CV. The original CV was reviewed locally and was not copied into Git.

Known data boundaries are explicit:

1. There is no committed employment record from October 2022 through February 2023. The assistant must call this period undocumented and must not infer the reason.
2. The latest committed employment record ends in November 2025. The assistant must not claim a current employer or role after that date.

See `knowledge/README.md` for collection, redaction, source extension, conflict, and stale-data rules.

## Evaluation Results

The committed evaluation contains 25 realistic questions across all required categories:

- direct CV questions,
- questions requiring multiple source records,
- ambiguous or underspecified questions,
- questions that cannot be answered from the knowledge base,
- adversarial attempts to fabricate experience, change scope, or expose secrets.

Run it with:

```bash
python evals/run_eval.py
```

The committed baseline reports:

| Metric | Result |
|---|---:|
| Case pass rate | 80.0% |
| Groundedness | 100.0% |
| Citation accuracy | 100.0% |
| Unanswerable handling | 100.0% |
| Adversarial safety | 100.0% |
| Hallucination rate | 0.0% |
| Provider cost | USD 0 |

The evaluation intentionally retains five usefulness failures. They are retrieval limitations, not hidden from the reviewer:

- `multi-001`
- `multi-004`
- `ambiguous-001`
- `ambiguous-002`
- `ambiguous-005`

Their root causes and next fixes are in `docs/error-analysis.md`. Metric numerators, denominators, pass bars, and the continuous-evaluation plan are in `docs/evaluation.md`.

The recorded p95 is an in-process application measurement and excludes Python interpreter startup. It is useful for comparing this local baseline, not a production capacity claim.

## Security and Failure Behavior

The web server binds to `127.0.0.1` by default. It does not expose the application publicly unless the bind address is deliberately changed.

The application refuses or falls back in these situations:

| Situation | Behavior |
|---|---|
| No relevant evidence | `not_found`, no sources, no invented claim |
| Prompt injection | `refused`, no source disclosure |
| Secret or out-of-scope request | `refused` |
| Current-status question beyond source coverage | Returns the stale-data boundary |
| Invalid web request | HTTP `400` with a validation error |
| Missing or invalid index | Startup error with a rebuild instruction |

No profile data leaves the machine in the current implementation. No external model provider is called.

## Known Limitations and Next Steps

This is a time-boxed engineering slice, not a production service. Known limitations include:

- lexical retrieval instead of semantic retrieval,
- weak handling of broad summary and timeline questions,
- limited multi-source result diversification,
- English-only query handling,
- no authentication or persistent audit log,
- no rate limiting, deployment configuration, or production monitoring,
- no hosted model synthesis.

The next three changes would be:

1. Add intent-aware routing and diversified retrieval for timeline, skills, summary, and comparison questions.
2. Add an optional model-backed synthesis adapter that can cite only retrieved chunk IDs and always fall back to extractive output.
3. Add authentication, security-safe audit logs, observability, rate limiting, source approval, and automated evaluation gates.

## Decisions and AI Use

The decision record covers five major choices:

- redacted public sources instead of the raw CV,
- local extractive retrieval instead of a hosted model,
- manifest-based ingestion instead of hardcoded parsing,
- deterministic evaluation instead of an LLM judge,
- CLI and Python web UI instead of a larger frontend stack.

See `docs/decisions.md` for rejected alternatives and trade-offs.

AI assistance was used for repository scaffolding, code and test drafts, evaluation-case drafts, documentation, and failure review. The raw CV, source-of-truth career facts, redaction policy, evaluation pass bars, and final safety boundaries were not delegated to a model. Generated output was reviewed, corrected, and tested; the five retrieval failures were retained rather than tuned away.

No prior project, starter repository, application template, or third-party codebase was reused. The implementation uses Python's standard library.

## Time Spent

Approximately 20 minutes of active implementation work were recorded for the final repository slice. Environment setup and reading the exercise brief were excluded. The time-box decision was to deliver a thin grounded path, committed evaluation evidence, a visual UI, and explicit limitations rather than a broader production-style system.

Details are recorded in `docs/time-log.md`.

## Submission Details

- Repository: `bjak-lead-engineer-<yourname>` requirement adapted to this working repository: `bjak-test`
- Visibility: public, with personal information redacted
- Review tag: `submission`
- Reviewed state: the commit referenced by the `submission` tag
- Main branch is pushed to the GitHub repository

To reproduce the final state:

```bash
git checkout submission
python scripts/build_knowledge.py
python -m unittest discover -s tests -v
python evals/run_eval.py
python -m src.webapp
```

The submission is designed to be read, run, evaluated, and discussed in the follow-up review.
