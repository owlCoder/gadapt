**Verdict: FIX.** Read-only; nothing applied or written. All **71 tests passed** using an in-memory import overlay, but targeted checks found remaining defects.

- **B2 — FIXED:** The public weight cap and adaptive bounds prevent weight overflow and subsequent `inf * 0`.
- **B3 — FIXED:** The previous-average reproduction now returns **2.0**, correctly recognizing improvement to **1.6**.
- **I2 — ACCEPTED-AS-DOCUMENTED:** Clipping removes unsafe penalty statistics; rule-based failures retain the declared scalar endpoint `3.0`.
- **I4 — FIXED:** The executor assigns tracked-best values after the final-winner loop; reported feasibility, objective and variables agree.
- **M2 — ACCEPTED-AS-DOCUMENTED:** The revised design explicitly chooses fixed schedule constants.
- **Penalty key collapse — NOT FIXED:** Overflow keys discard the objective. At weight `1000`, `(0, 1e307)` and `(1e308, 1e307)` still receive identical keys despite distinct penalties. [Comparator](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:391)
- **Parent selection/immigration on scalars — NOT FIXED (documentation incomplete):** README acknowledges scalar parent selection, but omits immigration and still broadly claims exact “selection.” Qualify this as *survivor selection* and explicitly document scalar immigration.

Additional bugs:

- **Overflow fallback can reverse penalty ordering.** At weight `1000`, `(-1e308, 1e306)` has a smaller mathematical penalty than `(1e308, 9e305)`, but its key ranks worse. Intermediate multiplication overflow also misclassifies `(-1e308, 1e308)` at weight `2`, whose mathematical penalty is finite.
- **Initial scale can overflow.** Two initial objective magnitudes of `1e308` produce `f_ref=inf` through `statistics.median`; rule-based objectives `-1e308` and `1e308` then both scalarize to `1.5`, erasing diversity within the initial scale. [Scale calculation](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:357)