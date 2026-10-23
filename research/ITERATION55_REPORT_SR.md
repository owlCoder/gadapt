# ITERATION55 (rad: Studija 5) — ispravljeni D3x i arhiva tragova poziva (IZVEŠTAJ)

**Datum:** 2026-10-23.
- Protokol: [ITERATION55_PROTOCOL.md](ITERATION55_PROTOCOL.md) (`4c2b4cd`) sa odstupanjima O1–O3 zabeleženim tokom
  merenja (`d2a3bb7`, `21787e7`, `8eaf8fd`).
- Kod: [iteration55_d3x_traces.py](iteration55_d3x_traces.py) (`ee39baf`; O1 ispravka na strani drajvera `21787e7`),
  ponovni račun [iteration55_recompute.py](iteration55_recompute.py).
- Izlazi: [results/iteration55/](results/iteration55/) (`cells_<lib>.json` sa `pip freeze`, kompletni tragovi
  `traces/<lib>/*.npz`, `recompute.json`); post hoc: [results/iteration55_posthoc/](results/iteration55_posthoc/).
- Povod: Codex recenzija 009 (`python -I` ignoriše `PYTHONHASHSEED`; arhiva bez tragova).
- Merenje je pokrenuto jednom (21 biblioteka × 30 ćelija; 630 ćelija, 20:40–22:55).

## 1. Provera manipulacije

U svakoj ćeliji sa tri uspešna procesa kontrolni heš je bio isti za A i A′ (`PYTHONHASHSEED`=1) i različit za B (=2):
**620/620** važećih ćelija. Nevažećih 10 su Nevergrad ćelije (sfera i Rastrigin, N = 10) koje padaju sa istom
`TypeError` greškom (NumPy 2.5) kao u I49.

## 2. Preregistrovane hipoteze

| Hipoteza | Rezultat | Ishod |
|---|---|---|
| H55a: D3x_razl tačno za {Nevergrad, SMAC} | D3x_razl > 0: Nevergrad (5/20), SMAC (30/30); ostalih 19 biblioteka 0 | **PODRŽANO** |
| H55b: SMAC D3x_isto = 0 (30/30), D3x_razl ≥ 25/30 | D3x_isto 0/30, D3x_razl 30/30, D3 0/30 | **PODRŽANO** |
| H55c: Nevergrad D3x_isto > 0 | D3x_isto 5/20 (iste ćelije kao D3 i D3x_razl) | **PODRŽANO** |
| H55d: biblioteke bez D3/D3x reprodukuju arhivirane zastavice u svim ćelijama | 1 odstupanje: emukit, plato, N = 2, seme 6001, C2 0 → 1 | **NIJE PODRŽANO** (strogo); objašnjeno post hoc (§3) |

- **Tumačenje:** zavisnost SMAC-a od `PYTHONHASHSEED` sada je utvrđena i unutar same revizije (isto seme → isti niz,
  različito seme → različit niz), a ne samo u zasebnom reproduceru. Nevergrad nije reproduktivan ni sa istim heš
  semenom, što odgovara poznatom uzroku (`cma.fmin` sa `seed='time'`).

## 3. Reproduktivnost arhive (opisno, uz H55d)

- **Zastavice:** reklasifikacija iz tragova daje isti skup biblioteka sa nalazom bez C1 kao rad: Studija 1
  {cma, DEAP, Nevergrad, PyGAD} = 4/9; Studija 2 {evotorch, GFO, scikit-opt, SMAC} = 4/12; ukupno 8/21.
- **Nizovi poziva (SHA-256) naspram arhive I50:** 318/358 identično bit po bit (I49 arhiva nema heševe).
  Razlike: SMAC 30/30 (I50 je zbog `-I` radio sa nasumičnim heš semenom; očekivano po H55b) i emukit 10/30.
- **emukit (post hoc, O3):** drajver I55 nije postavio `VECLIB_MAXIMUM_THREADS=1` (Apple Accelerate), koji je I50
  postavljao. Sa tom promenljivom svih 10/10 ćelija poklapa arhivu bit po bit. Uzrok je broj BLAS niti: isto seme,
  iste verzije i isti računar, a različit niz poziva. Ovo je dodatno ograničenje reproduktivnosti za biblioteke koje
  se oslanjaju na linearnu algebru (Gausovi procesi), a ne greška biblioteke.

## 4. Posledice za rad

- Ispravka iz §3 rada je potvrđena: oba pozitivna D3x nalaza stoje sa stvarnim, zabeleženim heš semenima.
- Studije 1–2 su sada podržane kompletnim tragovima i skriptom za reklasifikaciju (bez Studije 4, dispečinga).
- Nova preporuka za praksu: pri proveri reproduktivnosti fiksirati i broj niti numeričkih biblioteka (uključujući
  `VECLIB_MAXIMUM_THREADS` na macOS-u), jer i on menja niz poziva.
