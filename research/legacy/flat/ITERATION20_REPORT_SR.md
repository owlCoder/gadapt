# Iteracija 20 — ciljana IEEE118 Q osetljivost: jedan VG setpoint uklanja oba uporna Q prekršaja, ali ostaju još četiri

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** potpuno izvršen unapred registrovanih **8 stvarnih originalnih `pypower.runpf` AC NR proračuna**, svi konvergentni, **nijedan potpuno izvodljiv** po svim izvornim generatorskim QMIN/QMAX granicama. **Nema GA/DE/random optimizacije i nije nova GAdapt metoda.**

## 1. Poreklo i strogo fiksiran eksperimentski cilj

Iz [iteracije 19](ITERATION19_REPORT_SR.md) zna se da originalni IEEE118 izvorni baseline ima **78,099195 MVAr ukupnog pojedinačnog Q viška/nedostatka**, bez P/V/RATE_A prekoračenja, i da originalni generator #46 na **BUS103** ima QG=+75,422364 naspram izvornog QMAX=40, dok #48 na **BUS105** ima QG=-18,334525 naspram izvornog QMIN=-8. Njihovi početni izvorni VG su **1,01** odnosno **0,965 p.u.** i oba BUS-a su originalni PV (type 2). Obe PV kontrole bile su izostavljene iz kontrola ograničenog IEEE118 GAdapt pilota I18.

[Pre-registracija I20](ITERATION20_PROTOCOL.md), commit `25d630a71042974d8efd2dce97a9671dc90de36f`, sačuvana je **pre novih AC pokušaja**. Ulaz je neizmenjen `pypower.case118()` (118 bus, 54 aktivna gen, 186 grana); originalni PG **svih 54 generatora** su fiksni, sve ostale VG takođe. Dve izvorne PV vrednosti varirane su samo za `±0.02 p.u.` u originalnim granicama. Bazni prethodni AC rezultat iz I19 je pročitan, **nije besplatno ponovo evaluiran**. Izvršenih novih pokušaja: **tačno osam**.

## 2. Sirovi fizički nalazi

[GitHub Actions #39653434474](https://github.com/owlCoder/gadapt/actions/runs/39653434474): uspešni unit testovi i svih 8 realnih AC poziva sa izvornom mrežom, nezavisnim proverama originalnih pojedinačnih PG/QG, svih VMIN/VMAX, pozitivnih RATE_A na oba kraja i kompleksnog KCL. U svim osam numerički konvergentnih slučajeva **0 P, 0 V, 0 rated thermal** kršenja; ukupna Q ograničenja ostala su nezadovoljena.

| Izvorni VG probni scenario | Gen BUS103 QG (MVAr) | Gen BUS105 QG (MVAr) | Broj svih Q-offendera | Ukupan Q excess (MVAr) | Promena ukupnog Q excess prema baseline |
|---|---:|---:|---:|---:|---:|
| Prethodno originalno stanje, *bez novog poziva* | +75,422 | -18,335 | 6 | **78,099** | 0 |
| **BUS103 −0,02** | **+1,320** | **−6,221** | **4** | **32,346** | **−45,753** |
| BUS103 +0,02 | +152,654 | −30,425 | 8 | 172,222 | +94,123 |
| BUS105 −0,02 | +87,904 | −111,141 | 7 | 213,927 | +135,828 |
| BUS105 +0,02 | +63,057 | +78,662 | 8 | 154,708 | +76,609 |
| Obe −0,02 | +13,525 | −99,299 | 6 | 166,664 | +88,565 |
| BUS103 −0,02, BUS105 +0,02 | −10,770 | +91,050 | 6 | 128,581 | +50,482 |
| BUS103 +0,02, BUS105 −0,02 | +165,413 | −122,962 | 7 | 290,786 | +212,687 |
| Obe +0,02 | +140,012 | +66,298 | 8 | 242,771 | +164,672 |

**Jasno lokalno poboljšanje:** samo smanjenje generatora BUS103 VG sa izvornog 1,01 na **0,99 p.u.** dovelo je QG BUS103 sa +75,422 na +1,320 (sada unutar originalnih [−15,+40] MVAr), a istovremeno QG BUS105 sa −18,335 na **−6,221** (sada unutar originalnih [−8,+23] MVAr). Ukupno pojedinačno Q prekoračenje svih 54 izvora palo je sa **78,099 na 32,346 MVAr**, smanjenje za **45,753 MVAr**, odnosno približno **58,6%**. Ovde su izvorni P/V/termalni i kompleksni nodalni bilans ostali zadovoljeni prema već zamrznutim numeričkim kriterijumima.

**I dalje fizički neizvodljivo:** četiri originalna generatora još krše svoje QMIN:
- originalni gen #16, **BUS34**: QG≈−20,827 naspram QMIN=−8, višak **12,827 MVAr** ispod dozvoljenog;
- gen #43, **BUS92**: QG≈−13,960 naspram QMIN=−3, prekršaj **10,960 MVAr**;
- gen #9, **BUS19**: QG≈−14,274 naspram QMIN=−8, prekršaj **6,274 MVAr**;
- gen #15, **BUS32**: QG≈−16,285 naspram QMIN=−14, prekršaj **2,285 MVAr**.

Stoga ni "najbolji" deterministički screen kandidat ne sme biti proglašen izvodljivim AC-OPF, a njegova originalna ekonomska funkcija nije ostvaren optimum. Štaviše svih ostalih **7/8** simetričnih perturbacija ukupnu Q povredu je **povećalo**, neke dramatično. To dokazuje važnost izbora relevantnih fizičkih kontrolnih varijabli i smerova, ali **ne** garanciju da će bilo koji adaptivni operator statistički poboljšati GAdapt na većoj mreži.

## 3. Metodološki zaključak

Deset I19 AC pokušaja prethodno je dalo gotovo konstantan Q prekršaj BUS103/BUS105 jer **njihove lokalne PV setpoint kontrole nisu bile deo I18 genoma**, dok su četiri PG i pet geografski drugih VG slučajno/pretragom menjani. Osam novih I20 proba pokazuju da lokalni generator BUS103 VG ima **jaku fizičku vezu** sa obe Q granice i može ih popraviti bez nove P/V/rated-termalne povrede u jednom izolovanom stanju.

Ovo je naučno smislen **diagnostic pilot o reprezentaciji/selektovanju kontrolnih resursa**, ne originalna teorija genetskog algoritma. Algoritamska novost, superiornost ili industrijski deployment i dalje nisu dokazani. IEEE118 je javna testna mreža. Puni originalni IEEE118 AC-OPF je već lokalno post-hoc verificirano izvodljiv u I16 — a nije isto što i ovaj PV-kontrolisani PF podskup.

**Sledeća pre-registracija treba da proveri** reaktivnu Q osetljivost originalnih lokalnih PV setpointova BUS34, BUS92, BUS19 i BUS32, *polazeći od I20 fiksnog stanja BUS103 VG−0,02*, bez besplatnog simulatora i sa objektivnom evidencijom pogoršanja i poboljšanja. Tek posle toga preispitati GAdapt strukturu genoma i moguće feasibility-aware adaptation mehanizme uz literaturne reference i jake kontrole.

## Dokazi

- [Protokol sa svih 8 scenarija](ITERATION20_PROTOCOL.md)
- [Kod za tačno 8 stvarnih NR simulacija](iteration20_ieee118_reactive_sensitivity.py)
- [Unit testovi bez AC poziva](test_iteration20_ieee118_reactive_sensitivity.py)
- [Sirovi CSV — osam merenja](results/ieee118_iteration20_q_sensitivity_8_real_ac_20261021.csv)
- [Sirovi JSON — pojedinačni Q/P/V/MVA/KCL identiteti i sve komponente](results/ieee118_iteration20_q_sensitivity_8_real_ac_20261021.json)
- [GitHub Actions #39653434474](https://github.com/owlCoder/gadapt/actions/runs/39653434474)
