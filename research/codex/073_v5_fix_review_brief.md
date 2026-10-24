# Brief for Codex #73 — review library fix v5 before it is applied (read-only)
Patch: research/patches/constraint_api_v5_fix.patch (against the committed v4 library, commit 08a5b75). It fixes your Codex 050
blocking finding (research/codex/050_library_patch_precommit_codex_answer.md: the executor read cost_finder.best even with
constraint_handling=None) and two README wordings and a ga_results comment; adds a regression test to tests/test_constraint_handling.py.
Claimed: default seeded call-sequence hash unchanged (afcdb859...), 72/72 library tests, the new test fails on v4 and passes on v5.
Check: (1) correctness and completeness of the fix (any other place that reads constraint-handling state on the default path);
(2) the default path is unchanged (reason from code); (3) README text accurate (positive weight; "legacy" policy allowed);
(4) the regression test really exercises the bug; (5) does v5 change the I56 instrument behaviour (research/iteration56_cht_study.py
uses constraint_handling=None and its own CHTCostFinder without a `best` attribute) — I61 gates on bit-identity. You may apply
the patch in a temporary copy OUTSIDE the repo to run tests (python -B). Verdict APPLY / FIX FIRST. Max ~400 words.
