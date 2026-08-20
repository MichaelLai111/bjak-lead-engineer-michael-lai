# Knowledge source policy

## Visible information

The assistant can use the following committed information:

- professional summary and total experience claim,
- redacted employer identifiers,
- role titles and employment dates,
- responsibilities, technologies, and measured outcomes,
- education period, degree, and field of study,
- declared technical skills,
- known gaps and stale-data boundaries.

The assistant cannot see contact details, social profile URLs, legal identifiers, addresses, employer names, the university name, compensation, team sizes, budgets, or any fact not included in the committed sources.

## Collection and cleaning

The original CV was reviewed locally and was not copied into the repository. Relevant professional facts were manually transcribed into `sources/resume_redacted.md` and `sources/profile.json`. Contact details and identifying organization names were removed before commit. Claims retain qualifiers such as "up to" so a measured result is not overstated.

## Structure and indexing

`source_manifest.json` declares each source and its handling policy. `scripts/build_knowledge.py` loads the manifest, validates every source path, and delegates parsing to the Markdown or JSON loader in `src/knowledge.py`.

Every generated chunk contains:

- a stable `chunk_id`,
- the parent `source_id`,
- the source type and title,
- a section name,
- searchable text,
- source metadata,
- redaction and synthetic-data flags.

The generated `index.json` is committed so reviewers can inspect exactly what retrieval will use.

## Adding another source

1. Add a UTF-8 Markdown or JSON file under `knowledge/sources/`.
2. Add one manifest entry with a unique `source_id`, relative path, type, title, and privacy flags.
3. Run `python scripts/build_knowledge.py`.
4. Review the generated chunks before committing them.

No ingestion code change is required for another source using a supported format. A new format only requires a loader registered in `LOADERS`.

## Known conflicts and gaps

The source set includes two explicit limitations in `issues.json`:

1. The CV has no employment entry from October 2022 through February 2023. The system must describe this only as an undocumented period; it must not call it unemployment, leave, study, or consulting.
2. The latest employment source ends in November 2025. The system must not infer a current employer, current title, or activity after that date.

When a question lands on either issue, the assistant must return the documented facts, identify the missing coverage, and avoid filling the gap. These cases will also appear in the evaluation dataset.

## Redactions and synthetic content

- Contact details were omitted rather than replaced.
- Employer names use stable redacted identifiers.
- The university name uses a stable redacted identifier.
- No synthetic career achievement is included.
- Example questions and test prompts may be synthetic, but they are not knowledge claims.
