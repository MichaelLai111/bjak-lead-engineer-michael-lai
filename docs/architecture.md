# Architecture

## Decision

The first working slice uses local weighted keyword retrieval and extractive answers. It does not call a generative model.

The system loads the committed normalized knowledge index, tokenizes the question, expands a small set of domain aliases, ranks chunks using term frequency and inverse document frequency, applies a minimum evidence score, and returns the highest-ranked source text unchanged. Every answer includes the stable chunk identifiers used to produce it.

## Why this architecture

The main failure to prevent is an invented qualification, employer, project, or achievement. Extractive output provides a stronger initial guarantee than prompt-only grounding because answer text must already exist in a committed source. It also keeps redacted career data on the local machine, removes provider retention questions from the working slice, and is fast enough for the small source set.

The simpler alternative was exact substring search. It was rejected because realistic questions use related words rather than exact CV phrasing. The current weighted retrieval remains small and inspectable while handling terms such as payments, frontend, reliability, and AI.

A hosted generative model was also considered and deferred. It would improve synthesis across sources and conversational tone, but it would add data egress, variable cost, availability failures, and a larger hallucination surface before the evaluation baseline exists.

## Request path

1. Normalize and validate the question.
2. Reject known prompt-injection and out-of-scope requests before retrieval.
3. Add explicit stale-data terms to questions asking about current status.
4. Retrieve the top configured chunks from the local index.
5. Apply the configured minimum evidence score.
6. Return a deterministic not-found response when no chunk passes.
7. Return source text unchanged with stable chunk and source identifiers.
8. Record end-to-end latency for the response.

There is no hidden prompt or tool call in this version. The response can be predicted from the index, configuration, and ranking code.

## Traceability

Each answer source exposes `chunk_id`, `source_id`, title, section, and retrieval score. The `chunk_id` is a stable hash of the source identifier, section, position, and text. A reviewer can find the same chunk in `knowledge/index.json` and then follow `source_path` back to the committed source.

If no chunk meets the evidence threshold, the assistant returns `not_found` and does not produce a career claim. If a request attempts to change scope or expose configuration, it returns `refused` before searching.

## Model choice and switching evidence

The current model choice is no generative model. A generative provider should only be introduced if evaluation shows that extractive answers have acceptable groundedness but fail usefulness on questions requiring synthesis across multiple sources. Any model-backed version must preserve the same retrieved sources, validate returned citations against allowed chunk IDs, and keep deterministic refusal outside the model.

The decision to switch would be based on measured multi-source answer correctness, citation accuracy, latency, cost, and privacy requirements rather than model popularity.

## Failure paths

| Failure | Behaviour |
|---|---|
| Missing index | Startup fails with a command telling the operator to rebuild it |
| Invalid index JSON | Startup fails without attempting an answer |
| Empty or vague input | The user is asked for a specific professional question |
| No relevant evidence | A deterministic not-found response is returned |
| Prompt injection | The request is refused before retrieval |
| Out-of-scope request | The request is refused before retrieval |
| Unusable source record | Index generation fails during validation |

A future hosted-model adapter would need explicit timeout, rate-limit, invalid-schema, and provider-outage handling. Its deterministic fallback would be the current extractive answer path, not an ungrounded retry.

## Security and privacy

- Raw CV files are excluded by `.gitignore` and are not required at runtime.
- Only redacted committed sources are loaded.
- No source data leaves the machine in the current implementation.
- No secrets are required.
- Configuration comes from environment variables documented in `.env.example`.
- Manifest paths are resolved and rejected if they escape the knowledge directory.
- Requests for passwords, API keys, or hidden instructions are refused.

Because no external provider is used, there is no provider retention or training exposure in this slice.

## Cost and latency

The direct provider cost is USD 0 per question. Latency is measured by the application for every request. The committed evaluation run will report a measured p95 over the complete dataset rather than an estimate.

## Production changes

Before production use, the system would need stronger language coverage, semantic retrieval, authenticated access, structured audit logs, observability, versioned source approval, encryption controls, abuse-rate limits, and a reviewed policy for adding or removing personal data.

At 100 times the expected traffic, the first constraint would be repeated index loading if each request starts a new process. A persistent service should load the index once, apply bounded concurrency, cache repeated safe queries, and export latency and refusal metrics. The next limit would be CPU-bound ranking as the number of sources grows, at which point a proper search index would replace the in-memory scan.
