# Brief for Codex #4 — adversarial check of the I53 part A interpretation (read-only)

Read research/ITERATION53_REPORT_SR.md §1 (Serbian), the raw data research/results/iteration53/synthetic.json,
the protocol research/ITERATION53_PROTOCOL.md §2A and the code research/iteration53_oracle_step.py.

Check, using the raw per-seed data (you may run read-only Python with numpy to recompute):
1. Are the reported medians, verdicts A1/A2 and Holm p-values correct?
2. Is the interpretation justified: "step control explains most of the gap only on the isotropic problem; on the
   rotated ellipsoid no mutation intervention matters; the main remaining cause is coordinate-wise operation without
   correlation learning"? Name alternative explanations the data cannot exclude (e.g. CMA-ES also not converged at
   3000 evals on the rotated ellipsoid; blending crossover being coordinate-wise; oracle isotropy on a diagonal
   ellipsoid; the odd DN >> DR result on the diagonal ellipsoid — explain it if you can from the code).
3. Anything stated as preregistered that is actually post hoc.
Max ~500 words, numbered, most important first. Read-only: do not edit files.
