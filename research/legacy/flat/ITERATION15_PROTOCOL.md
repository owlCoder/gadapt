# Iteracija 15 — dijagnostički status native AC-OPF i druga PYPOWER strategija (565)

**Preregistrovano 21.10.2026 posle neuspešne iteracije 14 i PRE novih AC-OPF poziva.** I14 je imao dva prava AC-OPF poziva: `case9` sa algoritmom 560 uspešan; originalni `case1888rte` sa 560 nije uspeo posle 5,1993 s. Bez uspešnog originalnog OPF-a nisu objavljene fizičke vrednosti. Nema GAdapt poređenja.

## Jedino novo pitanje

Da li standardna PYPOWER interior-point *step-controlled* strategija `OPF_ALG=565`, uz **potpuno iste originalne uslove**, može da reši originalni ekonomski AC-OPF ili makar da pruži proverljiv signal o numeričkom prekidu? Nije zamena problemne formulacije, ne menja ni limit niti cenu.

## Predefinisani postupak

1. Tačno iste arhivirane originalne MATPOWER 2019 matrice (1888 BUSx13, 298 GENx21, 2531 BRANCHx13 i 298 GENCOSTx7), izvor MATPOWER commit `80b6e16f760f58721ad31221c7287c28259cd4ad`, CC BY4.0, nedozvoljeno za operativno upravljanje / planiranje stvarne francuske ili evropske mreže. `case9` ostaje standardni PYPOWER kontrolni problem, isti pinovi Python3.12, PYPOWER5.1.19, SciPy1.13.1, pandas2.2.3, pandapower2.14.11, jednonitni BLAS.
2. Najviše dva nova AC-OPF poziva: **prvo** `case9` sa algoritmom 565 i najviše 2 minuta; samo ako numerički uspe, **drugo** originalni RTE1888 sa algoritmom 565 i 13-minutnim timeout-om. `OPF_FLOW_LIM=0`, `PF_DC=0`, `OPF_IGNORE_ANG_LIM=False`, `OPF_VIOLATION=5e-6`, `PDIPM_MAX_IT=100`, `VERBOSE=0,OUT_ALL=0`. Ne prepravljati start, napone, termalna ograničenja, Q/P granice, originalnu ekonomsku cenu ili topologiju.
3. Za svaki solver poziv, bez obzira na konačni `success`, sačuvati originalni `raw.info`, `raw.output.message`, `iterations`, eventualne prve/poslednje `feascond`, `gradcond`, `compcond` i `costcond` iz iteracionog niza; ovo su **numerički statusi solvera, ne fizička snaga ili izvodljivost**. Ne prijavljivati neuspele PG/QG, napone, MW gubitke, target f i rešenja kao fizički relevantna; u neuspehu fizička metrika je JSON null.
4. Ako originalni solver tvrdi success, sprovesti isti strogi `audit_success` kao iteracija 14 (originalna generator PG/QG, bus VMIN/VMAX, source-positive RATE_A MVA oba kraja, složeni AC nodalni KCL i ponovni izračun originalne ekonomske cene). `solver_success` i `posthoc_validated` obavezno **odvojiti**: neuspeh audit-a ne sme sakriti stvarni solver signal. Ako solver success ali posthoc validator podigne izuzetak, prikazati `validator_error` i `posthoc_validated=false`, nikako fizikalno izmišljene vrednosti.
5. Bez p-vrednosti, poređenja GAdapt-a, heurističkih pretraga ili trećih pokušaja dok protokol nije završen. Svi testovi, raw CSV/JSON i izveštaj commited u owlCoder/gadapt:main. Ako i 565 ne uspe, ne tvrditi matematičku neizvodljivost — sledeće istraživanje proverava nezavisni solver / stvarne razloge numeričkog neuspeha.

## Naučna definicija rezultata

Pozitivan rezultat samo ako originalni AC-OPF ima `success=True` i **sve** nezavisne proveravane izvorne fizičke kriterijume ispunjene. Ako ne, zabeležiti pouzdane dijagnostičke kodove kao negativan rezultat, a ne simulirati optimalno rešenje.
