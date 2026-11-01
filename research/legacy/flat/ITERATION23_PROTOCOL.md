# Iteracija 23 — četvorotačkasti deterministički IEEE118 Q-bracket test između dva prethodna stvarna AC stanja

**Unapred registrovano 21.10.2026 pre svih novih originalnih IEEE118 AC proračuna ove iteracije.** Samo `owlCoder/gadapt:main`; nikada `bpzoran/gadapt`. Ova četiri unapred fiksirana AC pokušaja nisu GA, nisu algoritamska inovacija, nisu statističko poređenje. Javni `PYPOWER case118` model nije industrijska operativna mreža.

## Već stvarno plaćena fizička evidencija

U I19 source IEEE118 početni dispečing prekršio je originalne generatorske Q limite ukupno za 78,099195 MVAr; u I20 originalni BUS103 VG -0,02 doveo je do 32,345807697, a u I21 BUS32 VG +0,01 do 30,525900533. U I22 klasičnom centralnom diferencijom, prethodno arhiviranim realnim `runpf` pozivima iz I21, određena su **tri fiksna mali pozitivna delta-VG**:
- Originalni PV generator #16 BUS34, source VG 0,984, `delta34=0,004016033221868577`.
- Gen #43 BUS92, VG 0,99, `delta92=0,003533199035653122`.
- Gen #9 BUS19, VG 0,962, `delta19=0,004619105395208329`.

**Bez novih besplatnih PF baseline**: izveštaj i [raw I22](results/ieee118_iteration22_qmidpoint_5_real_ac_20261021.json) imaju:
- `all_three_half`, zajednički faktor α=0,5 za sva tri delta, source Q total **2,4644560480 MVAr**, **jedan QMIN** offender BUS92 (QG=-5,464456 vs QMIN=-3), nula P/V/RATE_A kršenja;
- `all_three_full`, α=1, source Q total **3,6428550961 MVAr**, **jedan QMIN** offender BUS36 (QG=-11,642855 vs QMIN=-8), nula P/V/RATE_A kršenja.
U oba izvornog originalnog BUS103 VG je fiksiran na **0,99 p.u.**, BUS32 na **0,973**. Sva **54 aktivna PG ostaju originalno fiksna**. Originalni izvorni slučaj ima 118 BUS, 54 GEN, 186 BRANCH, originalne individualne PG/QG, bus V, pozitivne RATE_A MVA na oba kraja i originalni polynomial gencost.

## Tačno četiri unapred definisana dodatna AC pokušaja

Za `alpha=0.6,0.7,0.8,0.9`, tim redosledom, za svaku od tri PV kontrole postaviti `VG_bus = VG_original_bus + alpha * delta_bus`, a BUS103 VG=0.99, BUS32 VG=0.973; sve ostale originalne generator VG i originalni PG svih 54 ostaju **neizmenjeni**. Svi koraci moraju zadovoljiti source VMIN/VMAX pre `runpf`.

**Tačno 4 stvarna originalna AC NR `pypower.runpf` (PYPOWER==5.1.19), PF_ALG=1, PF_DC=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=40, VERBOSE=0, OUT_ALL=0.** Brojati svaki ulaz u solver kao stvarni AC pokušaj i na exception. Izvršiti sve četiri fiksne α vrednosti, **čak i ako prvi postane feasible**; nema dodatnog bisection, tweaking, optimizatorskog random restart, niti naknadnog promovisanja povoljnih neuspešnih bodova.

Za svaki uspešno konvergiran `runpf`: originalni individualni QMIN/QMAX svih 54 aktivnih generatora i celokupni Q višak/nedostatak, originalni aktivni PG/PMIN/PMAX, originalni bus VMIN/VMAX, source-positive RATE_A MVA na oba kraja aktivnih grana, ponovo izračunati kompleksni AC nodalni KCL. Feasibility tolerancije iste I18–I22: P/Q 1e-3 MW/MVAr, V 1e-5 p.u., rated MVA 1e-3 MVA, KCL 1e-3 MVA; `RATE_A=0` nije ograničenje. Ako `success=False`/exception svi fizički izlazi su `null`. Uvek odvojiti `solver_converged` i `all_original_constraints_physically_feasible`. Originalna cena može se prikazati kao **ostvareni izvodljiv economic cost samo ako svi source limiti stvarno prođu**, inače je isključivo neizvodljiva dijagnostička komponenta.

Čak i ako se nađe provereno potpuno source-izvodljivo stanje, to je **jedna lokalna PV-kontrolisana AC-PF feasible tačka**, ne dokaz globalne AC-OPF optimalnosti, originalnog GAdapt mehanizma, superiornosti, statističke prednosti, realne industrijske implementacije ili matematički zajamčenog stanja celokupnog IEEE118 AC OPF prostora.

## Naučni rezultat i budžet

Ako postoji realizacija α u [0.6,0.9] sa bez-Q-kršenja, to pokazuje da izvodljivost u odabranom **uskom izvornom P-fixed VG subset-u** može postojati kroz domenski Q repair, dok prethodni nasumični 9D GAdapt/DE/random nisu pronašli ni jednu. Ako ne postoji, ne zaključivati neizvodljivost iz šireg prostora. **Maksimum i cilj četiri nova prava AC poziva, nula novih optimizer/AC-OPF poziva**.

Svi testovi i napomene reproducibilnosti: Python 3.12, pypower==5.1.19, scipy==1.13.1, pandas==2.2.3, pandapower==2.14.11, single-thread BLAS. Protocol, code, unit testovi, CI raw JSON/CSV i sve pozitivno/negativno u main, bez selektivnih rezultata.
