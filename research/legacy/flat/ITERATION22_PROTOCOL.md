# Iteracija 22 — mali prijavljeni IEEE118 feasibility-repair screen iz prethodnih Q/VG osetljivosti

**Preregistrovano 21.10.2026 pre ijedne NOVE stvarne AC evaluacije I22.** Samo `owlCoder/gadapt:main`, nikad `bpzoran/gadapt`. Metod je **klasična deterministička centralna konačna razlika i ekstrapolacija**, NE originalni GA mehanizam, bez optimizatora, niti garancija punog AC-OPF.

## Fiksirani istorijski izvori, nijedan besplatan AC

I19 originalni IEEE118 source baseline iz PYPOWER pokazao je 6 Q-offendera / ukupno 78,099195 MVAr. I20 izolovani izvorni gen BUS103 VG 1,01→0,99 (−0,02) **stvarno** je izmerio Qtotal=32,3458076968, bez P/V/RATE_A prekoračenja. I21 osam realnih AC `±0,01` proba na PV BUS34/BUS92/BUS19/BUS32, sa BUS103 VG 0,99, otkrilo je da samo **BUS32 VG 0,963→0,973** smanjuje Qtotal na **30,5259005332 MVAr**. Ta I21 `bus32_plus` tačka je nova **fiksna prethodno plaćena referenca**, NE izvršavati je ponovo niti dodavati kao I22 AC.

U toj referenci **tačno tri** originalna aktivna QMIN generatora krše source granicu:
- gen red16 (0-based 15), BUS34: izmereni QG = **−20,842226801510293**, source interval Q [-8,+24] MVAr.
- gen red43 (0-based 42), BUS92: QG = **−13,959900160493962**, source interval [-3,+9].
- gen red9 (0-based 8), BUS19: QG = **−14,723773571157601**, source interval [-8,+24].

Za svaku od tri kontrole već plaćena I21 merenja sa BUS32 na IZVORNOM VG daju:
- BUS34 `QG_minus=-91,87540228787019`, `QG_plus=+51,75999716278773`.
- BUS92 `QG_minus=-61,46361393293054`, `QG_plus=+34,5394698976348`.
- BUS19 `QG_minus=-62,932458617835664`, `QG_plus=+35,45790759779698`.

## Zamrznuta formula, bez manuelnog izbora koraka nakon rezultata

Sva tri originalna generatora su PV type2; izvorni originalni VG: BUS34 0,984, BUS92 0,99, BUS19 0,962; svaka source VMIN 0,94/Vmax1,06. Iz arhiviranog I21 JSON:
1. Centrirana lokalna osetljivost `s_i=(QG_i(VG_source+0.01)-QG_i(VG_source-0.01))/0.02` u MVAr/p.u. (primer: za BUS34 oko 7181,77 MVAr/p.u.). Izvori ± imali su fiksiran BUS32 na izvornom 0,963, a novi baseline ga ima na 0,973: stoga je linearna ekstrapolacija **aproksimacija, ne precizni univerzalni Jakobijan**.
2. Iz nove I21 `bus32_plus` reference čitati stvarni cilj `QG_i(base)`. Definisati čvrst cilj = **sredina originalnog individualnog intervala QMIN/QMAX** (BUS34 +8; BUS92 +3; BUS19 +8 MVAr).
3. Predloženi `delta_VG_i = clip((target_midpoint - QG_i(base))/s_i, 0, 0.008)` p.u. sa pozitivnim pre-registriranim ograničenjem povjerenja [0,0.008]. Ako slope nije pozitivan, nema dovoljno originalnog povjerenja; fail closed **pre svih simulacija**. Usporediti sa izvornom source VMIN/VMAX pre solvera, bez drugih promena.

**Tačno 5 pravih AC PF poziva** u unapred fiksiranom redosledu:
1. `bus34_predicted`: samo BUS34 delta_VG full prema fiksnom I21 `bus32_plus` baseline.
2. `bus92_predicted`: samo BUS92 delta_VG full.
3. `bus19_predicted`: samo BUS19 delta_VG full.
4. `all_three_half`: sva tri istovremeno po 0.5*delta_VG.
5. `all_three_full`: sva tri istovremeno po full delta_VG.

Svih 54 PG originalno fiksno, sve VG osim originalnog BUS103(0,99), BUS32(0,973) i eksplicitno izabrane tri korekcije ostaju originalno fiksne. Originalni IEEE118 bus/P/Q/V/RATE_A, load, shunt, tap i gencost netaknuti. **Samo** PYPOWER `runpf`, standardni NR `PF_DC=0,PF_TOL=1e-8,PF_MAX_IT=40,ENFORCE_Q_LIMS=0`, svim individualnim online originalnim PG/QG, svih VMIN/VMAX, originalnim pozitivnim RATE_A MVA na oba kraja i kompleksnim nodalnim KCL `<=1e-3 MVA` naknadno proveriti fizičku izvodljivost. Q se numerički ne nameće, već je obavezan uslov nakon AC. Izvorni trošak samo kao **ekonomska dijagnostika**, a kao ostvareni feasible kandidat samo ako SVA ograničenja zaista prolaze. Ne proglašavati globalnim AC-OPF optimumom.

Za svaki realni poziv upisati sve pojedinačne source offending BUS/generator Q identitete, P/V/thermal/KCL, original PG/VG, source Q total, source Q overflow, promenu u odnosu na prethodno izmerenih 30,5259005332 MVAr, izvornu originalnu ekonomsku cenu i `feasible` odvojeno od `solver_converged`. Svi numerički neuspešni AC rezidualli null sa solver error. Svaki **fizički** poziv se broji pre `runpf`, uključujući exception. Nema naknadnih dodatnih reakcija ili live prilagođavanja, nema uklanjanja nepovoljnih proba iz tabele.

Protokol, kod, unit testovi, CI, sirovi JSON i CSV, srpski izveštaj u repo. Python3.12, pypower==5.1.19, pandapower==2.14.11, scipy==1.13.1, pandas==2.2.3, single-thread BLAS/OMP. **Najviše 5 novih stvarnih AC PF, 0 GAdapt, 0 AC-OPF.**

## Važna naučna ograničenja

Ovo je tradicionalna inženjerska correction-prior/linearized feasibility-repair analiza. Korisnost zavisi od domenskih Q/VG kontrola; ne dokazuje algoritamsku novost, statističku superiornost, globalni optimum ili stvarnu industrijsku primenu na živom elektroenergetskom sistemu. Originalna puna IEEE118 AC-OPF referenca iz iteracije16 nije ista kao ovaj PV-PF gen PG-fixed podskup.
