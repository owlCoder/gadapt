# Iteracija 14 — prvi direktni originalni MATPOWER AC-OPF referentni pokušaj

**Pre-registracija:** 21. oktobar 2026, pre ijednog novog AC-OPF pokušaja. Repozitorijum owlCoder/gadapt:main, ne dirati bpzoran/gadapt. Ovo je dijagnostika domenskog optimizatora, **nije GAdapt algoritamski eksperiment**.

## Polazna činjenica

Izvorni MATPOWER case1888rte (2019) nije isti kao pandapower konvertovani model: slack referenca i Q/P distribucija se razlikuju. Direktni native PYPOWER AC PF iz iteracije 13 konvergira sa Q limitima tek uz tehnički popravljen Q-enforcement, ali ostaje 41 sabirnica ispod VMIN i **10 originalnih aktivnih generatora sa ukupno 54,95 MW ispod PMIN** već u ulaznom dispečingu. To nije dokaz OPF neizvodljivosti jer je aktivni P bio fiksiran.

## Cilj i unapred zamrznut postupak

Prvi pokušaj **lokalne** izvorno verne AC-OPF optimizacije sa **slobodnim P i Q dispečingom** i izvornim VMIN/VMAX i pozitivnim RATE_A na oba kraja grane, koristeći originalnu MATPOWER definisanu **linearnu generatorsku cenu**, a ne proizvoljni cilj minimizacije MW gubitaka.

1. Izvor je `MATPOWER/matpower/data/case1888rte.m`, commit `80b6e16f760f58721ad31221c7287c28259cd4ad`, blob `820bd317167381baf819d67eab7d886013e8b05a` (CC BY 4.0). Strogo netaknute numeričke matrice: `mpc.bus` = 1888x13, `mpc.gen` = 298x21, `mpc.branch` = 2531x13, `mpc.gencost` = 298x7. Osnovica 100 MVA. Proveriti da je originalni BUS1320 tip REF, izvornih online 291 generatora i 455 grana bez termičkog RATE_A. Originalni gencost mora imati MODEL=2, NCOST=3, C2=0 i C1 samo iz skupa {1,2,10}. Izvorni RATE_A=0 nije termički limit; originalni ANGMIN=ANGMAX=0 ne zadaje aktivno ograničenje u PYPOWER `makeAang`.
2. Pinovati Python 3.12, PYPOWER 5.1.19 (BSD), scipy 1.13.1, pandapower 2.14.11 kao okruženje, pandas 2.2.3, BLAS/OMP jedna nit. Ne menjati izvorni pandapower niti sistemski PYPOWER.
3. **Stvarna AC-OPF budget granica: najviše 2 poziva**: A standardni PYPOWER `case9` mali AC-OPF solver smoke test (radi provere interfejsa); B originalni RTE1888 AC-OPF sa identičnim solverom. Ako mali smoke baci grešku, velika instanca se preskače (brojati samo izvršene pozive). Svaki pokušaj čuvati čak i ako izuzetak, timeout ili fail.
4. Za oba `runopf` poziva: `OPF_ALG=560` (primal-dual interior-point), `PF_DC=False`, `OPF_FLOW_LIM=0` (oba kraja apparent MVA), `OPF_IGNORE_ANG_LIM=False`, `OPF_VIOLATION=5e-6`, `PDIPM_MAX_IT=100`, `VERBOSE=0`, `OUT_ALL=0`. Ne menjati napon, izvornu Q granicu, Pmin/Max, generator cenu, load, tap, rate ili topologiju.
5. Za slučaj B ne prijavljivati dobitak GAdapt-a. Ako solver `success=False` ili baca izuzetak, izmerene OPF fizičke metrike moraju biti JSON null, uz stvarni error i budžet. Ako `success=True`, **nezavisno** proveriti iz izlaznih MATPOWER tabela originalne individualne granice svih online generatora PG/QG, bus VMIN/VMAX, obostrana apparent MVA ograničenja grana koje imaju RATE_A>0, slobodni izvorni referentni gen PG/QG, i AC nodalni balans `V*conj(Ybus*V) - Sbus` u MVA. Ponovo izračunati originalni linearni trošak iz `gencost` i postignutih PG; uporediti sa prijavljenim `f`. Ne upoređivati economic dispatch cost sa ranijim MW loss ciljem.
6. Operativni kriterijum nezavisnog pregleda: maksimalna sabirnička kompleksna mismatch apsolutna vrednost <= 1e-3 MVA, max voltage bound excess <=1e-5 p.u., max individual generator P/Q bound excess <=1e-3 MW/MVAr i max rated branch end MVA excess <=1e-3 MVA. Sve tolerancije numeričke, **ne** opšta industrijska certificikacija. Ako solver success, a kriterijum ne prolazi, prijaviti `independently_validated=False`, bez optimističnih tvrdnji o izvodljivosti.
7. Unit testovi izvornog `gencost`, source identity i modela, ispravnog računanja linearne cene i reactive AC mismatch izraza na sintetičkom primeru; CI artefakti JSON i CSV verzionisani nakon izvršenja. Ako solver terminira nakon 15 minuta / memorijskog limita, beležiti timeout, ne tvrditi rezultat. GitHub Actions job najviše 25 minuta; vreme uključuje pripremu.
8. Ovo je samo referentni domenski *lokalni* nonlinear AC-OPF solver, ne globalni dokaz optimuma ili izvoda, a rezultat važi samo za originalni javni **istraživački** RTE model koji ne sme biti korišćen za planiranje/operaciju realnih francuskih/EU mreža.

## Hipoteza i obavezne negativne interpretacije

Pokušaj originalnog ekonomskog AC-OPF sa slobodnim PG može smanjiti izvorna Pmin kršenja, ali nema garancije da će veliki ne-konveksni problem konvergirati ili biti potpuno izvodljiv. Ne proglašavati uspehom ako padne smoke test, big solver, nodal balans ili pojedinačni limiti. Nema statističkog poređenja, novog GAdapt operatora ni tvrdnji o originalnosti ili superiornosti. Sledeći korak zavisi isključivo od potpunih stvarnih izlaza.
