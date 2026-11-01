# Iteracija 35 — direktna source IEEE118 AC validacija I34 operator-credit GAdapt-a

**Završeno 22.10.2026** na `owlCoder/gadapt:main`; [pre-registracija pre AC](ITERATION35_PROTOCOL.md), [uspešan GitHub Actions #39693170701](https://github.com/owlCoder/gadapt/actions/runs/39693170701), [svi 48 originalna source AC pokretanja](results/ieee118_iteration35_12seed_4arm_8587_real_native_AC_20261022.json), [CSV](results/ieee118_iteration35_12seed_4arm_8587_real_native_AC_20261022.csv). Originalni upstream `bpzoran/gadapt` nije menjan.

## Šta je zaista plaćeno i provereno

**4 režima pravog `gadapt.ga.GA` × 12 novih uparenih semena 2400–2411 × najviše 180 pravi originalni PYPOWER NR AC za svako pokretanje**. Stvarno izvršeno **8.587 / 8.640 genuine source IEEE118 AC solver poziva**, uključujući sve fizičke pokušaje. **0 numeričkih unknown**. Tačno **48/48** registrovanih `method×seed` redova arhivirano iz originalnog `I35_TRUE_AC` stdout (bez novih solver poziva pri arhiviranju). Ovo NISU GÉANT/Dijkstra simulacije.

`pypower.case118()` originalna mreža od 118 source sabirnica, 54 generatora; isti originalni 6D generatorski VG kontrolni prostor iz I30/I31, ista već korišćena **sintetička prostorna** PD/QD nominal/odd BUS×1,02/even ×0,98 / obrnuta tri opterećenja. Izvorne pojedinačne PG/QG, sve BUS VMIN/VMAX, izvorni pozitivni RATE_A oba kraja u MVA, kompleksni KCL proveravani za svaki zaista konvergentan solver rezultat. Nije širi puni slobodni AC-OPF niti nezavisna do sada neviđena mreža, niti stvarna pogonska elektroenergetska industrijska provera. Originalni trošak `gencost` daje se **samo za stvarno potvrđene sve tri** source izvodljive scene. Preskočene scene ostaju `unobserved`, bez fizičkog dokazivanja ili izmišljenih dobitaka.

## Zamrznuti GA načini imaju ISTI fiksni prvi-fail selekcioni fitness i isti fizički budžet

| Metod GAdapt-a | Seme sa ≥1 potvrđenim 3×AC source-feasible kandidatom (od 12) | Potpuno fizički verifikovani kandidati | Stvarni originalni AC | Najniži ostvareni potvrđeni originalni mean gencost |
|---|---:|---:|---:|---:|
| **Originalni `legacy_fixed`** | **10/12** | 413 | 2.145 | 131.195,790739 |
| `ucb_objective_fixed` (postojeći UCB) | **12/12** | **481** | 2.150 | **131.195,273865** |
| `uniform_censor_safe_fixed` (nova nagrada, uniform izbor) | 11/12 | 445 | 2.150 | **131.195,273865** |
| **`ucb_censor_safe_fixed` (novi I34 credit + UCB)** | **10/12** | 429 | 2.142 | **131.195,273865** |

Najniža potvrđena cena novog policyja je nešto niža od legacy minimuma, ali potpuno **identična postojećem objective-UCB i novom uniform modu**; nema dokaza da je izbor novog reward-a doprineo poboljšanju ili novom optimumu. **481/429/413** kandidata nije 481/429/413 nezavisnih statističkih realizacija — realna inferencijalna jedinica je seme, **n=12**. Medijane izvorne cene samo među semenski uspešnima: legacy 131.196,511855; novi UCB 131.197,030557 (nominalno lošiji) — neuspešna semena su izostavljena pa medijana nije bezuslovni algoritamski ranking.

## Tri unapred određena uparena testa, Holm(3)

| Kontrast | Obe uspešne | Samo novi UCB | Samo druga metoda | Obe neuspešne | Egzaktno 2-sided p | Holm(3) |
|---|---:|---:|---:|---:|---:|---:|
| **I34 new UCB : originalni legacy** (**PRIMARY**) | **10** | **0** | **0** | **2** | **1,0** | **1,0** |
| I34 new UCB : originalni objective-UCB | 10 | 0 | 2 | 0 | 0,5 | 1,0 |
| I34 new UCB : new uniform | 10 | 0 | 1 | 1 | 1,0 | 1,0 |

**Primarni originalni naučni test je negativan / neutralan: 10/12 potpuno identičan uspeh kao originalni legacy, egzaktno p=1. NEMA potvrđene prednosti novog cenzurno bezbednog operator-credit algoritma.** U ovom n=12 uzorku stari objective-UCB je čak pronašao 12/12 semena, ali prema novom UCB p=0,5 nije dovoljno za značajnu razliku. Sva tri primarna/sekundarna Holm p=1,0. To ne dokazuje ekvivalentnost metoda ni superiornost starog UCB-a.

Operator credit trag: `ucb_objective_fixed` 324 izbora operatora / 320 posmatranja /108 pozitivno nagrađenih; novi uniform 361/345/97; novi UCB 400/380/107. Ovi feedback podaci jesu registrovani, ali atribucija izvedena na nivou offspring-a nije izolovan kauzalni efekat mutacije. Originalni GA default nije promenjen.

## Originalni CI i naučni oprez

[Github Actions I35 #39693170701](https://github.com/owlCoder/gadapt/actions/runs/39693170701) prvo je prošao unit/preflight bez AC pa završio **48 realnih physics runova** uspešno. Originalni job `119544264140`. [Originalni JSON+CSV artifact id12389132886](https://github.com/owlCoder/gadapt/actions/runs/39693170701/artifacts/12389132886), SHA256 `a2129cdd2fc9245f5c2155535dfa8dd740cce9d48e02ccfddc50ee647ebb8cd5`. Kompletni raw JSON/CSV arhivirani u repozitorijumu bez ponovnog solver poziva; proveren jedinstven svih 48 ključeva, zbira pravih AC, potpunih izvornih cena i primarnih uparenih podataka.

**Značaj za disertaciju:** Direktna core implementacija I34 je stvarna inženjerska funkcionalnost, ali hipoteza o većoj uspešnosti na fizički složenom IEEE118 source modelu **nije potvrđena**. Ne podešavati credit težine nakon ovog negativnog poređenja. Sledeća I36 je **zasebno unapred zamrznuta IEEE14** (druga topologija od IEEE118, iako poznata iz I32), uz ista četiri GA operator mode-a i 12 novih uparenih semena 2500–2511. Sve rezultate otvoreno objaviti, bez predstavljanja modela kao operativno sertifikovane mreže ili originalnog naučnog pronalaska.
