# Historical original files and compatibility aliases

The physical migration preserved the Git blob SHA of **341 original files** (see the [migration manifest](../../MIGRATION_MANIFEST_2026-11-01.json)). Among current `_SR.md` entries here, **87 are regular, untranslated Serbian historical reports** and **20 are symlink aliases pointing to active English reports** at the research root. They are not all 107 distinct Serbian documents.

Start with the [English original-report index](INDEX_EN.md) or [evidence synthesis](../../EVIDENCE_SYNTHESIS.md), not with an unstructured filename list.

Do **not** execute original Python CLI scripts from this folder. First run `python research/compat/restore_legacy_paths.py --verify`, then explicitly opt into `--apply --verify` in a real clone. Historical regression remains not fully tested after migration. No experimental rerun or frozen report rewrite occurred.
