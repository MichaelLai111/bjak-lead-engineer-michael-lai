# User experience

The interface is a command-line application for the reviewer or engineer running the repository. A CLI was chosen because it is install-free, makes source identifiers visible without extra navigation, supports scripted evaluation, and keeps the time-boxed work focused on grounded behaviour rather than visual polish.

## Single question

```bash
python -m src.cli --question "What experience do you have with AI?"
```

The output separates the answer from its sources and displays status and measured latency.

## Interactive mode

```bash
python -m src.cli
```

Type `exit`, `quit`, or `:q` to close the session.

## Machine-readable mode

```bash
python -m src.cli --question "Where do you currently work?" --json
```

JSON output preserves response status, answer text, source identifiers, scores, latency, and fallback reason.

## Required visible behaviours

For an answerable question, the CLI shows every source chunk behind the answer. For an unsupported, adversarial, or out-of-scope question, it shows a deterministic fallback, `Sources: none`, and a machine-readable reason.
