# Iteracija 11 — direktan AC power flow originalnog MATPOWER RTE1888 (bez konverzije)

**Preregistracija: 21. oktobar 2026, pre izvođenja novih izvornih AC proračuna.** Fork owlCoder/gadapt:main. Zabranjeno menjanje bpzoran/gadapt. Prethodne iteracije 9/10 otkrile su da izvorni MATPOWER v2 ima reference BUS1320, ali konvertovani pandapower BUS1268; zato se prestaje sa predstavljanjem konvertovanog slučaja kao numerički ekvivalentnog izvora.

## Naučno pitanje

Može li se originalni MATPOWER case1888rte.m (2019) analizirati direktno u nezavisnom PYPOWER AC NR solveru, sa **originalnim** sabirnicama, generatorima i svim ograncima, i kakve su stvarne naponske, P/Q i pozitivne RATE_A povrede? Ovo nije pun AC-OPF; fiksni izvorni PG/VG ostaju. Pitanje nije da li GAdapt pobeđuje neki metod.

## Reproduktivni izvor i protokol

1. Fiksni izvor: MATPOWER/matpower `data/case1888rte.m`, commit `80b6e16f760f58721ad31221c7287c28259cd4ad`, blob `820bd317167381baf819d67eab7d886013e8b05a`. CC BY 4.0, Josz et al. Original zabranjuje upotrebu za operativno upravljanje ili planiranje francuske i evropske mreže.
2. Arhivirati **svih 21 numeričkih kolona generatora** (298 redova), **13 kolona grana** (2531 red) i već arhiviranih 13 kolona sabirnica (1888 redova) u raw CSV, čuvajući redosled i originalne MATPOWER konstante. Proveriti baseMVA=100, izvorni tip bus3=1320, broj aktivnih i offline elemenata, generator red298 i prvobitni RATE_A=0 u 455 grana.
3. Direktno formirati `ppc` dict sa `version='2'`, `baseMVA=100`, `bus` (MATPOWER 13 stupaca), `gen` (21), `branch` (13). PYPOWER 5.1.19 `runpf`, SciPy 1.13.1, numpy/pandas kroz pinovani pandapower 2.14.11, Python 3.12, jednonitni BLAS/OMP.
4. **Dva ograničena stvarna AC poziva:** A: `PF_ALG=1, PF_TOL=1e-8, PF_MAX_IT=40, ENFORCE_Q_LIMS=0` (generatorski Q limiti *nisu enforced*, naknadno ih fizički izmeriti); B: identični originalni podaci uz `ENFORCE_Q_LIMS=1` (PYPOWER Q-limit enforcement). `VERBOSE=0, OUT_ALL=0`; svaki poziv brojati uključujući solver fail i exceptions; nikada ne prekucavati slučaj između poziva. U oba slučaja `PF_DC=0`.
5. Iz originalnog AC rezultata **nezavisno** izračunati bus naponska prekoračenja prema izvornom VMIN/VMAX (sum + count), generator P/Q min/max prema originalnim pojedinačnim granicama (sum MW i MVAr, count, maksimum; aktivne jedinice), originalne pozitivne RATE_A MVA granice na oba kraja aktivnih grana koristeći PF/QF/PT/QT, ne postavljati limite na RATE_A=0; P/Q status generatora na izvornom slack BUS1320 (row298) sa izričitim QMAX=1 MVAr. Posebno sačuvati snage injekcije i proračun gubitaka kao **dijagnostiku**, ne kao izvodljiv optimum.
6. Ako PYPOWER prijavi `success=False` ili exception, **ne objavljivati kao fizičku vrednost** nijednu njegovu naponsku/P/Q/termalnu metriku, koristiti JSON null i sačuvati grešku. Uspešna konvergencija ne znači izvodljivost OPF niti ispravnost svake pojedinačne capability krive. Ako PF enforcement promeni PV/PQ/slack izbor, prikazati promenu brojeva; ne pretpostavljati da je model isti.
7. Razlike u modelu, uključujući 75 pandapower trafo impedance odstupanja, nisu ovim objašnjene; rezultat može biti upoređen samo deskriptivno sa iteracijom 10. Ne raditi optimizaciju i ne tvrditi statističku superiornost, originalnost ili operativnu spremnost. Ukupan predviđeni fizički budžet **najviše 2 nezavisna native AC solver poziva**.
8. Pre proračuna: unit testovi za izvornu šemu, 455 RATE_A=0, oba kraja branch flows, offline filter, nulu fizičkih metrika na fail, izvorni BUS1320. Pokretanje putem GitHub Actions sa raw CSV/JSON kao trajnim artefaktima i sa kopijom u repo main nakon uspeha.

## Prihvatljivi zaključci

Ako PF uspe bez enforcementa uz limit violation, to je **konvergentan, ali neizvodljiv OPF kandidat**. Ako drugi PF konvergira uz Q limits, ali postoji druga povreda, nije OPF kandidat. Ako oba ne uspeju, nije dokaz matematičke neizvodljivosti. Tek pun source-faithful AC-OPF model sa proverom svih domen-specifičnih ograničenja može biti benchmark za nova GAdapt unapređenja.
