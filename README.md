# bjak-test

Grounded professional-profile assistant built for the BJAK Lead Engineer practical exercise.

The repository is developed in five small stages. The current stage includes the personal knowledge layer and a local grounded assistant backend.

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
