# Iteracija 36 — IEEE14 originalni AC transfer: kompletan negativan/neutralan test I34 operator-credit hipoteze

**Status: ZAVRŠENO 22.10.2026; izveštaj naknadno napisan IZ POSTOJEĆEG arhiviranog eksperimenta, bez novih AC poziva.** Zamrznuti [I36 protokol](ITERATION36_PROTOCOL.md) prethodio je svim I36 fizičkim AC izvršavanjima. Repozitorijum je isključivo `owlCoder/gadapt:main`; originalni `bpzoran/gadapt` nije menjan. I36 je druga originalna source elektroenergetska topologija u odnosu na I35 IEEE118, ali **IEEE14 je već korišćen u I17/I32 i nije slepi holdout**.

## Dokazi i poreklo

- Originalni uspešni [I36 GitHub Actions #39693907117](https://github.com/owlCoder/gadapt/actions/runs/39693907117): `preflight-no-real-ac` SUCCESS, zatim `source-ieee14-48-real-native-ac` SUCCESS (job `119546729567`).
- [Originalni artifact #12389128774](https://github.com/owlCoder/gadapt/actions/runs/39693907117/artifacts/12389128774), digest `sha256:acd37d3008dafe453ffbc6caee7bbb3d12d96984f9db8eddc9f5abba5d29f977`.
- [Sirovi JSON, svih 48 method×seed redova](results/ieee14_iteration36_12seed_4arm_8585_real_native_AC_20261022.json) i [CSV](results/ieee14_iteration36_12seed_4arm_8585_real_native_AC_20261022.csv), sa `audit_provenance` metapodacima o očuvanim izvornim `I36_TRUE_AC` linijama.
- Statistika u ovom izveštaju izračunata iz postojeće `summary` i `paired_seed_contrasts` strukture i ponovo proverena: 48 jedinstvenih ključeva, svaki red ima `actual_native_AC_calls == sum(actual_AC_per_scenario)`, svaki budžet ≤180, globalni zbir **8.585**.
- **Nijedan simulatorski poziv nije izvršen pri pisanju ovog izveštaja.** Originalni preflight testovi se ne broje kao stvarne AC evaluacije.

## Model i ograničenja zaključivanja

Stvarni `pypower.case14()`: 14 sabirnica, pet generatora, devet slobodnih kontrola (četiri nenulte slack-nezavisne PG + pet generatorskih VG), originalna source P/Q ograničenja generatora, sve izvorne VMIN/VMAX, pozitivni originalni RATE_A na oba kraja voda, kompleksna KCL provera. Tri ranije korišćene, **sintetičke** prostorne load konfiguracije: `nominal`, `odd_bus_plus1pct`, `even_bus_plus1pct`. Jedan pozitivan ishod znači stvarnu fizikalnu izvodljivost svih **tri proverene** konfiguracije, ne fizički dokaz izvodljivosti u drugim mrežnim stanjima, industrijski sertifikat niti globalni optimum.

Četiri originalna GA core režima dele isti first-failure `stop_fixed` evaluator, selekcioni fitness i najviše **180 stvarnih PYPOWER Newton–Raphson AC** evaluacija po run-u. Poređenje tako izoluje izbor/mutacioni reward mnogo bolje od ranijih `full`/ `stop` kontrasta. Dvanaest novih uparenih semena **2500–2511**, ukupno 48 runova (maksimum 8.640 stvarnih AC). Uspeh optimizatora `result.success` **nije** fizička izvodljivost; primarni kriterijum je bar jedan potpuno trostruko validiran source-feasible kandidat za seme.

## Rezultati svih unapred fiksiranih metoda

| Stvarni GAdapt core režim | Seme sa ≥1 source-feasible 3×AC kandidatom | Broj potpuno proverenih feasible kandidata* | STVARNI originalni AC | Najniži stvarno proveren mean source gencost | Medijana po uspešnom semenu** |
|---|---:|---:|---:|---:|---:|
| `legacy_fixed` | 12/12 | 452 | 2.143 | 8.441,323618 | 9.324,346214 |
| `ucb_objective_fixed` | 10/12 | 371 | 2.143 | 8.364,230583 | 8.751,065697 |
| `uniform_censor_safe_fixed` | 12/12 | 436 | 2.148 | 8.276,327323 | 8.909,52341 |
| `ucb_censor_safe_fixed` | 12/12 | 418 | 2.151 | 8.330,485513 | 8.879,225423 |

*Potpuno validirani kandidati unutar jedne evolucione putanje nisu nezavisne statističke replikacije. Jedinica inferencije je seme: **n=12 po arm-u**.

**Medijane su deskriptivne i uslovljene semenskim uspehom; posebno `ucb_objective_fixed` nema uspeh za sva semena. Razlika najboljeg minimuma nije preregistrovan dokaz superiornosti. U I36 novi UCB minimum **8.330,485513** jeste nominalno ispod legacy minimuma **8.441,323618**, ali **uniformna nova-credit kontrola** daje još niži minimum **8.276,327323**. Nema atribucije te razlike UCB učenju ili dokaza globalne optimalnosti.

## Preregistrovana egzaktna uparena poređenja, Holm(3)

| Kontrast (prvi : drugi) | Obe uspešne | Samo prvi | Samo drugi | Obe neuspešne | Egzaktno dvostrano p | Holm(3) p |
|---|---:|---:|---:|---:|---:|---:|
| `ucb_censor_safe_fixed` : `legacy_fixed` | 12 | 0 | 0 | 0 | 1 | 1 |
| `ucb_censor_safe_fixed` : `ucb_objective_fixed` | 10 | 2 | 0 | 0 | 0,5 | 1 |
| `ucb_censor_safe_fixed` : `uniform_censor_safe_fixed` | 12 | 0 | 0 | 0 | 1 | 1 |

**Primarni I36 rezultat: novi UCB 12/12 naspram originalnog legacy 12/12; nema nijednog diskordantnog para, exact p=1, Holm p=1.** To ne znači dokaz ekvivalencije, već odsustvo detektovane razlike u ovom ograničenom, gotovo plafonskom testu. Naspram objective-UCB 10/12 novi ima dva pozitivna diskordantna para, ali **egzaktno p=0,5, Holm=1**. U odnosu na uniform istog credit režima 12/12 : 12/12, p=1. Stoga nije dokazana prednost novog mutator-credit UCB postupka.

## Realni naplaćeni solver i mutacioni trag

| Metod | Odabiri operatora | Obrađeni feedback događaji | Pozitivne mutacione nagrade |
|---|---:|---:|---:|
| `ucb_objective_fixed` | 605 | 581 | 125 |
| `uniform_censor_safe_fixed` | 438 | 413 | 47 |
| `ucb_censor_safe_fixed` | 450 | 429 | 15 |

Svaki `actual_native_AC_calls` u sirovom JSON-u meri stvarni PYPOWER poziv, uključujući neuspešnu fizičku probu. Ukupno **6.946** preskočenih, NEIZMERENIH scenario-slotova ostaju `unobserved`; ne prepisuju im se feasible ili infeasible etikete. **Nula** kandidata sa `numerically_unknown` u sirovim podacima. Nagradni događaj nije uzročna mera efekta pojedinačne mutacije: offspring rezultat je konfaundiran selekcijom, crossoverom i evolutivnom putanjom.

## Značaj za doktorat i stop pravilo

[I34 na GÉANT](ITERATION34_REPORT_SR.md): novi UCB 12/12 prema legacy fixed 11/12, primarni exact p=1, sa hipotetičkim neizvornim cap-om i scenario-recourse kupovinom. [I35 na IEEE118](ITERATION35_REPORT_SR.md): 10/12 prema 10/12, primarni exact p=1, 8.587 stvarnih source AC. **I36 IEEE14: 12/12 prema 12/12, primarni exact p=1, 8.585 stvarnih source AC.** Ovo su odvojene studije na prethodno istraženim modelima; ne sabirati njihove seedove u jednu nezavisnu populaciju radi post-hoc povoljnog p.

**GO**: sačuvati validirani GAdapt core i reproducibilne inpute kao inženjerski rezultat; koristiti I34–I36 da definišemo šta metod *ne* pokazuje. **NO-GO**: dalje podešavati iste UCB reward težine samo na poznatim GÉANT/IEEE topologijama i tvrditi novu naučnu operator superiornost. Sledeći korak je verificiran literaturni audit plus do sada netestiran, izvorno zasnovan *joint robust* telekom ili drugodomenski zadatak. Mora se prvo fiksirati nezavisnost, izvorni dataset, model, strong baseline-ovi, hipoteze i budžet — pre novih stvarnih evaluacija.
