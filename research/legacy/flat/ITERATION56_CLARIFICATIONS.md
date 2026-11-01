# I56: pojašnjenja i odstupanja (vodi se tokom izvršavanja)

Protokol: `ITERATION56_PROTOCOL.md` (zamrznut `3f09eb9`). Kod: `iteration56_cht_study.py`.

## Pojašnjenja (izbori koje protokol ne navodi; Codex 024: prihvatljivi, zabeležiti pre merenja)
- P1: razvojna semena (namena 2): FX-M i FX-T s = 1, 2, 3; proba (snaga) s = 11..15 (disjunktno).
- P2: case57 test scenariji (1,10, 203) i (1,15, 204): OPF ne uspeva → izuzeti po §2 (bez zamene). Blokovi
  case57 imaju 2 scenarija (20 jedinica pri 10 semena); 9 blokova sa jednakim težinama ostaje.
- P3: „b“ u FX-M = medijana v/d preko NOMINALNIH mutacija populacije (prvi poziv po jedinki); σ = medijana preko
  SVIH Gausovih mutacija, uključujući popravke (doslovno §5). Popravke pri ukrštanju i ponavljanja zbog
  jedinstvenosti beleže se odvojeno.
- P4: pokretanje je „ok“ ako potroši budžet, GAdapt vrati success i omotač nema izuzetaka; inače jedno ponovno
  pokretanje u novom procesu (oba pokušaja se čuvaju); reference i kalibracija koriste samo „ok“ pokretanja.

- P5: `dev_ref` je izvršen pre ispravke Codex 025 (brojanje izuzetaka u celom omotaču). Validnost: log
  izvršavanja je prazan (GAdapt svaki progutan izuzetak cost funkcije ispisuje sa traceback-om), 72/72 ok, 0
  grešaka, 0 ponavljanja → nijedan izuzetak nije progutan; rezultati važe. Format rezultata: `.json.gz`.

## Odstupanja
(nema do sada)
