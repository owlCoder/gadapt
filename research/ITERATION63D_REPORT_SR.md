# ITERATION63-D: deskriptivna ekstenzija I63 (NEPOTVRDNO) — izveštaj (generisan iz arhive)

**Status: DESKRIPTIVNO.** I63 je stao na konačnom STOP-u u fazi snage (zamrznuti kriterijum kalibracije lažne ekvivalencije na granicama ±0,05 nije zadovoljen; zahtev je veoma strog i pri stvarnoj veličini testa 5% prolazi približno 2,1% simulacionih serija; vidi `ITERATION63_REPORT_SR.md`). Ovde je izvršen isti zamrznuti test dizajn (roster, normalizatori, FX-T vektor, n iz I63 skrininga, estimand W/θ₆₃, bootstrap) u novom direktorijumu, bez zaključka o H56a/H63 i bez zamene I63. Izveštava se procena sa intervalima.

n po ćeliji = 160. θ₆₃ = 0.0139; 95% CI [-0.0090, 0.0372]; 90% CI [-0.0052, 0.0332].

Deskriptivni dijagnostici zamrznutih pragova, bez inferencijalne odluke: donja 95% granica > 0: False; gornja < 0: False; 90% interval unutar (−0,05; 0,05): True. Srednje po mreži: {'case30': -0.00625, 'case39': 0.034375, 'case24_ieee_rts': 0.013541666666666669}; izostavljanje jedne mreže: {'case30': 0.023958333333333335, 'case39': 0.0036458333333333343, 'case24_ieee_rts': 0.014062500000000002}.

| ćelija | n | srednje d | W(FR) | W(SP) | izv. FR AD-N | izv. FR FX-T | izv. SP AD-N | izv. SP FX-T | med. G FR AD-N | med. G FR FX-T | med. G SP AD-N | med. G SP FX-T |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case24_ieee_rts|2 | 160 | -0.022 | 0.525 | 0.547 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0028 | 0.0028 | 0.0028 | 0.0028 |
| case24_ieee_rts|3 | 160 | 0.069 | 0.650 | 0.581 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0072 | 0.0032 | 0.0072 | 0.0059 |
| case24_ieee_rts|4 | 160 | -0.006 | 0.516 | 0.522 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0130 | 0.0130 | 0.0130 | 0.0130 |
| case30|2 | 160 | -0.013 | 0.491 | 0.503 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0066 | 0.0066 | 0.0066 | 0.0066 |
| case30|3 | 160 | 0.000 | 0.500 | 0.500 | 0.00 | 0.00 | 0.00 | 0.00 | — | — | — | — |
| case39|2 | 160 | -0.016 | 0.516 | 0.531 | 1.00 | 1.00 | 1.00 | 1.00 | -0.0063 | -0.0073 | -0.0068 | -0.0070 |
| case39|3 | 160 | 0.116 | 0.581 | 0.466 | 0.97 | 0.96 | 0.97 | 0.97 | -0.0072 | -0.0084 | -0.0083 | -0.0073 |
| case39|4 | 160 | 0.003 | 0.503 | 0.500 | 0.00 | 0.01 | 0.00 | 0.00 | — | -0.0020 | — | — |

Medijana jaza (tabela iznad) je uslovna na izvodljivost; jaz je normalizovan kontinualnim OPF normalizatorom r, koji nije sertifikovani optimum (negativni jazovi su dozvoljeni). θ = 0,05 znači pet procentnih poena razlike očekivanog skora pobede, ne 5% ubrzanja. Bootstrap: 20.000 ponavljanja, nezavisno uzorkovanje semena unutar ćelije, jednake težine ćelija unutar mreže i mreža, `default_rng(63)`, percentili 2,5/97,5 i 5/95. case30/j4 izuzet unapred (eksplicitan OPF neuspeh); case30/j3 je neizvodljiv u svim granama, a case39/j4 gotovo; te veze ostaju u estimandu.

## Tumačenje (deskriptivno)
Procena je mala i neprecizna: interval uključuje nulu, a 90% interval leži unutar (−0,05; 0,05) samo kao informativni dijagnostik, ne kao ekvivalencija. Znak je isti kao u I56 (θ = +0,0205), ali je veličina manja i estimand se razlikuje. Većina doprinosa dolazi iz dve ćelije (case39|3: d = 0,116; case24_ieee_rts|3: d = 0,069); dve ćelije (case30|3, case39|4) su gotovo potpuno neizvodljive pa daju vezu. Po mrežama: case30 negativno, case39 i case24_ieee_rts pozitivno. Nezavisna reprodukcija (Codex 096, `reproduce_i63d.py`) daje identične ćelijske i globalne procene.

## Poreklo podataka (odstupanje)
Stablo `gadapt/` promenilo se tokom izvršavanja (opt-in kompenzaciona mutacija); prva provera je ispravno stala. Jednakost rezultata pokazana je ponavljanjem uzorka od 128 zadataka (2,5%) na zamrznutom stablu (128/128 identičnih heševa niza poziva i rezultata); `check` i `analyse` izvršeni su uz privremeno vraćeno zamrznuto stablo. Detalji: `research/results/iteration63d/provenance_addendum.txt`. Jednakost nije pokazana za svaki zadatak.

## Ograničenja
Nepotvrdno (I63 STOP); topologije ponovo korišćene; B izabran posle uvida u I61 pilot; kontrast uključuje zasebno podešavanje FX-T po CHT-u; ne identifikuje numerički mehanizam adaptacije.
