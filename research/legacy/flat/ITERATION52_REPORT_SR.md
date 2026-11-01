# ITERATION52: nalazi integriteta na stvarnom AC dispečingu (IZVEŠTAJ)

**Datum:** 2026-10-23.
- Protokol: [ITERATION52_PROTOCOL.md](ITERATION52_PROTOCOL.md) (`32bac01`) sa dopunom A1 (`0caef4c`).
- Kod: [iteration52_dispatch_integrity.py](iteration52_dispatch_integrity.py) (`8345310`).
- Sirovi izlazi: [results/iteration52/](results/iteration52/), sa `pip freeze` po biblioteci; agregat je u
  `integrity_dispatch.json`.

## 1. Odstupanje (pre ijednog merenja)
Prvo izvršavanje palo je u svih 315 ćelija pri uvozu (`networkx`; `pypower==5.1.19` nekompatibilan sa NumPy 2.5),
pre ijedne evaluacije funkcije troška. Arhivirano je u `results/iteration52/failed_run_env/`. Posle dopune A1
(pypower 5.1.21 i networkx 3.7, kao u repo `.venv`) merenje je izvršeno jednom.

Usput je otkriveno da I47 beleži pogrešnu pypower verziju (fiksna podrazumevana vrednost). Ispravka je u I47
izveštaju.

## 2. Primarni ishod: H52 POTVRĐENA
Status po biblioteci („bar jedan nalaz integriteta bez C1“) poklapa se između sintetičkih funkcija (I49 + I51, I50) i
stvarnog AC dispečinga (case14, case39, case118; 5 semena) za **19 od 21** biblioteke (95% CI 70–99%). Prag je bio 17.
Nijedna biblioteka nije neocenljiva.

**Dva neslaganja:**
- **Nevergrad:** sintetički D3 i D3x javljali su se samo na platou 10D. Na dispečingu je ocenljivo samo 5 od 15 ćelija;
  ostalih 10 pada zbog NumPy 2.5 greške ([#1707](https://github.com/facebookresearch/nevergrad/issues/1707)). U tih
  5 ćelija nema D3.
- **SciPy DE:** nov R3, samo na dispečingu (§4).

## 3. Prenos po klasama
- **Preneto 7 od 10** sintetičkih nalaza (biblioteka, klasa): DEAP C3, PyGAD C5, cma C4, evotorch C3, GFO R2,
  scikit-opt R3 i SMAC D3x.
- **Nije preneto:** Nevergrad D3 i D3x (vidi gore) i GFO R3. R3 kod GFO-a je verovatno posledica obrnutog znaka (R2):
  na platou su vrednosti negativne, pa negirana prijava ispada lošija od najbolje. Na dispečingu su vrednosti
  pozitivne, pa ostaje samo R2.
- **Novo na dispečingu:** SciPy DE R3.

**C1 na realnoj funkciji je specifičan.** GAdapt kontrola (probni pozivi) ima C1 u 15/15 pokretanja, a ostale
biblioteke skoro nikad: GFO 4, SciPy DE 4, evox 1 (od 15). Nespecifičnost C1 u I50 potiče uglavnom od test-funkcija,
posebno od platoa, čiji je optimum u uglu.

## 4. Nov nalaz: SciPy `differential_evolution` odbacuje bolji rezultat poliranja
Uz podrazumevano `polish=True`, rezultat L-BFGS-B se prihvata samo ako je `success=True`.

**Na dispečingu:**
- case118, seme 6001: poliranje troši 15.444 evaluacija, staje na `maxfun` i dostiže 143.102. Vraćeno je 271.061.
- case39, seme 6002: `ABNORMAL`; postignuto 42.659, vraćeno 62.886.
- Ukupno R3 u 5/15 pokretanja.
- Ukupan broj poziva je 1270–16.239, a nominalni DE budžet je 795–960. Formula iz dokumentacije važi samo bez
  poliranja, pa ovo nije C4, ali je praktično do 20× više evaluacija.

**Minimalan primer bez pypower-a:** 10D, kvadratna funkcija sa „zidom“ kazne. Vraćeno je 22,97, a evaluirano 1,10.
Potvrđeno je na SciPy 1.18.1 i na nightly 2.0.0.dev0 (`3f3cfc3`).

Prijavljeno: [scipy #26479](https://github.com/scipy/scipy/issues/26479).
- Po I50 pravilu, ovo bi bila „praznina u dokumentaciji“.
- Prijavljeno je ipak, jer je posledica velika (prijavljeni rezultat do 89% lošiji od evaluiranog), a sličan issue
  nije pronađen.

## 5. scikit-opt DE: R3 ponovljen i uzročno potvrđen
- **Pojava:** R3 se javlja u 2/15 pokretanja na dispečingu, a na običnoj sferi (10D) u 10 od 200 semena.
- **Uzrok:** posle selekcije, `self.Y` sadrži samo vrednosti probnih vektora. Ispravka u podklasi smanjuje R3 na
  0 od 200.
- **Prijava:** [scikit-opt #248](https://github.com/guofei9987/scikit-opt/issues/248), radi doslednosti sa SciPy
  prijavom.

## 6. Rasipanje na stvarnoj funkciji
Medijana udela ponovljenih evaluacija:

| Biblioteka | Dispečing | Sintetičke funkcije |
|---|---|---|
| scikit-opt DE | 36% | 47% |
| geneticalgorithm | 9,1% | 41,5% |
| DEAP | 8,4% | 11,5% |

Sintetički plato je preuveličao rasipanje kod geneticalgorithm. Pošto evaluacija dispečinga traje 2–16 ms, apsolutno
izgubljeno vreme je malo (najviše 12 s po biblioteci). Kod skupog modela taj udeo budžeta je ono što se računa.

## 7. Greške
| Biblioteka | Neuspele ćelije | Uzrok |
|---|---|---|
| Nevergrad | 10/15 | #1707 |
| bayes_opt | 5/15 | timeout na case118 |
| bofire | 5/15 | timeout i `ModelFittingError` na case118 |

## 8. Zaključak
Nalazi integriteta sa sintetičkih funkcija prenose se na stvaran infrastrukturni problem za 19/21 biblioteke.
Stvarna funkcija je otkrila i grešku koju test-funkcije nisu pokazale (SciPy DE). Preporuka za praksu se zato
pooštrava: reviziju raditi i sa sopstvenom funkcijom troška, ne samo na test-funkcijama.
