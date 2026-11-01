# Iteracija 22 — centralna Q/VG korekcija fizički smanjuje IEEE118 prekršaje sa 30,526 na 2,464 MVAr, ali i dalje nije feasible

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** uspešan [CI #39655376644](https://github.com/owlCoder/gadapt/actions/runs/39655376644), svih 5 unapred registrovanih fizičkih originalnih IEEE118 `runpf` AC proračuna izbrojano, **0 od 5 potpuno izvodljivo**. Nije menjana GA implementacija, nema optimizatorskih pokretanja. Ovo je klasična inženjerska finite-difference feasibility-repair dijagnostika, **nije naučno novi GAdapt operator**.

## 1. Polazno arhivirano merenje i formulacija

[Preregistracija I22](ITERATION22_PROTOCOL.md), commit `50b32504fe361761583188ea49c82ef0236deeab`, zamrznuta pre novih simulator poziva. Sve je izvedeno na originalnom, nekonvertovanom PYPOWER `case118()`: originalnih 54 aktivnih gen, 118 bus, 186 grana, 54 PG fiksno na izvornoj referenci; Q se tokom NR PF ne forsira, ali **sve individualne source QMIN/QMAX** su obavezan naknadni uslov. Bus V, originalni P limiti, rated RATE_A MVA na oba kraja i kompleksni AC bilans takođe su provereni. Raniji originalni AC iz I20 sa BUS103 VG 0,99 i I21 sa BUS32 originalnim VG 0,963→0,973 čini fiksni već plaćen baseline **30,5259005332 MVAr** ukupnih individualnih Q prekršaja, sa tri QMIN-offendera BUS34, BUS92, BUS19. Taj baseline **nije** ponovo računat besplatno.

Korišćene su centralne konačne razlike iz **osam stvarnih ranijih I21 AC poziva** na tri QMIN relevantna originalna PV generatora, `dQ/dVG=(Q(+0,01)-Q(-0,01))/0,02`. Iz fiksnog prethodno izmerenog I21 `bus32_plus` baseline QG, za svaki generator postavljen je **ciljni srednji Q=(QMIN+QMAX)/2**, a VG pomak izračunat iz fizičkog nagiba, ograničen unapred registrovanim trust region [0,+0,008] p.u. Nisu izabrani retroaktivno nakon novih pokušaja:
- **BUS34** Q nagib ≈ **7181,77 MVAr/p.u.**, pozitivna VG korekcija **+0,00401603** (izvorni VG 0,984).
- **BUS92** nagib ≈ **4800,15 MVAr/p.u.**, korekcija **+0,00353320** (izvorni VG 0,99).
- **BUS19** nagib ≈ **4919,52 MVAr/p.u.**, korekcija **+0,00461911** (izvorni VG 0,962).

Linearna prognoza zasniva se na delimično različitoj baznoj tački (pre novog BUS32 VG+0,01), pa je **aproksimacija**, ne egzaktan višedimenzionalni elektroenergetski Jakobijan.

## 2. Pet originalnih stvarnih AC rezultata

| Predregistrisani originalni VG scenario | Source Q-offendera | Ukupni pojedinačni Q excess (MVAr) | Promena prema I21 baseline | Stvarna izvodljivost |
|---|---:|---:|---:|---|
| Prijašnja izmerena referenca — nije novi AC | 3 | **30,525901** | 0 | Ne |
| Samo BUS34 puna predviđena korekcija | 3 | 22,887628 | −7,638273 | Ne |
| Samo BUS92 puna korekcija | 2 | 19,565944 | −10,959957 | Ne |
| Samo BUS19 puna korekcija | 2 | 25,642154 | −4,883746 | Ne |
| **Sva tri po polovini predviđenog pomaka** | **1** | **2,464456** | **−28,061444** | **Ne** |
| Sva tri u punom predviđenom pomaku | **1** | **3,642855** | −26,883045 | **Ne** |

**Ključan nalaz:** kombinacija polovičnih malih pomaka popravila je BUS34 i BUS19 individualno, ali **BUS92 ostaje QMIN prekoračen za 2,464456 MVAr**, sa izmerenim BUS92 QG = **−5,464456** naspram QMIN=-3. Nasuprot tome, kombinacija punih malih pomaka stavlja i BUS92, BUS34 i BUS19 **unutar** originalnih Q granica, ali **izaziva novo QMIN kršenje na BUS36 (gen red17)**: QG ≈ **−11,642855** prema QMIN=−8, dakle **3,642855 MVAr**. U svim pet proračuna P/V/izvorni rated thermal zadovoljeni, kompleksni AC KCL maksimalni rezidual oko 1,5–1,6e-10 MVA, AC solver konvergirao.

**NIJEDAN I22 nije fizički izvodljiv**, uprkos drastičnom smanjenju ukupnih individualnih Q prekoračenja. Originalna ekonomska cena konvergentnog ali neizvodljivog stanja nije **prihvaćena feasible AC-OPF cena**, i ovaj rezultat nije GA optimalnost, čak ni lokalna OPF garantovana optimalnost.

## 3. Sledeći proverljiv istraživački korak

Polovina (`scale=0,5`) i ceo (`scale=1,0`) zajednički dodatni VG vektor, oba izmerena u I22, imaju **različite poslednje prekršioce** BUS92 (kod 0,5) i BUS36 (kod 1,0). To motiviše odvojeni, izričito unapred registrovani deterministički screen **međukoraka između tih poznatih tačaka**, bez novih optimizatorskih poziva, čije su vrednosti određene pre simulacije, uz dozvoljenu mogućnost da nijedan ne bude feasible.

Ako neka izvorna Q/P/V/RATE_A/KCL provera pokaže feasible tačku, ona je legitimna **fizički izvodljiva kontrolna tačka u fiksnom-P PV modelu**, ne dokaz da novi GAdapt može sam da je pronađe ili da nadmašuje najbolji izvorni AC-OPF; za algoritamsku novinu, trošak pretraživanja, mehanizam selekcije resursa i strong baselines još treba odvojena validacija.

## Dokazi

- [Pre-registracija I22](ITERATION22_PROTOCOL.md)
- [Kod sa pet stvarnih AC poziva i prethodno zamrznutim Q nagibima](iteration22_ieee118_qmidpoint_repair.py)
- [Unit testovi bez AC](test_iteration22_ieee118_qmidpoint_repair.py)
- [Sirovi CSV svih pet](results/ieee118_iteration22_qmidpoint_5_real_ac_20261021.csv)
- [Sirovi JSON, svi Q/P/V/thermal/KCL i izvorne promene](results/ieee118_iteration22_qmidpoint_5_real_ac_20261021.json)
- [GitHub Actions #39655376644](https://github.com/owlCoder/gadapt/actions/runs/39655376644)

**Važenje:** javni akademski IEEE118, nije industrijski operativni sistem; literatura o sensitivity-guided constraint repair postoji, te nema tvrdnje o naučnoj originalnosti ili generalizaciji.
