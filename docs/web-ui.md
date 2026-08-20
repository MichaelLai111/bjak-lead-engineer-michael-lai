# Python web UI

The visual interface is Task 4's user experience layer. It is a small Python-backed local web application, not a separate frontend build system.

## Run

```bash
python -m src.webapp
```

Then open `http://127.0.0.1:8000`.

## What to test visually

1. Click `AI experience` and confirm the answer is shown with source cards.
2. Click `Unknown fact` and confirm the status becomes `not_found` and the evidence panel says no evidence met the threshold.
3. Click `Current status` and confirm the stale-data source is visible.
4. Click `Adversarial` and confirm the request is refused without sources.
5. Review the Evaluation section for case pass rate, groundedness, citation accuracy, adversarial safety, categories, and known failures.
6. Scroll to How it works and follow the request path from Ask to Retrieve to Prove or Refuse.

## Endpoints

- `GET /api/health` verifies the server is running.
- `GET /api/summary` returns the committed evaluation summary.
- `POST /api/ask` accepts `{ "question": "..." }` and returns the same response shape as the CLI.

The server binds to `127.0.0.1` by default. Set `BJAK_WEB_PORT` to use another local port. It does not expose the application publicly unless the bind address is deliberately changed.
