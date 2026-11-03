# I65: original I55 620-NPZ end-to-end source attestation gate — 2026-11-03

**Status: PROSPECTIVE READ-ONLY GATE — FULL RAW NPZ REPLAY NOT RUN IN THIS SESSION.**
No optimizer, AC power flow, held-out COCO or new experiment was executed.

## Evidence already established

Original I55 source commit: 6b56fbc53ffc4d275ecef5e911ea4663474c9a08; original root Git tree: f88d221152fcb4157a8e1151a11b53cdfe8180b7. A 2026-11-03 independent GitHub tree comparison found exactly **620 archived original NPZ files, 12,319,037 compressed bytes, 21 library folders**, and no path/SHA/size changes on main. Ten nevergrad sphere/Rastrigin dimension-10 cells had failed and have no NPZ.

The source index I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json is itself Git blob **50ca2e96762447070a74309850cb1aa6586d3eb3**. A previous file-list/working-byte check could be weakened by altering both a manifest entry and the corresponding NPZ; its textual original-commit field was not an independent proof of that entry. The new attestation checks the manifest bytes against a pinned blob AND independently re-enumerates the original Git commit tree.

## Ordered independent gates

1. Authenticate the exact 620-record manifest blob and roster/total-size invariants.
2. Verify original commit root tree via git rev-parse and compare **all** original git ls-tree records, including file mode, path, SHA-1 and size, against the pinned manifest.
3. Read and compare the 620 original NPZ byte streams in the working tree, rejecting missing, changed or unexpected files.
4. Only after those gates pass, invoke the existing archived NPZ verifier to recompute 620 A-process SHA-256 call-sequence hashes and C/R detector flags, the I50/I55 318/358 digest pairing, and the 10/10 archived emukit VECLIB post hoc control. Emit a JSON attestation with full_attestation_pass=true only if ALL checks actually passed. Failure emits BLOCKED and exit code 2.

The 13 new fail-closed synthetic unit tests and the existing 12 source-manifest synthetic tests passed together **25/25 locally**. These tests do not substitute for replay of the original NPZ binary arrays.

## Execution

Full local Git clone: run

    python research/i65/archive_review/i55_full_npz_attestation.py --repo-root . --output /tmp/i55-620.json

Alternatively, the new GitHub Actions **I65 I55 frozen NPZ read-only attestation (manual)** workflow checks out full history and runs the gate, saving the JSON as an artifact. **Manual workflow_dispatch ONLY; not triggered by committing this gate.** It installs NumPy and runs no optimizer, PF or COCO experiment. Full workflow execution has NOT been verified in this session.

## Limits for the doctoral manuscript

Even a full 620-NPZ PASS would reconstruct only the A-process traces. A-prime/B traces were archived as digests rather than those 620 NPZ array files; a future PASS must not be described as re-running or independently reproducing all three physical processes. The original H55a–c supported and H55d not supported decisions remain unchanged. Detection specificity, universal defect prevalence, causal novelty and author/supervisor approval remain unproven. Historical I50 C1 nonspecificity and emukit thread-confound caveats remain binding.

**Scientific status:** draft-only, NO-FREEZE, held-out COCO NOT_RUN, originality NOT_ESTABLISHED, M6/C1 unsigned.
