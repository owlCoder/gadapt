## Iteracija 6 — IEEE118 i RTE: stvarni fizički rezultati, bez lažnog optimuma

**Završeno i reprodukovano na `main`:**
[Izveštaj na srpskom](ITERATION6_REPORT_SR.md) ·
[Unapred fiksiran protokol](ITERATION6_PROTOCOL.md) ·
[Pravi IEEE118 benchmark](ieee118_allocation.py) ·
[Odvojeni RTE stres-test](iteration6_rte_stress.py).

IEEE118 (osam generatorskih napona, dva faktora opterećenja,
šest novih semena × šest metoda × 180 stvarnih AC evaluacija = **72 pokretanja**):
standardni samostalni SLSQP ostaje najbolji po medijalnim izvodljivim
gubicima (131,553953 MW na 100%, 172,554719 MW na 110%).
Fiksni i eksperimentalni adaptivni GAdapt→SLSQP daju samo mešovite
rezultate. Ni jedna primarna razlika nije statistički potvrđena posle
Holm korekcije (n=6). Nema dokaza da je unapred zamrznuti
adaptivni kontroler bolji od fiksnog hibrida.
[Verifikovan IEEE118 CI](https://github.com/owlCoder/gadapt/actions/runs/39582074680).

Francuski RTE1888, 12 metod–seme slučajeva × 72 stvarna NR poziva:
**0/12 fizički izvodljivih rešenja** u modelu koji menja samo osam napona;
prijavljeno je minimalno kršenje mrežnih ograničenja, a ne
nepostojeći optimum izvodljivih gubitaka.
[Verifikovan RTE1888 CI](https://github.com/owlCoder/gadapt/actions/runs/39582153291).

Sirovi CSV: `results/ieee118_allocation_20261021.csv` (72 reda),
`results/rte1888_stress_20261021.csv` (12 redova).
[Nezavisno uspešno ponovno analiziranje i SVG/PNG grafikoni](https://github.com/owlCoder/gadapt/actions/runs/39583243300)
validira broj pravih poziva, svih šest metoda, 12 RTE redova i
ne imputira izvodljive MW rezultate kada fizičke granice nisu zadovoljene.
Svi detalji u [ITERATION6_REPORT_SR.md](ITERATION6_REPORT_SR.md).
**Kontroler je eksperimentalni research modul, ne promena GAdapt podrazumevane metode.**

---

## Iteracija 5: provera najboljeg ostvarenog rešenja, ne dokaz globalnog optimuma

Pregled **izvršenih eksperimenata, 360 objektivnih AC evaluacija po metodi,
12 novih uparenih semena i CMA-ES baseline-a**:
[ITERATION5_REPORT_SR.md](ITERATION5_REPORT_SR.md).
Prethodno fiksiran protokol: [ITERATION5_PROTOCOL.md](ITERATION5_PROTOCOL.md).

Na javnom IEEE14 AC referentnom sistemu potvrđena su rešenja sa gubicima
13.497263522715254 MW (100% opterećenje) i 16.791946841097882 MW
(110% opterećenje). Obe vrednosti dobijene su jednom visoko-budžetnom
pretragom i ponovo proverene nezavisnim AC solve-om. **To nisu
matematički sertifikovani globalni optimumi**, a IEEE14 nije industrijski
operativni uzorak. Na jednakih 360 AC evaluacija SLSQP i CMA-ES
pokazali su preciznost znatno bolju od originalnog GAdapt-a na ovoj
konkretnoj niskodimenzionalnoj formulaciji. Sama hibridizacija nije
originalan naučni rezultat.

Reprodukcija iz `owlCoder/gadapt:main`:

```bash
python -m pip install -e . 'scipy>=1.11,<1.16' 'pypower>=5.1,<6' 'networkx>=3.2,<4' 'cma>=4,<5'
python -m research.ieee14_local_refinement --seeds 12 --seed-start 100 --budget 360 --output ieee14_local_refinement.csv
python -m research.ieee14_cma_es --seeds 12 --seed-start 100 --budget 360 --output ieee14_cma_es.csv
python -m research.ieee14_best_known_reference --budget 3600 --de-stage 2000 --output ieee14_best_known_reference.csv
python -m research.geant_local_refinement --seeds 8 --seed-start 100 --budget 360 --output geant_local_refinement.csv
python -m research.analyze_geant_local_refinement geant_local_refinement.csv
python -m research.analyze_ieee14_six_method_pilot
```

Uključene su trajno verzionisane sirove numeričke tablice
`research/results/ieee14_local_refinement_20261021.csv`,
`research/results/ieee14_cma_es_20261021.csv`,
`research/results/ieee14_reference_3600_20261021.csv`,
`research/results/geant_local_refinement_20261021.csv`,
SVG grafikoni u `research/figures/` i svi izlazi GitHub Actions.
Zapisi `True/False` očuvani su u Python CSV formatu radi
reproduktivne statistike. Vremenski GÉANT blok je ranije pregledan;
**nije nezavisan holdout**. Kodovi SLSQP/CMA-ES predstavljaju postojeće
referentne metode, ne korisnikov originalni doktorski algoritam.

---

## Paired physical mutation-credit experiment — current `main`

`mutation_credit_assignment="paired"` is a STRICT opt-in research setting
for full GAdapt. Unlike ordinary adaptive mutation, it evaluates the same
offspring once BEFORE a one-variable mutation and once AFTER. **Both solver
calls consume the optimization budget.** This is a local effect comparison,
not a proof of improved final optimization or a new AOS theorem. The callback
must report a monotonically increasing number of genuine physical evaluations;
post-budget sentinel objective calls must NOT advance that counter.

```python
ga = GA(
    cost_function=physical_objective,
    mutation_operator_policy="ucb",  # or "uniform"
    mutation_operator_credit="objective",  # or "feasibility"
    mutation_credit_assignment="paired",
    mutation_evaluation_counter=lambda: actual_simulator_calls,
    ensure_unique_individuals=False,
    number_of_mutation_decision_variables=1,
    candidate_solution_mutation="random",
)
# For feasibility mode, also set mutation_violation_function to a
# cached metadata reader returning >=0 normalized physical violation,
# and None if that particular physical evaluation never occurred.
```

Regenerate raw CSV and paired tests on *both* public infrastructure models:

```bash
python -m research.paired_credit_ieee14 --runs 8 --budget 240 --output paired_ieee14.csv
python -m research.analyze_paired_credit_ieee14 paired_ieee14.csv
python -m research.paired_credit_geant --runs 8 --budget 240 --output paired_geant.csv
python -m research.analyze_paired_credit_geant paired_geant.csv
```

The older GÉANT August block is **reused** (not a new independent holdout).
Full protocol: [PAIRED_CREDIT_PROTOCOL.md](PAIRED_CREDIT_PROTOCOL.md).
No method may be asserted scientifically superior on 8 seeds. Failures and
different counts of unscored objective wrapper requests remain reported.

---

## Experimental mutation-benefit AOS (branch `research/feasibility-credit-aos`)

**Do not interpret this as a dissertation-ready method.** The original
`GA()` behavior is unchanged; AOS is opt-in:

```python
from gadapt.ga import GA
ga = GA(cost_function=my_cost,
        mutation_operator_policy="ucb",
        mutation_operator_credit="objective")
# Add variables as usual, then ga.execute().
```

For physical feasibility credit, set `mutation_operator_credit="feasibility"`
and provide `mutation_violation_function=lambda values, penalized_cost: ...`.
This callback must return a finite nonnegative *normalized* violation (zero
if physically feasible), or `None` when an objective request did not receive
an actual physical evaluation because the hard budget expired. For rigorous
budget accounting, the callback should only read an evaluation cache; any
new simulations inside it must be separately counted. This API is research-only
and does not replace domain verification, nor provide a general hard-constraint
solver.

Replicate on the actual package:

```bash
python -m pip install -e . 'scipy>=1.11,<1.16' 'pypower>=5.1,<6' 'networkx>=3.2,<4'
python -m unittest discover -s tests -v
python research/aos_ieee14_pilot.py --runs 8 --budget 240 --output aos_ieee14_pilot.csv
python research/analyze_aos_ieee14.py aos_ieee14_pilot.csv
python -m research.aos_geant_temporal --runs 8 --budget 240 --output aos_geant_temporal.csv
python -m research.analyze_aos_geant_temporal aos_geant_temporal.csv
python research/plot_aos.py --kind ieee14 --csv aos_ieee14_pilot.csv --prefix aos_ieee14_figure
python research/plot_aos.py --kind geant --csv aos_geant_temporal.csv --prefix aos_geant_figure
```

- [AOS protocol: scientific prior art and frozen chronological timestamps](AOS_ITERATION_PROTOCOL.md)
- [AOS iteration report: numeric evidence, failures, limitations](AOS_ITERATION_REPORT.md)
- [Original dissertation protocol](DISSERTATION_PROTOCOL.md)

The IEEE14 case is a public AC reference model; GÉANT is archival
anonymized/scaled data with an assumed module planning model, not live
infrastructure. Archive SHA, software dependencies, true evaluations, extra
calls, failures and selection telemetry are captured in GitHub Actions.

---

# Research: robust cost-diversity baseline

This branch contains a deliberately **opt-in** change to GAdapt:

```python
from gadapt.ga import GA

ga = GA(cost_function=my_cost_function, cost_diversity_metric="affine_invariant")
```

The default remains `log_relative`. The new `affine_invariant` metric:

* calculates the half-range of **finite** population costs;
* compares it to the initial generation's half-range and clamps to [0,1];
* is invariant to addition of a constant and multiplication by a positive
  constant, modulo floating-point representability;
* returns 0 when all costs are identical; if the initial spread is zero,
  it recovers to 1 when nonzero diversity subsequently appears;
* raises a `ValueError` for nonfinite costs in the diversity calculation.

**Limitation:** Invariance of a metric is not a proof of better optimizer
accuracy. The range is sensitive to outliers; a zero initial range loses
relative magnitude information. Whether this is an improvement for any
class of objective functions must be measured in full GAdapt runs.

## Reproduce

Run tests from the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run exploratory seeded benchmarks on the full package:

```bash
python research/benchmark_affine.py --runs 30 --generations 150 --output affine_results.csv
```

For a defensible dissertation, the next experiments must compare the
unchanged baseline, the opt-in metric, and independent optimizers under
controlled objective-evaluation budgets across multiple dimensions,
replicates, transformations, noise levels and constraint scenarios.
Statistical inference must use paired seeds and multiplicity corrections.
Do not compare results of differently scaled cost values without undoing
the affine transform. Use engineering cases with independently verified
feasibility before making infrastructure or industrial claims.

## Repositories / provenance

Based on owlCoder/gadapt fork of bpzoran/gadapt at
`8825da180377cb231d4751c08108a8149269ffc1` (2026-10-17).
The upstream repository is not modified by this research branch.
