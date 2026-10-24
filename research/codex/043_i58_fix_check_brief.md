# Brief for Codex #43 — check of the I58 fixes for your 036 review (read-only)
Your 036: research/codex/036_i58_code_review_codex_answer.md (FIX FIRST, 3 blocking + notes). Fixes: research/iteration58_validation.py
(witnesses incl. first-target and both returned arms, reference witnesses, independent structure/bounds/grid without repair, OPF
success, full build manifests with a same-build guard, BusORPD by composition, initial-population assertion at collection,
post-budget sentinels 1e300 / (0, 1e150)), tests research/test_iteration58_validation.py (4/4). Also review the post-I57 chain
script /private/tmp/claude-501/-Users-danijel-Desktop-gadapt/fdaf0545-a06f-4145-b0ee-795267bb858e/scratchpad/post_chain.sh (applies
patch v4 by copying 10 reviewed files from the tested copy after checking gadapt/ is unchanged since the base commit, then
bit-identity hash + library tests, then I58 refs/test/check/analyse, then I59). For each 036 item FIXED / NOT FIXED; any
new bug; anything in the chain that could contaminate or misorder stages. Verdict RUN / FIX. Max ~450 words. Read-only.
