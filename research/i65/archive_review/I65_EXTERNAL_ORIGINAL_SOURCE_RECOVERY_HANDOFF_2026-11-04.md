# I65 — Owner-machine recovery handoff for original I64-R and I55 A′/B source

**2026-11-04 — evidence recovery only; no recreation of an experiment.**
Technical status: `DRAFT / NO-FREEZE / NOT_ESTABLISHED`.

## Original I64-R source to retrieve

Original R seed data were recorded outside Git in an approximately 8 MB
gzip file named `research/results/iteration64_r/run.json.gz`, with
**4,200** original records. The *abbreviated* historical SHA-256
marker is `f23046f6…3618`. The Git-tracked source directory contains
only `analysis.json.gz` (Git blob
`59025d6cc052baef76b14e5496962704bdb7604a`) and
`check_repro.json.gz` (Git blob
`11ca5fdfabfe6ce20cb54752a2a41fe8e2deee3d`).

Independent searches of **15 visible active branch tips**, the
archived repository paths, accessible connected Drive and filename-only
Library, plus GitHub Actions runs on **2026-10-29** (zero such runs)
have not located the original R raw file. These checks **do not** rule
out original data on the experimental machine, a backup, an inaccessible
cloud drive, detached Git refs, or another repository.

### Read-only operator procedure on the original experiment computer

From a terminal on a computer containing the original working copy:

```bash
# First find only the originally produced file. Do not invoke r_study.py run.
find "$HOME" -type f -path '*/iteration64_r/run.json.gz' -print 2>/dev/null

# For a real candidate, calculate the complete digest and size.
sha256sum '/original/path/research/results/iteration64_r/run.json.gz'
wc -c '/original/path/research/results/iteration64_r/run.json.gz'
```

Capture the unmodified original file and the calculated full
64-hex-digit digest, plus (if possible) contemporaneous independently
created checksum/manifest/console evidence. **The present 12-hex-digit
marker (8-prefix/4-suffix) does not authenticate the full digest**.
Do not pretend that a newly computed full SHA is a previously trusted
historical checksum.

In the repository with the Git-pinned original E and R analysis files
available, run the existing **non-mutating** gate:

```bash
python research/i65/archive_review/i64_r_off_git_raw_recovery_gate.py \
  --repo-root . \
  --raw-run '/original/path/research/results/iteration64_r/run.json.gz' \
  --output /tmp/i64_original_raw_source_structure.json
```

This checks exact **4,200-record seed/config/pair roster**, ordered
events, original-budget structure, R/E build lineage and the
historical truncated SHA marker, and reports whether the frozen E
run_part files and normalizers are accessible. The output
`STRUCTURE_MATCHES_ARCHIVED_R_SPEC` is a **structural** success only.
Without an independently trusted full historical digest its result
explicitly remains
`ONLY_48_BIT_HISTORICAL_ABBREVIATION; FULL_DIGEST_NOT_ATTESTED`.

If and only if a **separately trusted original 64-hex-digit SHA-256**
can be documented, additionally run the same command with:

```text
--expected-full-sha256 <independently trusted 64-digit sha256>
```

Do not run a fresh optimizer to fill missing data. A verified source
can then be handed to an independent analyst for a **read-only**
20,000-draw seed-level R bootstrap using the already frozen
algorithm and RNG seed 70; that analysis is **NOT performed by
this handoff**. Do not alter any preregistered R hypothesis decision.

## Original I55 A′/B coordinate sequences

The **620 valid A-process NPZ** sources contain A only. They do
not contain A′/B original full coordinates, objective measurements,
or phases. Historical cell JSON establishes **digest-level** A/A′/B
relationships but cannot reconstruct those byte sequences.

Look for contemporaneous originals on the same machine/backups,
with source path/creation context and full digest before moving
anything. In particular, locate any explicit A-prime, B, hashseed,
or negative-control trace collections. **Do not** call optimizers,
rerun I55 A′/B seeds, or generate synthetic stand-ins. Any candidate
requires an independent byte/roster/schema authentication against
the frozen 21-library × 3-function × 2-dimension × 5-seed design and
the archived per-cell sequence hashes. Digest agreement alone does
not provide a second independent original A′/B numerical oracle.

## Minimum provenance handoff (not filled by the AI)

| Required item | Owner/reviewer evidence |
|---|---|
| Original file path and storage location | PENDING |
| Full SHA-256 of the original R gzip | PENDING |
| Independently dated source digest/manifest or trusted custody record | PENDING |
| Complete 4,200 original records and frozen E lineage structural gate | PENDING |
| R raw-seed bootstrap performed independently without new optimizer runs | PENDING |
| Original I55 A′/B raw trace candidates and independently authenticating hashes | PENDING |
| Reviewer identity, date and authorization for any scientific claim | PENDING |

The correct current treatment is **source not yet recovered**.
An accessible historical source is a prerequisite, not a human
signoff or a substitute for prior-art/physical-model validation.

**Do not close these two scientific gates without real original files.
DRAFT / NO-FREEZE / NOT_ESTABLISHED; COCO NOT_RUN.**
