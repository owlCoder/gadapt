# I34 — direktna izmena GAdapt core: cenzurom i stvarnim troškom zaštićen mutacioni kredit (22.10.2026)

**Implementirano na `owlCoder/gadapt:main`** nakon unapred sačuvanog [I34 protokola](ITERATION34_PROTOCOL.md). Ovo je RESEARCH-ONLY opt-in mehanizam; ni originalni `GA()` niti upstream `bpzoran/gadapt` nisu menjani po podrazumevanom ponašanju.

## Izmenjeni stvarni GA moduli

1. [`gadapt/ga.py`](../gadapt/ga.py): dozvoljen `mutation_operator_credit="censored_verified_per_cost"` samo uz aktivnu `ucb` ili `uniform` politiku, `mutation_scenario_count=N>=2`, obavezan monotoni `mutation_evaluation_counter`, čisti `mutation_violation_function` callback i `offspring` atribut. Nelegalne opcije daju `ValueError`.
2. [`gadapt/operations/cost_finding/elitism_cost_finder.py`](../gadapt/operations/cost_finding/elitism_cost_finder.py): meri **stvaran counter delta** pre i posle pravog `cost_function`. Novi modalitet dozvoljava `0..N` izvršenih simulacija i taj broj prosleđuje controller-u. Nulta / postbudget cena ne može dobiti reward i uopšte ne poziva callback. Delta negativna ili veća od N je greška. Stari `scenario_feasibility` ostaje **strogo 0 ili N** kao ranije.
3. [`CreditBasedDecisionVariableMutator`](../gadapt/operations/mutation/decision_variable_mutation/credit_based_decision_variable_mutator.py): callback sme da vrati SAMO `status, actual_calls, observed_scenarios, observed_violations` — sve mereno. Proveravaju se tačan broj originalnih poziva, jedinstvene oznake, finitne nenegativne fizikalne povrede i međusobna konzistentnost:
   - `verified_feasible` samo za svih N pozvanih scenarija, sve povrede = 0: reward `1/N`;
   - `measured_infeasible` za stvarno izmerenu bar jednu pozitivnu povredu, reward **0**, čak i ako je kandidat odbijen jeftino nakon prvog scenarija;
   - `numerically_unknown` i `None`: feedback se zadržava kao **nepoznat**, bez reward/observation; nepotpun kandidat nikada se ne proglašava robusno izvodljivim.
   - score `1e9+` za cenzurisani fitness nikada nije prikazan kao originalna ekonomska cena za učenje.
   - operator-level reward i dalje nije kauzalni efekat pojedinačne mutacije jer reprodukcija/crossover doprinose offspring-u; ovaj nedostatak nije rešen.
4. [`research/iteration34_censor_credit_geant.py`](iteration34_censor_credit_geant.py): strogo last-evaluation observation cache služi samo da izveštaj posle upravo izvršenog `cost_function` ne napravi još jedan pravi routing. Koristi već postojeći [I33 originalni GÉANT simulator](iteration33_geant_routing_budget.py). Jedna kandidat scena = jedna stvarna Dijkstra+module-price evaluacija, nije AC.
5. [Core sintetički testovi](../tests/test_censored_verified_per_cost_credit.py) i [adapter sintetički testovi](test_iteration34_censor_credit_geant.py): strict 1/2/3 counter, nulta nagrada za rano potvrdjen fail, missing/unknown withheld, brojanje bez recikliranja stare memorije, fail-closed callback greške, legacy regresija i execution kroz *pravi* GAdapt GA.

## Konceptualna granica

`1/N` reward za verifikovani robust success jeste jasno definisan i normalizovan po ceni, ali svaki uspešni `N`-scenario kandidat ima isti N; stoga iz ovog oblika **ne nastaje automatski netrivijalno optimalno raspoređivanje različitih skupih resursa**. Motivacija je **prevencija pogrešne operator-credit atribucije** u uslovima cenzurisane fitness ocene, a ne dokazan novi optimizacioni princip. Poznate bandit, cost-sensitive bandit, feasibility-based credit i scenario-racing metode postoje; ideja se mora proveriti protiv originalne literature pre bilo kakvog naučnog „novum-a“.

## Testovi i sprovođenje

Originalni [I34 workflow](https://github.com/owlCoder/gadapt/actions/workflows/research-iteration34-censored-credit.yml) pre I34 solver run zahteva Python 3.11 sa pinned paketima i SVIM starim i novim regressions. **Prvi CI preflight** [#39691771826](https://github.com/owlCoder/gadapt/actions/runs/39691771826) je našao jednu isključivo sintaksičku grešku u I34 benchmark reporteru PRE ikakvog realnog GÉANT routinga. Ispravljena na `main` bez promene protokola/metoda/semena/cap-a. **Drugi CI** [#39691941881](https://github.com/owlCoder/gadapt/actions/runs/39691941881) je uspešno prošao sve preflight testove pa prešao na prvo preregistrovano fizičko-domensko izvršavanje. Po završetku tog rada pravi rezultati i status pripadaju posebnom [I34 rezultatskom izveštaju](ITERATION34_REPORT_SR.md).

**Nema smisla tvrditi da je mehanizam naučno bolji dok se ne vidi pun I34 rezultat**, niti izvodljivost GÉANT pod našim hipotetičkim cenovnim cap-om predstavljati kao industrijski/operativno potvrđen QoS.
