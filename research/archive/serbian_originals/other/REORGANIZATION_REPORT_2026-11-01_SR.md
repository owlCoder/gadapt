# Reorganizacija research/ — 2026-11-01

**Status:** nedestruktivna Git migracija putanja; ovo nije nova naučna studija.

| Mera | Pre | Posle |
|---|---:|---:|
| Fajlovi direktno u `research/` | 379 | 38 pre dodatnih indeksa |
| Istorijski fajlovi premešteni bajt-identično | — | 341 |
| Pogledi simboličkim vezama, po temi/iteraciji | — | 341 |
| Generisani `__pycache__` artefakti uklonjeni iz Git-a | 64 | 0 u `research/` |
| Originalni sirovi rezultati u `results/` | 2717 | 2717 nepromenjenih |

**Garantovano proverljivo na nivou Git stabla:** canonical premešteni fajlovi koriste iste blob SHA kao stari. Sirovi rezultati i aktivni I64/I65 izveštaji nisu migrirani niti ponovo računati. Mapa sa svim izvornim i završnim putanjama: [MIGRATION_MANIFEST](MIGRATION_MANIFEST_2026-11-01.json).

**Ograničenje:** direktni istorijski `research/<ime>.py` ulazi više nisu dostupni bez lokalnog `compat --apply`. To je namerna opt-in kompatibilnost radi čistog korena, ali nije obavljena puna regresija. Stari tekstualni linkovi ka eksplicitnim root putanjama i arhivski manifesti mogu zahtevati kompatibilno okruženje. Nisu preslikavani stari zamrznuti heševi u nove istoriografske tvrdnje. Ne pokretati skupe CI ili konfirmatorne eksperimente tokom migracije.

**Sledeći gate:** nezavisni offline replay kritičnih i64/i63 skripti sa zaključanim verzijama; tek posle toga razmatrati dalju istraživačku implementaciju I65.
