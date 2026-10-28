# Brief for Codex #77 — draft a NEW preregistered successor design "I63" (read-only; return text; Serbian Latin; max ~1800 words)
Context: Codex 076 (research/codex/076_next_direction_codex_answer.md) said a bigger-B-only I63 is NO-GO (T=h/B shrinks as B grows; the
I61 window [0.3,0.8] with four simultaneous medians cannot pass), but a reasoned new design is conditionally GO. Read
research/ITERATION61_PROTOCOL.md, ITERATION61_REPORT_SR.md, results/iteration61/select_b.json.gz (records[*].first_target, task),
research/ITERATION56_REPORT_SR.md and iteration56_cht_study.py / iteration61_replication.py for the instrument.
Observed in I61 dev data (descriptive, post hoc): the target f <= 1.01 L* + 0.01 MW is unreachable by AD-N within 12000 calls on some scenarios
(case30 j=0: 0/10; case39 FR j=1: 0/5), and reached at very different times on others. So the failure is the TARGET/ESTIMAND definition, not B.
Task: design ONE successor study that tests the same scientific question as H56a (does adaptive-vs-tuned-fixed gap depend on the CHT, FR vs SP)
with an estimand robust to this heterogeneity. Candidate ideas to evaluate (choose/improve, reject with reason): (i) per-scenario target = a
fixed quantile (e.g. the level that the median of an independent PILOT pool of SP/FR runs reaches at B_pilot), set from dev data only;
(ii) fixed-budget quality estimand: fixed-budget gap-to-reference of best feasible f (censoring for infeasible) with rank-based/Wilcoxon
paired contrast instead of hitting time; (iii) ECDF-area (anytime) over a set of targets (COCO style) so no single target needs a window;
(iv) per-scenario budget. For the chosen design give: estimand formula; what is decided from dev data only and how; exact STOP rules that
cannot trivially pass (non-degeneracy guard); fresh seeds/scenarios and the disclosure that I61 dev data are pilot; power plan using only dev
data; the biggest threat to validity; CPU cost at 3.3-4.5 ms/PF on 10 cores (state ceiling); and a straight GO/NO-GO on whether this
is worth running at all given H56a was tiny (theta=+0.0205 mostly case14), i.e. what outcome would change the thesis claim.
Be strict about CLAUDE.md rules (no repeat-until-positive, one final successor, disclosure).
