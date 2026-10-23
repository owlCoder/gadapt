# ITERATION49 — revizija integriteta evaluacija u Python optimizacionim bibliotekama: izveštaj

**23. oktobar 2026.** Protokol: [ITERATION49_PROTOCOL.md](ITERATION49_PROTOCOL.md) (`92b307f`). Alat `ab641be`. Okruženje:
Python 3.14, NumPy 2.5.4, verzije zaključane u [h4_requirements_lock.txt](h4_requirements_lock.txt). Izvršeno je
**jedno** pokretanje: 300 ćelija (10 biblioteka × 6 problema × 5 semena), svaka sa ponovljenim i transformisanim
pokretanjem, ukupno 53 s. Sirovi izlaz: [results/iteration49/integrity_audit.json](results/iteration49/integrity_audit.json).

## 1. Validacija alata (§6, pre pokretanja): **prošla**
- Pet podmetnutih grešaka (ugaoni probni poziv, duplikat, poziv preko budžeta, neevaluiran rezultat, pogrešna
  vrednost) otkriveno je tačno, svaka u svojoj klasi.
- Čista referenca nije označena ni za jednu klasu.
- GAdapt sa podrazumevanim podešavanjima daje C1, a sa `probe_cost_function=False` ne daje.

## 2. Preregistrovani ishod: **ČESTO** (4/9 biblioteka; Clopper–Pearson 95% [0,14; 0,79])

| Biblioteka | Pokretanja sa nalazom (od 30) | Klasa | Razvrstavanje (post hoc) | Već poznato |
|---|---|---|---|---|
| DEAP `eaSimple` | 30/30 | **C3** van granica | Dizajn: DEAP ne kontroliše granice; korisnik mora dodati dekorator | Da: Ravber i sar. 2025, [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603) |
| PyGAD | 30/30 | **C5** pozivi posle povratka (21 po pokretanju) | Dokumentovano: `best_solution()` bez `pop_fitness` ponovo računa fitnes populacije | Da: [PyGAD #160](https://github.com/ahmedfgad/GeneticAlgorithmPython/issues/160) |
| cma `fmin2` | 10/30 | **C4** preko dokumentovanog `maxfevals` (do 1011 za 1000) | Odstupanje od dokumentacije: „maximum“ se proverava po iteraciji | Da: [pycma #108](https://github.com/CMA-ES/pycma/issues/108), [#195](https://github.com/CMA-ES/pycma/issues/195) |
| Nevergrad `NGOpt` | 5/20 (10 pokretanja palo) | **D3** nereproduktivno uprkos `parametrization.random_state` (plato, 10D; razlika već od 1. poziva; NGOpt bira `ParametrizedMetaModel(CmaFmin2)`) | Odstupanje od dokumentovanog načina zadavanja semena | Da: [nevergrad #1572](https://github.com/facebookresearch/nevergrad/issues/1572) (otvoren od 2023; ispravka: ranije pisalo #966, vidi §6) |

**Bez nalaza integriteta:** pymoo, Optuna, PySwarms, geneticalgorithm, SciPy DE (uz napomene ispod).

## 3. Ostali nalazi (nisu klase integriteta po protokolu)
- **Pad:** Nevergrad `NGOpt` pada u 10/30 ćelija (sfera i Rastrigin, 10D). Uzrok je
  `float(model.predict(...))` u `metamodel.py:177`, koji NumPy 2.5 više ne prihvata.
  - Već prijavljeno kao [nevergrad #1707](https://github.com/facebookresearch/nevergrad/issues/1707), zatvoreno
    2026-03-16 ispravkom u `main` grani (PR #1712). Poslednje izdanje 1.0.12 (2025-04-23) je ne sadrži
    (ispravka: ranije je pisalo „zatvoreno 2025-12-26“).
  - Ograda: okruženje je novije od onoga što biblioteka verovatno testira.
- **Rasipanje na duplikate (C2, medijana udela):**
  - geneticalgorithm **41,5%**, DEAP 11,5% (poznato: [DEAP #162](https://github.com/DEAP/deap/issues/162)),
    PyGAD 3,9%, SciPy DE 0,2%;
  - ostale 0%.
  - Za skupu funkciju troška (npr. AC proračun) 41,5% znači da se skoro polovina budžeta troši na tačke koje su već
    evaluirane.
- **GAdapt (kontrola):** C1 u 30/30, R3 u 5/30. Na plato problemu probni poziv u donjem uglu jeste globalni minimum,
  koji GAdapt ne prijavljuje kao rezultat. Ovo potvrđuje artefakt iz I43 na nezavisnom problemu.
- **Invarijantnost G1 (sekundarno, prior art):** tačno invarijantni na afinu promenu jedinica po promenljivoj su
  pymoo, DEAP, PyGAD, geneticalgorithm i Optuna (30/30); SciPy DE 13/30; PySwarms, cma, Nevergrad i GAdapt 0/30.
  - Za cma je to posledica našeg adaptera (skalarni σ0 umesto `CMA_stds` po promenljivoj), ne same biblioteke.
  - Zato G1 ne služi za zaključke o cma.

## 4. Analiza osetljivosti (post hoc, eksplicitno)
- Ako se računaju samo nalazi koji **protivreče dokumentaciji** (cma C4, Nevergrad D3), a izuzmu dokumentovane ili
  dizajnerske odluke (DEAP C3, PyGAD C5), dobija se **2/9**, što je granica „IZMEĐU“.
- Nijedan od četiri nalaza nije nov kao pojedinačna greška: svi su već prijavljeni ili dokumentovani.

## 5. Zaključak
- **Rasprostranjenost:** problemi integriteta evaluacija su česti po preregistrovanom kriterijumu (4/9). Kada se
  računa samo protivrečnost dokumentaciji, nalaz je na granici (2/9).
- **Doprinos je metodološki:**
  - validirani black-box alat otkriva **sve** ove klase automatski, bez čitanja koda;
  - jednim pokretanjem od 53 s ponovo nalazi probleme koji su ranije prijavljivani pojedinačno, kroz godine,
    u issue trackerima;
  - na GAdapt-u pokazuje kako takav artefakt menja zaključak eksperimenta (I39/I43).
- **Praktično za industriju:** pre poređenja optimizatora na skupoj funkciji troška treba pokrenuti ovakvu reviziju.
  - Uz PyGAD treba prosleđivati `pop_fitness`.
  - Uz DEAP treba dodati kontrolu granica.
  - Ne treba se oslanjati na `maxfevals` kao tvrdu granicu (cma).
  - Treba proveriti reproduktivnost Nevergrad-a pri izabranom optimizatoru.
  - Treba uzeti u obzir 41,5% duplikata kod geneticalgorithm.
- **Prijava održavaocima:** vidi §6 (jedan komentar, Nevergrad #1572).

## 6. Naknadna provera Nevergrad D3 (2026-10-23, posle zaključka; ne menja preregistrovani ishod)
- **Ispravka citata:** D3 odgovara [nevergrad #1572](https://github.com/facebookresearch/nevergrad/issues/1572)
  („ParametrizedMetaModel(multivariate_optimizer=CmaFmin2) runs are not reproducible“, otvoren od 2023, bez
  odgovora održavalaca). #966 opisuje nestabilne benchmark testove iz 2020. i bio je pogrešno naveden.
  `CmaFmin2`, `MetaModelFmin2` i `NGOpt$` su u listi `UNSEEDABLE` u testovima biblioteke, ali to nije dokumentovano.
- **Nalaz potvrđen na `main` grani** (`55950f95`) i na 1.0.12: nereproduktivno i između odvojenih procesa, od 1. poziva.
- **Uzrok, uzročno potvrđen:**
  1. `recastlib.py` poziva `cma.fmin` bez `seed`, pa pycma koristi `seed='time'` i usput menja globalni `np.random`;
  2. `metamodel.learn_on_k_best` pravi unutrašnji Powell/DE sa parametrizacijom bez semena.
- **Ispravka od 12 linija** ([diff](iteration49_nevergrad_1572/nevergrad_seed_fix.diff)): 16/16 ćelija reproduktivno
  (sfera i plato, 10D, 8 semena, isti proces i odvojeni procesi). Na nepromenjenoj `main` grani je 0/6. Originalni
  primer iz #1572 je takođe reproduktivan. Relevantni testovi biblioteke: 11 prošlo, 15 preskočeno.
- **Objavljeno:** [komentar na #1572](https://github.com/facebookresearch/nevergrad/issues/1572#issuecomment-6357311253)
  sa uzrokom, diff-om i proverom. Korisnik je odluku o objavi prepustio autonomnoj proceni. Na #966 i #1707 se ne
  komentariše: prvi je drugi problem, a drugi je već ispravljen.
- **Usput:** proces sa globalnim `NGOpt` objektom ne završava se posle `minimize` (nit `CmaFmin2` nije daemon).
  Verovatno je to već [#180](https://github.com/facebookresearch/nevergrad/issues/180) i ne prijavljuje se.
  Na 1.0.12 sa NumPy 2.5 pad iz #1707 se jednom manifestovao kao zamrzavanje (0% CPU).
- Arhiva: `research/iteration49_nevergrad_1572/` (skripte, diff, sirovi izlazi, tekst komentara).
