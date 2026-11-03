# I64-R off-Git source audit and family-resampling tools (2026-11-03)

- [Scientific audit and limitations](I65_I64_R_OFFGIT_SOURCE_AND_FUNCTION_FAMILY_STRESS_2026-11-03.md)
- [Derived nine-family 100k resampling ledger](I65_I64_R_FAMILY_VARIATION_STRESS_2026-11-03.json)
- [Family resampling read-only script](i64_r_family_resampling_audit.py) and [10 tests](test_i64_r_family_resampling_audit.py)
- [Original off-Git R source recovery gate](i64_r_off_git_raw_recovery_gate.py) and [11 tests](test_i64_r_off_git_raw_recovery_gate.py)

Original reported I64-R seed-only H64r3 remains `SUPPORTED` for fixed 21 pairs; independent raw-seed bootstrap replay remains `NOT_RUN` until the ~8 MB run.json.gz intentionally kept outside Git is recovered. **Do not conflate this audit with original preregistration**. The nine-family resampling band is deliberately **not** a confidence interval over all functions.

Usage:

```sh
python research/i65/archive_review/i64_r_family_resampling_audit.py \
  --analysis research/results/iteration64_r/analysis.json.gz \
  --replications 100000 --seed 7001 \
  --output /tmp/i64_r_function_family_diagnostic.json

python research/i65/archive_review/i64_r_off_git_raw_recovery_gate.py \
  --repo-root . --raw-run research/results/iteration64_r/run.json.gz \
  --output /tmp/i64_r_recovery_gate.json

python -m pytest -q research/i65/archive_review/test_i64_r_family_resampling_audit.py \
  research/i65/archive_review/test_i64_r_off_git_raw_recovery_gate.py
```

No optimizer, physical objective, COCO, PF or OPF calls; no edits to frozen experiment files. Check the audit report before citing any numerical statement.
