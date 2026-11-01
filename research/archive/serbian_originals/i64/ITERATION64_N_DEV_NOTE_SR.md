# I64-N razvojna sonda (EKSPLORATIVNO, nije preregistrovano): zavisnost GAdapt-a od proizvoljnog redosleda oznaka nominalnih promenljivih

Potts-slučaj: 10 promenljivih × 8 kategorija, 20 grana, B = 3000; 12 problema × 16 preimenovanja × 4 semena po metodi. Jaz = (best − ref)/|ref|, ref = najbolja nađena vrednost po problemu (nije sertifikovani optimum).

| metoda | srednji jaz | std između preimenovanja (po problemu, prosek) | std semena unutar preimenovanja (prosek) | odnos između/unutar |
|---|---|---|---|---|
| gadapt_M | 0.0896 | 0.0338 | 0.0609 | 1.11 |
| gadapt_free | 0.0876 | 0.0331 | 0.0607 | 1.09 |
| hillclimb | 0.1590 | 0.0460 | 0.0921 | 1.00 |
| random | 0.3789 | 0.0267 | 0.0501 | 1.07 |

Odnos između/unutar ≈ 1 znači da preimenovanje ne menja ishod više od šuma semena (invarijantnost); znatno > 1 znači da proizvoljan redosled oznaka utiče na rezultat.
