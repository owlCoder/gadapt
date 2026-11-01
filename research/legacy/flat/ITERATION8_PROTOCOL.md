# Iteracija 8 — eksploratorna reaktivno-naponska dijagnostika RTE1888

**Registrovano:** 2026-10-21, nakon iteracije 7, pre prvog AC izvršavanja ovog eksperimenta.
**Repozitorijum:** `owlCoder/gadapt:main`. Upstream `bpzoran/gadapt` ne menjati.
**Status:** pre-registracija DIJAGNOSTIKE, a ne potvrđujućeg algoritamskog poređenja.

## Polazna činjenica

Iteracija 7 je u izvorno ograničenoj formulaciji `RATE_A>0` pri 100% opterećenja
dobila nula početnih termičkih prekoračenja, ali 120 naponski povređenih sabirnica
i zbir naponskih kršenja 1.091786 p.u. u referentnom AC stanju.
Osam prvih generatora nije dalo izvodljivo rešenje u malom pilotskom budžetu
(0/15 metod-seme pokretanja). To ne dokazuje nemogućnost punog RTE AC-OPF.

## Hipoteza za ovaj screening (bez inferencijalnog testa)

Topološki bliske dodatne generatorske naponske zadate vrednosti mogu
promeniti naponski rezidual u drugačijem smeru od prvih osam setpointa.
Nepoznato je da li povoljna lokalna promena daje potpuno izvodljivo rešenje.

## Tačno fiksirana metoda pre izvršavanja

1. Javna konvertovana `pandapower.networks.case1888rte()` mreža; bez promena
   topologije, P-dispečinga, transformator tapova, šantova ili potrošnje.
   Samo opterećenje 100% u ovom screenu. Pinovati Python 3.12,
   `pandapower==2.14.11`, `scipy==1.13.1`, `pandas==2.2.3`,
   jednonitni BLAS/OMP i `PYTHONHASHSEED=0`.
2. Fiksni Newton-Raphson AC protokol iz iteracije 7:
   `runpp(init="dc", algorithm="nr", calculate_voltage_angles=True,
   numba=False, enforce_q_lims=True, max_iteration=40, tolerance_mva=1e-8)`.
   Brojati SVAKI stvarni poziv, i nekonvergentni.
3. Fizička provera ostaje `SourceRatedRTEGrid`: napon sabirnica i MVA
   na oba kraja svih pozitivno ocenjenih izvornih `RATE_A` grana;
   `RATE_A=0` nema izmišljenog termičkog limita.
   Granice generator Q prikazati zasebno, uključujući broj na granici i
   najveće eksplicitno prekoračenje, uz caveat da nisu svi mogući uslovi OPF
   provereni. Pozitivni rezultati ne dokazuju izvodljivost punog OPF.
4. Jedan referentni AC poziv sa originalnim setpointima svih 271 generatora.
   Na osnovu STVARNO izmerenih prekoračenja referentnih napona deterministički
   sortirati sabirnice opadajuće po magnitude prekoračenja, pa po indeksu.
   Napraviti neopterećen (unweighted) graf aktivnih AC vodova i transformatora.
   Za svaku sabirnicu sa prekoračenjem izabrati najbliži još neizabrani
   generator na aktivnoj sabirnici (BFS broj grana, tie-break ID generatora),
   izuzev prvih osam generatora koje je koristila iteracija 7.
   Izabrati NAJVIŠE osam novih generatora sa konačnim postojećim
   `min_q_mvar/max_q_mvar` i `max_q>=min_q`, čiji početni `vm_pu`
   leži u preseku `[0.95,1.08]` i naponskih granica priključne sabirnice.
   Ako ima manje od 8 legitimnih izbora, izvršiti samo dostupne.
   Ovaj izbor je namerno *data-dependent exploratory screening*, NE holdout.
5. Za svaki odabran generator napraviti dve nezavisne varijante
   `vm_pu +/- 0.02`, odsečene na presek prethodno definisanih granica.
   Sve ostale generatorske napone vratiti na referentne vrednosti
   za SVAKI pokušaj. Ukupni budžet = `1+2*k` stvarnih AC poziva
   (najviše 17), bez optimizacije. Nulta efektivna perturbacija se ipak
   beleži kao poziv i jasno označava.
6. Sačuvati po pozivu: ID generatora, ciljnu povređenu sabirnicu, BFS
   udaljenost, traženu i efektivnu perturbaciju, konvergenciju,
   naponska/termička kršenja i fizičku izvodljivost po postojećem
   source-rated kriterijumu; Q-limit counts, prekoračenja i naponski
   rezidual pre/posle. Neuspehe serijalizovati kao JSON `null` tamo gde
   nisu merljivi, ne kao izmišljene rezultate. Zabeležiti iskorišćeni budžet.
7. Graf i rezultati su samo za *konvertovanu* pandapower mrežu; ovaj
   eksperiment ne dokazuje električku bitovsku ekvivalenciju sa izvornim
   MATPOWER slučajem. Originalni izvor Q granica i 75 ranije
   identifikovanih impedansnih odstupanja zahtevaju odvojenu verifikaciju.
8. Pozivanje standardnog GAdapt-a, SLSQP-a, DE-a ili OPF solvera NIJE
   deo ovog dijagnostičkog eksperimenta. Pre svakog daljeg poređenja
   mora se doneti zaseban, unapred zamrznut protokol, sa nezavisnim
   fizičkim OPF solverom i punom proverom Q/slack/P ograničenja.
   Bez novih ili potvrđenih statističkih tvrdnji na osnovu ovog screena.

## Reprodukcija

```bash
python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration8_reactive_screen
python -m research.iteration8_reactive_screen --csv /tmp/i8_screen.csv --json /tmp/i8_screen.json
```

## Literatura

- MATPOWER, `case1888rte.m` (fiksni source branch rate iz iteracije 7)
- [MATPOWER data format](https://matpower.app/manual/matpower/DataFileFormat.html)
- [pandapower `runpp` dokumentacija — `enforce_q_lims`](https://pandapower.readthedocs.io/en/v2.14.11/powerflow/ac.html)
- Josz et al. (2016), *AC Power Flow Data in MATPOWER and QCQP Format*.
