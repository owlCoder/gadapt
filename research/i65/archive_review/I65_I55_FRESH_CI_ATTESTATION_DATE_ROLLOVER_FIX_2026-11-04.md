# I55 original-source CI: date-safe freshness, immutable source SHA custody

**2026-11-04 | READ-ONLY CI RELIABILITY FIX | DRAFT / NO-FREEZE / NOT_ESTABLISHED**

## Confirmed problem

The original full-620 NPZ attestation writer
`i55_full_npz_attestation.py` includes the dynamic value
`"date": str(date.today())`. The 620 detector census and NPZ
phase/C1-C2 reports then store **the SHA-256 of that current full
attestation file**. Therefore a correct read-only rerun on the
following day changes the bytes of **all three machine-readable
reports** even if the immutable original 620 NPZ source files, objective
values, detector flags and scientific conclusions are identical.

The newer draft I55 workflow incorrectly compared *newly generated
census and phase output files* to the historical completed original
run 41804478669 **byte-level SHA-256 values**. This creates a false
CI failure on any day when the full report carries a new date. It
mistakes a dated output/report checksum for an immutable **input
source identity**.

The correct permanent input evidence remains the original Git
commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`,
original root tree `f88d221152fcb4157a8e1151a11b53cdfe8180b7`,
and original 620-NPZ manifest Git blob
`50ca2e96762447070a74309850cb1aa6586d3eb3`.

## Correction

1. [Fresh original full/census/phase SHA256 lineage gate](
i55_fresh_original_report_lineage.py) is pinned to the original
Git input identities and requires all **620/620 original blob/trace
attestation checks PASS**. It then dynamically SHA-256 hashes the
new full-620 attestation and requires **both current census and
current phase outputs** to refer to **exactly that** latest full
report, rather than a previous execution's dated checksum.
2. The gate checks C1=2,105, C2=18,779, total original calls
295,445, C1∩C2=1,956, C1-positive cells=109, full signed
corner first visits=149 and both-sign cells=40; all original
21-library, three-function and two-dimension C1/C2/calls/repeat
source strata must independently reconcile, including the 1,200
historical post calls. A modified original source, forged output,
missing trace or stale census/phase linkage is **rejected**.
3. [Node.js gate for current full/census/phase SHA provenance](
i55_fresh_original_report_lineage_node.cjs) now guards the
separate [13-case signed NPZ ledger regression suite](
test_i55_109_signed_corner_source_weighting_gate.cjs) and
the Node machine report writer. The immutable 109 original
Git-blob-pinned signed-source ledger and roster remain fixed.
4. The direct "40 cells with both signed corners" CI step now
uses the same **fresh linked reports** and saves their current
SHA-256 values, without pretending that the output JSON had the
same bytes as run 41804478669. The workflow uploads
`i55_620_fresh_source_lineage.json` as an additional receipt.

## Tests actually executed, independent of latest-head GitHub CI

**12/12 new Python adversarial tests PASS locally** using the
**original** GitHub run 41804478669 artifacts, including:
- original 620 successful source attestation + census + phase;
- a simulated **2026-11-05** full report whose date and SHA-256
  change, with both dependent output links updated: **PASS**;
- the same new report with **stale old dependent hashes: FAIL CLOSED**;
- altered original Git tree, missing original NPZ bytes, forged
  original trace replay flag, altered source C1/C2 counts,
  library-stratum population, missing function, false Git
  authentication and replaced manifest: **FAIL CLOSED**.

The exact source program Git blob
`59bc9fc42f10e0300c95076ab2b0c64b49f188ac`
and test blob
`dc4a8cfeb4de69479c56d93721492c1b0a2f5291`
are byte-identical to the locally executed scripts.
The original archived full output SHA is
`9a6a5a3d32120394798ccf47675aaff403b82062fac240267a47e327283fa111`;
the baseline census SHA is
`a0bfb1bfeaa2979ae8f195ffbcde8c9ff2c45b0562f96ecdf7915e229963c4ea`,
and the baseline phase SHA is
`14ee6ea5839b59f3b15403921b7ed76a45c72a0ec39321f5aefde16dbe21d82f`.
They remain historical receipts, **not required future output hashes**.

The exact [Node source-lineage helper](
i55_fresh_original_report_lineage_node.cjs) also passed a direct
read of the original successful CI triple, a simulated next-day
recomputed SHA linkage, and a deliberately broken phase SHA linkage
that was correctly rejected. Node and Python require **no new
optimizer or numerical benchmark execution**.

## Boundaries

This is a CI false-negative prevention and original-source integrity
improvement. It **does not** authorize rerunning original experiments
or imply any new M3/M5/M6 physical/originality approval. The previous
86-test full-clone I55 source CI remains successful for its historic
code; **no new GitHub Actions result for the changed PR HEAD is
confirmed**. The proposed latest workflow now includes 12 additional
Python checks along with the newer 13 Node and other pending source
tests; do not combine expected counts into a claimed CI pass.

Original I55 A′/B raw streams and the original I64-R 4,200-run raw
archive are still unavailable, human scientific signatures unsigned,
and held-out COCO NOT_RUN/NOT_AUTHORIZED.

**DRAFT / NO-FREEZE / NOT_ESTABLISHED; main remains unchanged.**
