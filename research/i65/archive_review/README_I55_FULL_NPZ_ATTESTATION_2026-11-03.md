# I55 original 620 NPZ source-to-detector attestation

This is a **prospective read-only replay procedure**, not a claim that all 620 original traces have been recomputed already.

With a **full Git checkout** containing the original I55 NPZ blobs and the original commit 6b56fbc, run:

    python research/i65/archive_review/i55_full_npz_attestation.py --repo-root . --output /tmp/i55-620.json

Or open Actions, select **I65 I55 frozen NPZ read-only attestation (manual)** and select Run workflow. That new workflow has a manual-only trigger, read-only contents permission and no optimizer or physics execution. The JSON result is retained as an artifact.

The four gates require: the SHA-pinned manifest itself, exact correspondence to the original Git commit tree, the actual original 620 local NPZ file bytes, and a complete independent A-trace SHA-256 and original detector-flag replay. Success requires full_attestation_pass=true AND 620 checked original traces AND no errors. Failed or unavailable sources produce BLOCKED, never an invented PASS.

The archived A-prime/B comparisons are digest-level only; their full numerical arrays are **not** among the 620 archived A-trace NPZ files.

See I65_I55_ORIGINAL_620_NPZ_END_TO_END_ATTESTATION_GATE_2026-11-03.md for evidence, controls and scientific limitations.
