**Verdict: FIX.** The fixes substantially improve I58, but validation can still report success without validating required evidence.

1. **036 witnesses — NOT FIXED completely.** Both returned arms, first-target vectors/indices and reference witnesses are now captured. However, [stage_check](/Users/danijel/Desktop/gadapt/research/iteration58_validation.py:388) silently skips missing witnesses and never compares returned `min_cost`, objective or violation against recomputed values. A returned vector passes whenever structurally valid unless `feasible` is explicitly `True`, even if PF fails. Require expected witnesses and verify available reported quantities, including G0’s scalar.

2. **036 independent checker — NOT FIXED completely.** Raw-case reconstruction, grouping, bounds, grid checks without repair, OPF success and finite PF-output checks are implemented. **New bug reproduced:** NaN controls bypass bounds/grid comparisons and return `valid=True, converged=False`. Combined with item 1, such returned vectors can pass. Reject nonfinite controls before PF ([validation](/Users/danijel/Desktop/gadapt/research/iteration58_validation.py:355)).

3. **036 provenance — NOT FIXED completely.** Both manifests now include library-tree hashes, patch/research hashes and versions. But settings remain a short subset rather than complete resolved GA/external-method settings. The [same-build guard](/Users/danijel/Desktop/gadapt/research/iteration58_validation.py:245) compares only library/patch hashes, allowing changed research code or dependencies between references and tests. Compare those fields too and verify provenance after collection.

4. **BusORPD — FIXED.** Composition preserves the unchanged delegate and expands grouped VG controls correctly.

5. **Initial populations — FIXED** for successful paired runs: collection checks both reference/test pairs for equality and exactly 32 entries.

6. **G0/G1 configuration, seeds/budgets/reference rules and analysis weighting/bootstrap — FIXED / retained satisfactory.** The post-budget sentinels correctly prevent unevaluated candidates from improving the reported incumbent under these evaluators.

The [chain](/private/tmp/claude-501/-Users-danijel-Desktop-gadapt/fdaf0545-a06f-4145-b0ee-795267bb858e/scratchpad/post_chain.sh:21) has the correct nominal stage order, but **does not stop on validation failures**: I58’s checker prints failures and exits zero; analysis ignores its result. I59’s checker also exits zero, although its analysis suppresses inference when failures are recorded. Make validation failure propagate a nonzero exit before downstream stages.

The tracked baseline guard currently passes. It ignores untracked importable files, and the mutable copy source has no pinned content hashes; bit-identity sampling and library tests do not establish exact patch identity. Pin and verify the copied build, and include research tests before expensive stages.

**Verification:** 4/4 I58 tests passed. In-memory probes reproduced acceptance of missing witnesses and failed-PF returned vectors. No files changed.