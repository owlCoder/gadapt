**FIX FIRST.** Read-only and result-blind; no prohibited results or logs were opened. References below are to `research/iteration61_replication.py` unless stated otherwise.

The six blocking findings:

1. **Roster preflight/reuse — closed.** All 15 scenarios are checked, both development scenarios and ≥1 test scenario per network are required, and subsequent stages reuse the persisted roster (`iteration61_replication.py:269`, `:289`, `:406`). Its hash enters the gate manifest.

2. **Fallback gate and hash binding — partially closed.** CLI and spawn-child imports preserve `I61_LIBRARY` (`:35`); pre-populating REPO/HERE prevents I56’s insertion from displacing it. The gate’s pytest runner also establishes the correct order (`:377`). Gate creation is guarded, and current/fallback outcomes are retained (`:382`, `:399`, `:423`).

   Remaining edits:
   - At `:410`, verify an existing fallback directory against **17e9ce7**; currently any existing directory is reused.
   - At `:371`, catch execution exceptions, record a failed current gate, and continue to fallback. A `run_plain` exception currently escapes before fallback.
   - At `:391`/`:142`, bind **both** attempts and their build manifests, retain/hash complete regression stdout/stderr, and verify the selected-result/archive/test-source hash chain. Downstream checks currently verify only `gate.json.gz` and roster; stored `result_sha256` is never followed.
   - In `research/test_iteration61_replication.py:9`, import I61 before I56; otherwise fallback-configured driver tests preload the repository library before I61 selects LIB.

3. **Create-once freeze/build provenance — partially closed.** Freeze overwrite and frozen-build comparison are addressed (`:156`, `:704`). However, producer manifests contain no committed **output hash**. Consumers compare sidecar provenance, then accept whichever artifact currently occupies the filename (`:152`). An in-memory probe confirmed acceptance of a foreign output.

   **Edit:** publish a completed producer manifest containing its output SHA-256; verify that hash and the producer’s recorded input bindings recursively before consumption. Do not overwrite a completed sidecar before successful production. Extend final validation to gate/roster/frozen dependencies. Add `before = require_provenance(...)` and `finish(...)` to **power** (`:649`) and **analyse** (`:863`), immediately before publishing outputs; both currently omit final revalidation.

4. **Consumed-reference guard — closed.** Both check and analysis enforce the consumed artifact hash, reference mapping, and every task’s embedded reference (`:774`, `:814`, `:872`).

5. **Empty witness set — closed.** Check derives the expected set and permits zero expected/verified witnesses; analysis accepts matching zero counts (`:786`, `:835`, `:867`).

6. **Development witness coverage — partially closed.** Development L*, stopcheck targets, and rehearsal best solutions are now covered and hash-bound (`:816`). Selection and FX-T records still contain target/best witnesses that are omitted. **Edit:** add `select_b` and `fxt` to `INPUTS["check"]` and the witness sources, covering their first-target and reported-best witnesses too.

The four non-blocking findings:

- **Weighted attainment diagnostics — closed:** both tilts report rates by network/arm (`iteration61_replication.py:658`).
- **Pairing assertions — closed:** grouping includes configurations sharing network/scenario/seed, with calls across paired optimization stages (`:312`, `:440`, `:457`, `:485`, `:509`, `:564`, `:714`, `:741`).
- **Exclusion counts/rates — closed:** denominators derive from frozen roster × n, including wholly missing units/cells (`:875`, `:885`, `:891`).
- **Binary comparison — closed:** recursive, type-aware float-bit comparison is used (`:346`, `:368`).

**Additional introduced blocker:** analysis initializes planned units but then admits unexpected units through `setdefault`; these can enter primary inference (`:879`). Reject unplanned unit keys and duplicate arm records before assembling complete units.

**Normal-order check:** no missing producer manifest or stage-name/argument mismatch found. `power` has dedicated zero-argument dispatch; CLI `analyse` correctly uses the `analysis` dependency key (`:127`, `:926`).

Validation: ten pytest tests passed without disk writes; the create-once test passed separately with in-memory storage. No full gate or experiment was run.