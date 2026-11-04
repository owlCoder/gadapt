# I64-R original E freeze and off-Git R digest readiness — source-only correction

**2026-11-04. DRAFT / NO-FREEZE / NOT_ESTABLISHED.**

## Historical E freeze schema (original Git source, not a new experiment)

The immutable original E source `research/i64/e_study.py`,
Git blob `b72a4bae65967c925a7f0a683a50f5144270ba34`,
defines development candidates only for `cma`, `ipop`,
`bipop` and `es11`. Original `stage_freeze()` writes a
`params` map containing these **four tuned configurations**.
The GAdapt-M default is **not** a fifth tuned key:
`params.get('gadapt')` correctly evaluates to `None`.
Original R code `research/i64/r_study.py`, blob
`4e8e33e07894ae1006c03cb0ada3566254fb9907`,
creates paired tasks using exactly `params.get(cfg)` for
`cfg in ('gadapt','ipop')`.

An earlier I64-R custody gate incorrectly required both
`gadapt` and `ipop` to be stored as explicit frozen keys
when original R task rows were present. That would reject
source-faithful records even if the original off-Git R archive
were recovered. The corrected gate validates the four
originally tuned keys and checks GAdapt's `None` and IPOP's
frozen dictionary, without invoking any algorithm.

The SHA-256 original E roster is still enforced for every
present input; exactly **66 of 67** source items, including all
**44 of 44 required** inputs, were previously authenticated by
[post-merge I55 CI 41883469505](https://github.com/owlCoder/gadapt/actions/runs/41883469505).
The optional combined E `run.json.gz` remains **MISSING**.

## Original off-Git R full-digest readiness

The historical R source record names an approximately 8 MB
off-Git `run.json.gz` whose only published digest fragment is
`f23046f6...3618` (8 hexadecimal prefix + 4 hexadecimal
suffix = 48 digest bits). A file having that abbreviated marker,
even with 4,200 plausible records and matched E inputs, is
not sufficient for a trusted original-data attribution.

The revised `i64_r_off_git_raw_recovery_gate.py` therefore
distinguishes:
- **Structural inspection**: possible only when candidate R
  bytes exist and pass the archived source contract; this
  never reconstructs or generates any missing record.
- **Read-only independent R-bootstrap readiness**:
  requires the original raw file **plus** a matching full 64-hex
  SHA-256 provided from a separately trusted archival record
  **plus** a complete authenticated R roster and SHA-256
  verified required E inputs. The gate cannot independently
  judge whether the externally supplied full digest genuinely
  originated before this recovery. Custodian provenance and
  independent human evidence review remain mandatory.

Five synthetic tests mock the R record parser only to
isolate the digest boundary; they explicitly do **not**
simulate original R results or validate scientific conclusions.
Existing synthetic E/R checks continue to fail closed on
missing IPOP tuning, invented GAdapt tuning, forged task
parameters, corrupt bytes and incomplete record rosters.

**No R 4,200-record source has been found or re-created.**
No original R bootstrap, optimizer, PF/AC/OPF, held-out
COCO or new objective evaluation is executed.
M3/M5/M6/C1 independent decisions remain unsigned.
