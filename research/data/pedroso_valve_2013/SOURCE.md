# Valve-point economic dispatch data (archived input for ITERATION48)

- Source: J.P. Pedroso, M. Kubo, A. Viana, UCP_VALVE (2013), http://www.dcc.fc.up.pt/~jpp/code/valve/ (GPLv3, see COPYING),
  companion of arXiv:1404.4944 "Unit commitment with valve-point loading effect". Downloaded 2026-10-23.
- `ucp_data.py` (byte-for-byte, NOT executed; parsed as text) and the Gurobi logs `RESULTS/eld13-1800.txt`,
  `eld13-2520.txt`, `eld40-10500.txt` (certified optima: best objective = best bound, gap 0.0%).
- `valve_point_dispatch.json` is derived from `ucp_data.py` by text parsing (column order a, b, c, e, f; p_min, p_max)
  plus the certified optima from the logs: eld13@1800 = 17963.8287998, eld13@2520 = 24169.9169018,
  eld40@10500 = 121412.532719.
- Check: the published optimal vectors (3 decimals) evaluate to 17963.884 and 121412.572 with these data, i.e.
  equal up to the rounding of the published vectors.
- Known discrepancy: the literature has two 13-unit data sets (e.g. unit 3 e = 150 vs 200; see Li, Zhang, Lu,
  IEEE Access 2019, 10.1109/ACCESS.2019.2927574). We use Pedroso's set because its optimum is certified with the same data.
- Original systems: 13-unit (Wood & Wollenberg / Sinha et al. 2003), 40-unit (Chen & Chang 1995 via dos Santos Coelho & Mariani 2010).
