**Verdict: the numerical results reproduce, and H56a is appropriately qualified, but several interpretations need revision.** I independently recomputed from raw records using `.venv/bin/python -I`; no files were changed.

| Contrast | Estimate | 95% percentile interval | p | Holm p |
|---|---:|---|---:|---:|
| H56a | +0.0205185 | [0.0019646, 0.0395899] | .0300 | — |
| H56b | +0.0014694 | [−0.0130714, 0.0160306] | .8498 | 1 |
| AP−SP interaction | +0.0092981 | [−0.0129566, 0.0313436] | .4019 | 1 |
| EC−SP interaction | +0.0029593 | [−0.0188336, 0.0247816] | .7894 | 1 |
| H56a using FX-M | −0.0070444 | [−0.0254355, 0.0107890] | .4617 | 1 |
| SP−SP-T encoding | +0.0034722 | [−0.0103172, 0.0164472] | .6040 | 1 |

Mean d for case14 at R = 9/17/33 is **0.033325 / 0.0916917 / 0.059650**; all six remaining blocks equal zero. Medians match the report. Removing case14/R17 and averaging the remaining eight blocks gives **0.0116219 [−0.0045178, 0.0285836]**, correctly labelled descriptive.

I recomputed attainment for all 16 arms and nine blocks. Selected counts below are ordered R = 9/17/33:

| Arm | case14, denominator 40/block | case57, denominator 20/block |
|---|---|---|
| FR/AD-N | 3 / 16 / 20 | 0 / 0 / 0 |
| FR/FX-T | 3 / 34 / 20 | 0 / 0 / 0 |
| SP/AD-N | 4 / 17 / 15 | 0 / 0 / 0 |
| SP/FX-T | 2 / 23 / 21 | 0 / 0 / 0 |
| EC/AD-N | 0 / 37 / 36 | 2 / 1 / 1 |

Every case118 arm has zero attainment. EC/AD-N mean T reproduces **0.281042/0.391917** on case14/R17/R33 and **0.951133/0.971933/0.991300** on case57. EC’s pooled attainment range is exactly **0.20–0.26**. Figures agree with these data and distinguish descriptive summaries from protocol inference.

Concrete fixes to [the report](/Users/danijel/Desktop/gadapt/research/ITERATION56_REPORT_SR.md):

- **§5 and conclusion 2 overclaim mechanism exclusion.** Replace with: “H56b i kontrast SP–SP-T nisu statistički podržani. Ovi rezultati ne dokazuju odsustvo efekta niti isključuju mehanizam preko vrednosti troška; relativna verovatnoća drugih mehanizama nije utvrđena.” Also change “nijedna sekundarna procena nije različita od nule” to “nijedan sekundarni kontrast nije statistički značajan posle Holm korekcije.”

- **§6’s EC exclusivity claim is false.** Use: “Uz EC, cilj na case57 povremeno dostižu i SP/FX-M pri R=9 (1/20) i SP-T/AD-N pri R=17 (1/20).” Restrict “višestruko skraćuje vreme” to the cited case14/R17–R33 descriptive comparisons; EC is not uniformly fastest across blocks.

- **§4 and conclusion 1 generalize missing information too broadly.** Replace “studija nema informaciju” with “primarni FR–SP kontrast nema varijabilnost u ovih šest blokova pri ovom budžetu.” Their zero contributions remain part of the nine-block estimand.

- **Add the protocol-required negative gaps:** “U 24 test-pokretanja najbolji izvodljiv gubitak bio je ispod L*; najveće poboljšanje iznosilo je 0,3111 MW (2,894%).”

- **§6 feasibility wording implies equivalence.** Use: “Objedinjeni udeli nalaženja izvodljivog rešenja bili su 0,467–0,507; sličnost ovih udela ne dokazuje ekvivalentnost.”

The positive-sign explanation and tuned-fixed-policy advantage are already explicit and correct; use exact SP attainment **57.5% versus 42.5%**. Retain the existing power caveat: the four degenerate rehearsal blocks indeed inject **0.02222** without variability. Add that inference is conditional on frozen references, calibration constants and scenarios.