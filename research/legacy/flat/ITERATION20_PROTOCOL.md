# Iteracija 20 — lokalna Q osetljivost IEEE118 generatora BUS103 i BUS105

**Preregistracija 21. oktobar 2026, pre bilo kakvih NOVIH AC poziva iteracije 20.** `owlCoder/gadapt:main`, ne dirati upstream `bpzoran/gadapt`. Ovo je **deterministički mali elektroenergetski screening, bez GA/DE/random optimizacije i bez statističkih tvrdnji**.

## Šta je već dokazano

U [iteraciji 19](ITERATION19_REPORT_SR.md) izmereno je 10 originalnih IEEE118 AC proračuna: izvorni PG/VG i 9 starih I18 best-penalized, sva 10 nisu source-Q izvodljiva. Originalni aktivni gen **#46 BUS103** ima QG oko +75,422363582 MVAr naspram izvornog QMAX +40 (**+35,422364**), a **#48 BUS105** ima QG oko -18,334525252 naspram QMIN -8 (**-10,334525**) u svih 10. Ti generatori nisu među četiri PG/pet VG prethodno podešavanih resursa. Njihove originalne BUS sabirnice su PV (type2). Izvorni baseline ukupno Q prekoračenje je **78,0991950173 MVAr**, 6 Q-offenders, bez P/V/RATE_A prekoračenja. Ovi brojevi su iz već arhiviranog, zasebno proveravanog I19 JSON-a — NE iz novih proračuna.

## Zamrznuti eksperimentski redosled

Ne ponavljati izvornu baznu tačku (I19 stvarni AC #1); čitati je iz I19 raw JSON-a i preflight validirati originalni Q103/Q105, broj poziva=10 i identitet. Ne koristiti I16 AC-OPF dispečing kao besplatan optimizatorski initializer.

Neizmenjen originalni `pypower.case118()`: svih 118 bus / 54 online gen / 186 branch, originalni izvori PG/QG granica, P, Q, load, shunt, tap, RATE_A, generator gencost. Originalna slack BUS69. **Svih 54 PG ostaju izvorni i fiksni**, svih 54 VG su fiksni **osim dva**:
- gen originalni **red #46 / 0-based 45 / BUS103** sa originalnim VG=**1.01 p.u.**, izvorni BUS103 dopušta [0.94, 1.06], probati -0.02 i +0.02;
- gen originalni **red #48 / 0-based 47 / BUS105** sa originalnim VG=**0.965 p.u.**, BUS105 [0.94, 1.06], probati -0.02 i +0.02.

Redosled **tačno 8 novih stvarnih Newton–Raphson `runpf`**:
1. BUS103 -0.02 (BUS105 bez izmene), 2. BUS103 +0.02;
3. BUS105 -0.02 (BUS103 bez izmene), 4. BUS105 +0.02;
5. BUS103 -0.02 / BUS105 -0.02;
6. BUS103 -0.02 / BUS105 +0.02;
7. BUS103 +0.02 / BUS105 -0.02;
8. BUS103 +0.02 / BUS105 +0.02.

Solver identičan I18/I19: PYPOWER 5.1.19 `PF_ALG=1`, `PF_DC=0`, `ENFORCE_Q_LIMS=0`, `PF_TOL=1e-8`, `PF_MAX_IT=40`, `VERBOSE=0, OUT_ALL=0`. Q nije forced, *naknadno* se meri i ako van originalnog QMIN/QMAX kandidat nije fizički feasible. Svaki pokušaj se broji na granici stvarnog `runpf`, uključujući neuspeh ili izuzetak. Bez izmene algoritma GAdapt-a i bez trećeg izvora kontrole.

## Unapred određene izlazne metrike

Za svaki stvarno **konvergentan** AC: stvarni source `QG` / individualni `QMAX/QMIN` gen#46 i gen#48; njihove `Q excess` posebno, ukupni fizički Q excess MVAr svih 54 gen i broj Q-offendera; sve originalne sabirničke VMIN/VMAX (broj, sum p.u.), individualni PG/PMIN/PMAX, originalni source-positive RATE_A MVA oba kraja, i kompleksni AC KCL. Ekonomski cost samo kao `diagnostic_not_feasible_economic_opf`, nikako kao postignuti optimalan dispečing. Razlika ukupne Q povrede i dve pojedinačne razlike od I19 baseline (negativna znači poboljšanje), kao i da li su obe ključne generator granice zadovoljene. Ne zahtevati potpuno izvodljivo rešenje. Ako PF nije konvergentan, sve fizičke metrike null i izvorni error; ne prikazivati numerički nevalidan Q.

Hipoteza: izvorni VG na BUS103/105 treba da utiču na njihove Q injekcije. **Nije unapred sigurno** da će oba generatora postati Q-feasible istovremeno, da će druge Q povrede nestati, da će V ostati validni ili da je novi algoritam bolji. `RATE_A=0` nikada nije termički limit. Ne tvrditi o stvarnoj industriji: IEEE118 je javni testni model.

Maksimum 8 AC PF poziva, **0 AC-OPF** i **0 optimizer poziva**. Pre izvršavanja testovi da oba generatora postoje u izvornim redovima i oba modifikovana VG ostaju u izvornim V granicama, da se svi ostali PG/VG ne diraju, i da su I19 baseline i svih 8 jedinstvenih scenarija poznati. Pinovi Python3.12, PYPOWER5.1.19, SciPy1.13.1, pandas2.2.3, pandapower2.14.11, jednonitni BLAS. Posle CI sačuvati raw JSON/CSV i srpski izveštaj na main.

## Sledeći korak uslovljen ovim rezultatom

Ako se ta dva Q prekršaja smanje (ne mora biti potpuna izvodljivost), buduća naučna pretpostavka treba da cilja **izbor fizički korisnih reaktivnih kontrola**, a tek potom ograničenjima-svesnu adaptaciju *stvarnog GAdapt* operatora. Ako se ne smanje, pregledati originalni model Q raspodele i električnu topologiju; nikakva heuristička “inovacija” nije opravdana ovim screeningom.
