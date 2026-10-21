# Iteracija 26 — prvi direktni opt-in scenario-feasibility operator-credit mehanizam unutar stvarnog GAdapt-a

**21.10.2026. Fork `owlCoder/gadapt:main`, upstream `bpzoran/gadapt` nepromenjen. Status: IMPLEMENTIRANO u core GAdapt-u, prošli testovi na Python 3.10 / 3.11 / 3.12.** Ovo je **istraživačka modifikacija** unutar stvarnog algoritma, ne samo infrastrukturna/elektroenergetska dijagnostika. **Nije dokazano da je naučno originalna ni statistički superiorna.**

## Problem koji rešava kod

Postojeći GAdapt fork je već imao `CreditBasedDecisionVariableMutator` sa `uniform/ucb` izborom i `objective/feasibility` reward, uključujući opcioni, stvarno fizički naplaćen `paired` reward. Zbog toga je nekorektno samu ideju UCB ili feasibility credit pripisivati našoj novini.

Na IEEE118, prethodni I24 test je pokazao izvodljive 100%-load tačke, ali I25 sa držanjem tih istih originalnih PV odluka pri sintetičkom load 98% / 102% izgubio je source Q izvodljivost u većini režima, posebno originalni BUS74. Ključno pitanje postalo je **kako adaptacija mutacionih operatora tretira fizičku izvodljivost kroz više različitih load-scenario evaluacija**.

## Tačno šta je promenjeno u source kodu

1. `gadapt/ga.py`: opcioni `mutation_operator_credit='scenario_feasibility'` sa obaveznim `mutation_scenario_count=N>=2`, stvarnim `mutation_evaluation_counter` i prethodno postojećim `mutation_violation_function(vector,score)`. `mutation_operator_policy='ucb'/'uniform'` mora biti aktivan. Novi način trenutno podržava samo `mutation_credit_assignment='offspring'`; nemoguće je lažno koristiti `paired` dok ne postoji dvostruki N-AC fizički budžet. Klasični `GA()` bez nove opt-in opcije je ostao **nepromenjen**.
2. `gadapt/ga_model/ga_options.py` i `gadapt/factory/ga_factory.py`: prenose N u stvarni mutator, bez novog wrapper optimizatora.
3. `gadapt/operations/mutation/decision_variable_mutation/credit_based_decision_variable_mutator.py`: **novi fiksni reward**. Samo čisto cached feedback N zasebnih fizikalno normalizovanih source constraint-violation vrednosti, nula samo kada su **svi** fizikalni limiti dotičnog scenarija zadovoljeni. Ako su sva N scenarija source-feasible `reward=0.75+0.25*bounded_objective_improvement`. Za delimičnu izvodljivost `reward=0.5*share_feasible_scenarios+0.125/(1+max_viol)+0.125/(1+mean_viol)`. Nisu dozvoljeni negativni, nonfinite, bool ili nedovoljno dugi signali. Callback `None` znači nedostajući fizički podatak i **nije nagrada**. Ovo su eksplicitno heurističke ablation težine, ne izvedena univerzalno optimalna politika. UCB politika izbora ostaje ista, kao i postojeća interpretacija uzročno konfaundiranog offspring credit.
4. `gadapt/operations/cost_finding/elitism_cost_finder.py`: pre i posle stvarnog objective poziva pročita **monoton real AC counter** i eksplicitno zahteva ili **N stvarnih source-scenario AC** ili **0** (post-budget sentinel). Delimični scenario batch `0<delta<N`, negativan skok, ili counter oštećenja su **fail-closed**. Samo celokupan N stvarno plaćenih solver poziva može davati operator credit. Nema izmišljene numerički ili fizički izvodljive jedinke posle hard budgeta.

## Unapred objavljen protokol, unit i integracija

[Preregistracija I26](ITERATION26_PROTOCOL.md) sačuvana je u commit-u `3f6b561aa3c370596b66567828fbf6afef8f968f` pre izmena. Implementirani [testovi](../tests/test_scenario_feasibility_credit.py) validiraju robust-all-zero strogo bolje nagrađen od skoro feasible, propagaciju stvarnih count==N iz `GA.execute`, isključivanje postbudget reward, odbijanje loše dužine/nan, i kompatibilnost default GA.

[Uspešan CI I26 #39662796544](https://github.com/owlCoder/gadapt/actions/runs/39662796544): Python **3.10, 3.11 i 3.12** sa unit i integralnim starim regression testovima `tests.test_operator_credit`, `tests.test_paired_operator_credit`, `tests.test_affine_cost_diversity`. Sintetičke unit simulacije nisu stvarni AC tokovi; ne prikazuju se kao stvarni elektroenergetski rezultati.

## Šta je ovde poznato iz literature

- Kalyanmoy Deb (2000), *An efficient constraint handling method for genetic algorithms*, DOI: https://doi.org/10.1016/S0045-7825(99)00389-8
- T. P. Runarsson & X. Yao (2000), *Stochastic Ranking for Constrained Evolutionary Optimization*, DOI: https://doi.org/10.1109/4235.873238
- DaCosta, Fialho, Schoenauer, Sebag, *Adaptive Operator Selection with Dynamic Multi-Armed Bandits*, GECCO (2008): https://gpbib.pmacs.upenn.edu/gecco2008/docs/p913.pdf
- Whitacre, Pham, Sarker (2009), *Credit Assignment in Adaptive Evolutionary Algorithms*: https://arxiv.org/abs/0907.0592
- *Constraint handling techniques for metaheuristics: a state-of-the-art review and new variants*, 2023: https://doi.org/10.1007/s11081-022-09782-9
- *Adaptive constraint handling technique selection for constrained multi-objective optimization*, 2024: https://doi.org/10.1016/j.swevo.2024.101488
- Ming et al. (2024), *Constrained Multi-Objective Optimization with Deep Reinforcement Learning Assisted Operator Selection*: https://arxiv.org/abs/2402.12381

**Novi opt-in credit je samo kandidat za konkretan inženjerski doprinos u fork-u**. Literatura već obuhvata AOS/bandit credit, feasibility rules, adaptivne constraint metode i reward prema fizikalnim ograničenjima. Potrebni su pun pregled literature, definisana razlika i nezavisna višedomena statistička demonstracija pre bilo kakvog naziva *originalan doktorski mehanizam*.

## Prvi fizički benchmark u narednoj I27

Pre novih native AC poziva zasebno je zamrznut [I27 protokol](ITERATION27_PROTOCOL.md), pa stvarno izvedeno 3.240 native AC na originalnom IEEE118 source modelu sa tri sintetička PD/QD load režima. Videti [I27 izveštaj](ITERATION27_REPORT_SR.md). Jedan scenario-feasible nalaz, makar pozitivan, nije dovoljan dokaz da je nova reward funkcija generalno bolja.
