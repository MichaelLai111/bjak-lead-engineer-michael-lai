# Self-review

If this arrived as another engineer's pull request, I would request these two changes before production use.

## 1. Replace alias-only ranking with tested intent routing

The evaluation shows false refusals for broad summary and timeline questions and incomplete coverage for a multi-role question. I would ask for structured routing for summary, timeline, skills, and comparison intents, plus ranking diversification and regression tests for all five current failures.

## 2. Add a production security and observability boundary

The local CLI has no authentication, persistent audit trail, abuse controls, or deployment monitoring. I would ask for an authenticated service boundary, structured security-safe logs, request and source version IDs, latency and refusal metrics, rate limits, and automated evaluation gates before exposing the assistant to external users.
