# Decisions

## 1. Commit redacted sources instead of the raw CV

- Decision: commit a redacted but real professional profile and keep the original PDF outside Git.
- Rejected alternative: commit the raw CV so the reviewer sees every original field.
- Deciding constraint: the repository is public and the raw document contains contact details and identifying organization information.
- Trade-off: the runnable pipeline and factual work history remain reviewable, but employer and university names cannot be demonstrated publicly.

## 2. Use local extractive retrieval instead of a hosted language model

- Decision: rank local source chunks and return their text unchanged.
- Rejected alternative: use a hosted generative model to synthesize conversational answers.
- Deciding constraint: unsupported career claims are the highest-cost failure, while a model would also introduce data egress, secret management, variable cost, and provider failure modes.
- Trade-off: groundedness is easy to verify, but broad and multi-source questions are less natural and currently produce several false refusals or incomplete answers.

## 3. Use a source manifest and format loaders

- Decision: register sources in `knowledge/source_manifest.json` and load them through format-specific handlers.
- Rejected alternative: hardcode CV parsing directly into the assistant.
- Deciding constraint: the task asks for additional sources to be added without redesigning the system.
- Trade-off: there is slightly more structure than a one-file script, but provenance and source extension remain explicit.

## 4. Use deterministic evaluation instead of LLM-as-judge

- Decision: score status, required text, forbidden claims, source IDs, groundedness, and citation accuracy with deterministic code.
- Rejected alternative: ask another model to grade answer quality.
- Deciding constraint: the small redacted dataset supports exact labels, and model-judge variance would make the safety result less reproducible.
- Trade-off: semantic usefulness is only approximated by required strings, so the error analysis is still needed to explain incomplete but grounded answers.

## 5. Ship a CLI instead of a web interface

- Decision: provide single-question, interactive, and JSON command-line modes.
- Rejected alternative: build a React chat interface.
- Deciding constraint: the graded UX requirements are source visibility and clear fallback, both of which a CLI exposes with less setup and less unrelated code.
- Trade-off: the interface is less polished for non-technical recruiters but easier for the engineering reviewer to run and inspect.

## What was cut

- Hosted model synthesis was cut because the grounded deterministic baseline and evaluation needed to exist first.
- Embedding retrieval and a vector database were cut because the source set has only 19 chunks and lexical ranking is sufficient to prove the ingestion-to-answer path.
- A web UI, streaming, conversation memory, suggested questions, and confidence indicators were cut because none improves the core no-fabrication guarantee.
- Authentication, audit persistence, rate limiting, caching, and deployment automation were documented rather than implemented because this is a local exercise slice, not a production service.

These cuts keep the system small enough to understand and evaluate honestly. Adding them before resolving the known retrieval failures would increase surface area without improving the main safety property.

## Next three changes

1. Add intent routing and diversified retrieval for timeline, summary, skills, and multi-role questions.
2. Add an optional model-backed synthesis adapter that can only cite retrieved chunk IDs and always falls back to the extractive path.
3. Add production controls: authenticated access, audit logs, observability, source approval/versioning, rate limiting, and automated regression gates.
