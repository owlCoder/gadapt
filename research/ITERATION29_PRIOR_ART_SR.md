# Iteracija 29 — literatura i formalna granica novosti: rano odbacivanje neizvodljivih scenarija već postoji

**Datum:** 21.10.2026. **Status:** kritički pregled odabranih izvora, NE potpun sistematski/PRISMA pregled, NIJE tvrdnja o originalnoj doktorskoj teoriji. [I29 protokol](ITERATION29_PROTOCOL.md) pripremljen je pre novih AC izračunavanja i osnovni testovi proveravaju stvarni `runpf` budget.

## Relevantna prior art literatura

- **Sankary et al. (2018)**, *Stochastic Scenario Evaluation in Evolutionary Algorithms Used for Robust Scenario-Based Optimization*, *Water Resources Research*, [doi:10.1002/2017WR022068](https://doi.org/10.1002/2017WR022068). Jasno eksplicitno opisuje činjenicu da evaluacija kandidata preko mnogo scenarija povećava simulacioni trošak, i da stohastički izbor manjeg skupa scenarija može smanjiti number-of-evaluations u evolutionary optimizaciji. **Sam evaluator koji proverava manje režima nije nov**.
- **Complexity Is an Effective Observable to Tune Early Stopping in Scenario Optimization**, *IEEE Transactions on Automatic Control*, 2023, [IEEE dokument 9721591](https://ieeexplore.ieee.org/document/9721591/), doi:10.1109/TAC.2022.3153888. Teorijska early stopping politika u drugačijem scenario optimization okviru; naša implementacija NEMA njenu teoremu o riziku niti predvidivo generalizuje na neviđenu neizvesnost.
- **Multi-objective constrained black-box optimization using radial basis function surrogates** (2016), [doi:10.1016/j.jocs.2016.05.013](https://doi.org/10.1016/j.jocs.2016.05.013). Surogati za skupu fizikalnu evaluaciju i constraint-feasibility već postoje; naš tehnički evaluator nema naučno originalan surrogate model.
- **M-Race: A Racing Algorithm for the Tuning of Meta-Heuristics Based on Multiple Performance Objectives** (2025), [MDPI Applied Sciences 15(14) 7658](https://www.mdpi.com/2076-3417/15/14/7658). Racing može uklanjati loše konfiguracije na osnovu merenja; naš rani prekid je još jednostavnija forma fizikalno dokazivog *AND* screening-a i nije ekvivalent teorijski validiranom statistical race.
- **Adaptive Ranking-Based Constraint Handling for Explicitly Constrained Black-Box Optimization**, *Evolutionary Computation* 30(4) (2022), [MIT Press](https://direct.mit.edu/evco/article/30/4/503/110409/Adaptive-Ranking-Based-Constraint-Handling-for). Obrada poznatih eksplicitnih ograničenja sa malim evaluacionim troškom je prethodni poznati domen; izvorni AC simulator constraints su skuplji i implicitni.
- **Learned Surrogates for AC Feasibility in Stochastic Unit Commitment: A Comparative Study With Conformal Guarantees** (2026), [doi:10.1049/gtd2.70345](https://doi.org/10.1049/gtd2.70345). Feasibility screening naučno traži merenje pogrešne feasible klasifikacije i kalibraciju; naš klasični evaluator NEMA validirane conformal/robust uncertainty garancije.
- Dodatno [I28 bibliografska matrica](ITERATION28_LITERATURE_NOVELTY_AUDIT_SR.md): UCB/AOS credit, constraint handling i robust AC OPF, uključujući vrlo relevantnu 2026 feasibility-guided operator selection, već su široko zastupljeni. Izmena operatora sa novom reward skalom bez dodatne teorije i testova ne daje automatski doktorsku novinu.

## Strogo ograničeno ono što naš opt-in source kod ZAISTA garantuje

Imamo tačno tri zadana load režima i tvrdnju `robust_feasible(x)=AND(feasible_0.98(x), feasible_1.00(x), feasible_1.02(x))`. Ako je jedan **konvergiran i originalnim izvorim Q/P/V/positive RATE_A/KCL proverama utvrđeno neizvodljiv**, `AND` je lažna za TAJ KONKRETAN izmereni vektor i za OVA TRI fiksna režima, pa su preostali AC za tog kandidata nepotrebni da bi se odbacila robust izvodljivost. Time se ne zna vrednost drugih scenarijskih prekoračenja ni puna srednja originalna cena; **ne smemo izmišljati penalizovani objective za preskočene AC**. Kod vraća `censored heuristic score` radi rangiranja, eksplicitno ne kao true three-AC fitness.

Ako fizički poziv `runpf` ne konvergira, to je numerički neuspeh, **NE dokaz fizičke neizvodljivosti**. Ako tri scenarija konvergiraju i SVA source ograničenja stvarno prolaze, onda je kandidat u ova tri fiksna numerička modela verifikovano feasible, ali nije ni puni AC-OPF optimum ni garantovano robustan na bilo kakav drugi load/fault.

Kod `stop_adaptive` ne predviđa scenario iz ničega: poređa sledeći scenario samo prema fiksnim posterior frekvencijama merenih failure-ova `(1+observed_source_constraint_fails)/(2+actually_executed_AC)` po scenariju. NIKADA ne uči iz preskočenih AC, jer nema njihove vrednosti. Potrebno je kontrolno poređenje sa fiksnim teškim scenarijem prvim; u tri veštačka load režima `0.98` je unapred poznat posebno težak zbog generatorskog BUS74 Q limita i adaptivni redosled stoga može doneti malo ili ništa novo.

**Ovo je inženjerski doprinos auditabilnom softveru i fer evaluaciji**, ne tvrdi se matematička algoritamska originalnost. Eventualni stvarni doktorski doprinos treba zasebnu, literaturom i više domena validiranu tezu (npr. AC cost model sa utvrđivanjem minimalnog konfidencijskog učinka), ali ne sme se predstavljati kao završen pre istraživanja.

## Obavezni kriterijumi analize nakon I29

1. Ušteda i broj obrađenih *fitness* vektora pri istom maksimumu stvarnih AC, **ne** isto što i bolja source robust-feasible stopa.
2. Pronađene potpuno source-izvodljive odluke moraju zaista imati sva tri plaćena true AC, ne ograničiti se na parcialne diagnostičke Q.
3. „Najbolja cena“ sme se porediti samo među tako source-feasible kandidatima. Censored `1e9` surrogate je kontra originalnom `mean cost + penalty` i može pogoršati EA search landscape.
4. Mali I29 pilot ima 4 seedova na prethodno fizikalno kalibrisanoj IEEE118 javnoj mreži; čak i statistički bolji mean ne dokazuje originalnost ili transfer na stvarni telekom/industriju.
