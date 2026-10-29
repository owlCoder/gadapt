# ITERATION63: replikacija H56a, kvalitet pri fiksnom budžetu — izveštaj (generisan iz arhive)

Protokol: [ITERATION63_PROTOCOL.md](ITERATION63_PROTOCOL.md) (v2, zamrznut `7c1f698`); beleške: [ITERATION63_PRERUN_NOTES.md](ITERATION63_PRERUN_NOTES.md); driver `research/iteration63_replication.py`.

## Ishod: KONAČAN STOP u fazi `power`

STOP: power confirmation or null/equivalence calibration failed (§6); final

H63 NIJE ocenjena (STOP ne daje zaključak o H63; grana teze „I63 STOP“).

Publikovane faze: gate, normalizers, fxt, rehearsal, power.

## FX-T kalibracija
Izabrano: SP [0.75, 0.1, 0.05], FR [0.75, 0.1, 0.05]; pokretanja 972, ponavljanja 0.

## Razvojna proba: prošla = True

| mreža | kompletno j0/j1 | min izvodljivih po grani | ne-veze FR/SP | d≠0 | var(d) | prošla |
|---|---|---|---|---|---|---|
| case30 | {'0': 20, '1': 20} | 20 | {'FR': 14, 'SP': 12} | 14 | 0.1250 | True |
| case39 | {'0': 20, '1': 20} | 19 | {'FR': 36, 'SP': 34} | 26 | 0.4319 | True |
| case24_ieee_rts | {'0': 20, '1': 20} | 20 | {'FR': 29, 'SP': 29} | 22 | 0.3225 | True |

## Snaga
izabrani n = 160, potvrda = True, kalibracija = False, prošla = False.

### Kalibracija (1000 simuliranih eksperimenata; kriterijum: Wilsonova gornja granica stope pogrešnog zaključka ≤ 0,05)

| varijanta i cilj θ | pozitivan | negativan | ekvivalentan | gornja granica (poz / neg / ekv) | prolazi |
|---|---|---|---|---|---|
| pooled|+0.05 | 918 | 0 | 52 | 0.933 / 0.004 / 0.068 | False |
| pooled|+0.00 | 24 | 33 | 910 | 0.035 / 0.046 / 0.926 | True |
| pooled|-0.05 | 0 | 909 | 58 | 0.004 / 0.925 / 0.074 | False |
| j0|+0.05 | 889 | 0 | 49 | 0.907 / 0.004 / 0.064 | False |
| j0|+0.00 | 28 | 29 | 890 | 0.040 / 0.041 / 0.908 | True |
| j0|-0.05 | 0 | 910 | 41 | 0.004 / 0.926 / 0.055 | False |
| j1|+0.05 | 949 | 0 | 49 | 0.961 / 0.004 / 0.064 | False |
| j1|+0.00 | 29 | 25 | 940 | 0.041 / 0.037 / 0.953 | True |
| j1|-0.05 | 0 | 947 | 50 | 0.004 / 0.959 / 0.065 | False |

Pali su samo kriterijumi lažne ekvivalencije na granicama θ = ±0,05. Na granici ekvivalencije stopa pogrešne ekvivalencije ravna je veličini testa (nominalno 5%), pa zahtev da Wilsonova gornja granica ne pređe 0,05 sa 1000 simulacija veoma retko biva ispunjen (približno 2,1% simulacionih serija pri stvarnoj veličini 5%); njegov neuspeh je osobina zamrznutog pravila, ne podatak o H56a. Pravilo se ne ublažava naknadno (§6).


## Ograničenja
Ponovno korišćene topologije; B = 12.000 izabran posle uvida u I61 razvojne medijane (pilot); kontrast uključuje zasebno podešavanje FX-T po CHT-u; estimand ≠ vreme dostizanja H56a; nema tvrdnje o novoj metodi.
