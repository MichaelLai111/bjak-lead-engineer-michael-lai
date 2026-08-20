# AI usage disclosure

AI assistance was used heavily for this exercise.

## AI-assisted work

- analyzing the practical-exercise brief and turning it into an implementation checklist,
- drafting the repository structure and Python implementation,
- converting the locally reviewed CV into a redacted knowledge representation,
- drafting evaluation cases, deterministic scoring code, tests, and documentation,
- reviewing evaluation failures and proposing narrow fixes,
- running commands, tests, evaluation, Git commits, and repository checks.

## Review changes made after generated output

- Raw contact details, employer names, the university name, and the original CV were kept out of the public repository.
- The first evaluation run exposed fabricated-employer and certification-query weaknesses; the guards were changed and the unchanged dataset was rerun.
- A broad certification guard was narrowed after it incorrectly changed the adversarial response path.
- Five retrieval failures were retained and documented instead of tuning labels or lowering the evidence threshold to force a perfect score.
- Commit messages were kept short and ordinary rather than using generated summary-style messages.

## Where AI was deliberately not treated as authority

AI output was not treated as a source of truth for career facts. Only facts transcribed from the locally supplied CV or explicit data-quality rules were allowed into the knowledge base. AI was also not allowed to justify publishing raw personal contact data in the public repository.

Before submission, the candidate should personally verify every committed career statement, redaction, evaluation label, architectural claim, and measured result. That final factual review cannot be delegated to a model.

## Reuse declaration

No prior project, starter repository, application template, or third-party codebase was reused. The implementation uses the Python standard library. The original CV supplied with the exercise was used only as a local factual source and is not committed.
