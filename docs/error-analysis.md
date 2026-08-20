# Error analysis

The committed evaluation run passes 20 of 25 cases. All responses remain grounded and correctly cited, but five cases fail usefulness or retrieval expectations.

## Failure 1: multi-001

- Question: `Summarize your fintech and insurance experience.`
- Expected: evidence covering both claims and BNPL work from both source representations.
- Observed: the result includes insurance detail and general cross-industry summaries but no BNPL detail.
- Failure type: retrieval diversity and answer coverage.
- Root cause: multiple high-scoring insurance and summary chunks consume the three answer slots. Ranking treats every chunk independently and does not reserve coverage for separate concepts or roles.
- Safety impact: low. The answer is incomplete but contains no unsupported claim.
- Next fix: add intent-aware diversification, such as maximum marginal relevance or one result per matched role/source section, then add a coverage check for multi-part questions.
- Regression case: retain `multi-001` and require both `claims` and `BNPL`.

## Failure 2: multi-004

- Question: `Give me a timeline of your two documented professional roles.`
- Expected: both documented role dates.
- Observed: deterministic `not_found`.
- Failure type: vocabulary mismatch.
- Root cause: `timeline`, `documented`, and `professional roles` do not overlap strongly enough with the stored role records to pass the evidence threshold. The alias table has no timeline-to-dates expansion.
- Safety impact: low. The system refuses rather than inventing a timeline.
- Next fix: add a structured timeline intent that retrieves records with `section=experience` and sorts them by parsed dates. This is preferable to adding more ad hoc synonyms.
- Regression case: retain `multi-004` and verify chronological ordering as well as both dates.

## Failure 3: ambiguous-001 and ambiguous-002

- Questions: `Tell me about your work.` and `What did you build?`
- Expected: a broad professional summary or representative project evidence.
- Observed: deterministic `not_found` for both.
- Failure type: underspecified-query handling.
- Root cause: after stop-word removal, these questions leave too little discriminative vocabulary. The current system has no default summary route and intentionally avoids answering when lexical evidence is weak.
- Safety impact: low. This is a false refusal, not a fabricated response.
- Next fix: route short broad questions to a reviewed summary chunk and return suggested narrower questions. Keep the default summary source explicit rather than lowering the global threshold.
- Regression cases: retain both cases and verify that the selected summary remains source-backed.

## Failure 4: ambiguous-005

- Question: `What are your strongest technical skills?`
- Expected: the committed skills section including React, Python, and AWS.
- Observed: role summaries without the requested skill list.
- Failure type: field prioritization.
- Root cause: query expansion introduces role-related technology terms that score structured role records above the dedicated Markdown skills chunk. Section names and source fields are not currently weighted.
- Safety impact: low. Returned facts are valid but do not answer the question.
- Next fix: add section-aware ranking so an explicit skills intent boosts `section=skills`; alternatively, index the skill list as individual structured records.
- Regression case: retain `ambiguous-005` and require the dedicated skills source.

## Why these failures remain

The changes required to solve them introduce routing, structured date handling, or ranking diversity. Those are meaningful architecture changes rather than safe threshold tweaks. Inside the exercise time box, keeping the grounded baseline and reporting the remaining retrieval limitations is a better trade-off than tuning individual questions until the dataset reports 100 percent.
