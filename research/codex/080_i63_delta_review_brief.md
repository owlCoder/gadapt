# Brief for Codex #80 — targeted check of the I63 driver delta BEFORE the real gate (read-only; Serbian Latin; max ~700 words)
git diff 1c94a63 HEAD -- research/iteration63_replication.py research/test_iteration63_replication.py  (read the files directly). Codex 079 fixes were applied
(your code, adapted); a pipeline rehearsal with I63_TESTING=1 (tiny B, relaxed thresholds, uniform tilt fallback, temp dir) ran gate..analyse end to end.
Check ONLY: (1) is any TESTING branch able to leak into the production run (env var absent -> B=12000, SIM 1000/2000/20000, thresholds 10/8/8/0.02 and
0.8/0.05, FXT_GRID 27, N_GRID (80..480), REHEARSAL_SEEDS 1..20, ESS rule, no uniform fallback)? (2) the STOP/attempts CLI wrapper: can a protocol STOP be
bypassed, or a crash wrongly become terminal? (3) the execute() archive: are the first attempts of failed runs and repeats kept, and does a repeated
failure STOP in every stage (fxt, rehearsal, test) with the attempts already saved? (4) stage_gate: provenance before/after, no fallback, roster hashes;
does require_provenance for 'normalizers' work with the patched verify_chain (gate/roster identity)? (5) any remaining blocking defect. Verdict:
GATE NOW / FIX FIRST (exact code).
