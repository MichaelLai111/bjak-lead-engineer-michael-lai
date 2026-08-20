# bjak-test

Grounded professional-profile assistant built for the BJAK Lead Engineer practical exercise.

The repository is developed in five small stages. The current stage implements the personal knowledge layer with redacted source material, explicit provenance, and documented data gaps.

## Knowledge layer

The committed source material is redacted because this repository is public. Contact details, employer names, and the university name are not included. The remaining role dates, responsibilities, technologies, and measured outcomes are based on the supplied CV.

Build the normalized knowledge index:

```bash
python scripts/build_knowledge.py
```

The command reads `knowledge/source_manifest.json` and writes `knowledge/index.json`. New Markdown or JSON sources can be added by creating the file and registering it in the manifest; the ingestion code does not need to change.

See `knowledge/README.md` for the source policy, schema, redactions, and known gaps.
