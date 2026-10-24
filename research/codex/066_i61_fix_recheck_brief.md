# Brief for Codex #66 — re-check I61 driver after your Codex 065 findings (read-only, result-blind, short)
Your review: research/codex/065_i61_fix_check_codex_answer.md. Fixes: `git diff 6604b8a -- research/iteration61_replication.py
research/test_iteration61_replication.py` (tests 12/12). Do NOT open i58_test/check/analysis, i59_*, i60_* results or logs.
For each remaining item (fallback tree verification, gate exceptions, both attempts bound + hash chain, test import order,
output-hash producer manifests + recursive chain + create-once per stage, power/analyse revalidation, select_b/fxt witnesses,
unplanned units): closed or not. Then simulate the normal order mentally (gate -> dev_ref -> select_b -> fxt -> stopcheck ->
rehearsal -> power -> test_ref -> test -> check -> analyse): any spurious STOP (e.g. stages that publish then STOP; the frozen
manifest written inside test_ref before publish; check's INPUTS now include select_b/fxt)? Verdict READY / FIX FIRST with exact
edits. Max ~500 words.
