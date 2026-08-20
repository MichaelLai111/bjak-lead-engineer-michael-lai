# bjak-test

Grounded professional-profile assistant built for the BJAK Lead Engineer practical exercise.

The repository contains a complete thin slice: redacted knowledge ingestion, local grounded retrieval, a CLI, a 25-case evaluation, and the decision record behind the implementation.

## Scope

The assistant answers questions about the committed professional profile. It must not invent employers, roles, projects, qualifications, or achievements. It returns extractive source text when evidence passes the configured threshold and returns a deterministic fallback otherwise.

Non-goals for this time-boxed version are hosted-model synthesis, a web UI, authentication, deployment, and production observability.

## Knowledge layer

The committed source material is redacted because this repository is public. Contact details, employer names, and the university name are not included. The remaining role dates, responsibilities, technologies, and measured outcomes are based on the supplied CV.

Build the normalized knowledge index:

```bash
python scripts/build_knowledge.py
```

The command reads `knowledge/source_manifest.json` and writes `knowledge/index.json`. New Markdown or JSON sources can be added by creating the file and registering it in the manifest; the ingestion code does not need to change.

See `knowledge/README.md` for the source policy, schema, redactions, and known gaps.

## Backend

The assistant uses local weighted retrieval and returns source text without generative rewriting. It requires no API key and sends no profile data to an external provider.

Configuration is documented in `.env.example`. The backend implementation is in `src/assistant.py`, and the design and trade-offs are described in `docs/architecture.md`.

## Run the assistant

No package installation is required. Use Python 3.11 or newer.

Ask one question:

```bash
python -m src.cli --question "What experience do you have with AI?"
```

Start an interactive session:

```bash
python -m src.cli
```

The CLI always shows answer sources or an explicit `none` fallback. Interaction details are in `docs/user-experience.md`.

## Evaluation

Run the complete 25-case evaluation:

```bash
python evals/run_eval.py
```

Run the focused unit tests:

```bash
python -m unittest discover -s tests -v
```

Metric definitions are in `docs/evaluation.md`. The generated results and failure analysis are committed under `evals/` and `docs/`.

Current committed result: 20 of 25 cases pass. Groundedness, citation accuracy, unanswerable handling, and adversarial safety are 100 percent. The remaining retrieval and usefulness failures are described in `docs/error-analysis.md`.

## Architecture and trade-offs

The local extractive architecture, request path, security model, failure handling, cost, measured latency approach, production changes, and 100-times-traffic limit are documented in `docs/architecture.md`.

The implementation has no external provider cost and sends no profile data outside the machine. The committed evaluation currently reports a sub-millisecond in-process p95; interpreter startup is excluded.

## Known limitations and next steps

The current lexical retriever does not reliably handle broad summary questions, structured timelines, explicit skills intent, or diverse multi-role coverage. It is English-only and uses hand-maintained query aliases. It has no authentication, persistent audit logging, rate limiting, deployment configuration, or production monitoring.

The next three changes are intent-aware diversified retrieval, optional citation-constrained model synthesis with extractive fallback, and production security/observability controls. Full reasoning is in `docs/decisions.md`.

## Exercise notes

- Decisions, rejected alternatives, cuts, and next steps: `docs/decisions.md`
- AI usage and reuse disclosure: `docs/ai-usage.md`
- Self-review: `docs/self-review.md`
- Time spent: `docs/time-log.md`
- Source privacy and redaction policy: `knowledge/README.md`
