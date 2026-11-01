# I65 — migracioni kompatibilni gate, 2026-11-01

**Status: DELIMIČNI GO za alat za restauraciju; NO-GO za proglašavanje potpune istorijske regresije.** Nema novog optimizacionog benchmarka, promene GA default-a, COCO pokretanja ili promene zamrznutih studija.

## Obuhvat

1. GitHub baza: pre migracije `0e7cacda2040643a41ff923dd2a71ffbc3f5dfef`, posle migracije `92a31c109edf60810e383833bac1bf8d7430d603`. Provereno: 341 starih root fajlova fizički premešteno sa **identičnim Git blob SHA**, 2.717 starih sirovih izlaznih fajlova nepromenjeno; 64 generisana `__pycache__` fajla uklonjena.
2. **Kritična statička revizija GitHub izvora:** I56 `iteration56_cht_study.py`, I58 `iteration58_validation.py`, I61 `iteration61_replication.py` i I63 `iteration63_replication.py` zasnivaju `HERE` i/ili `REPO` na `os.path.abspath(__file__)`; `OUT` u I56/I61/I63 zavisi od lokacije. Pozivanje direktno iz `research/legacy/flat/` ili `research/studies/iNN/` **nije** zamena za stare CLI putanje.
3. **Korekcija:** `research/__init__.py` više ne dodaje implicitno `legacy/flat` u import putanju. Pre aktivnog istorijskog importa potrebna je **eksplicitna** opt-in restauracija starih root symlink-ova.
4. Restaurator `research/compat/restore_legacy_paths.py`: preflight svih 341 navoda *pre* stvaranja prve veze, opcioni Git blob SHA audit, fail-closed pri korisničkom postojećem fajlu, konfliktnoj simboličkoj vezi ili pogrešnom SHA, idempotentnost. `research/.gitignore` sadrži samo 341 tačno određen historijski alias i održava Git status preglednim.
5. **Lokalni mali sintetički testovi** (Python stdlib, Git, privremeni direktorijumi): `python -m unittest discover -s research/compat -p test_migration_compat.py -v` → **9/9 PASS**. Testiraju dry-run, apply+idempotenciju, neprepisivanje korisničkih podataka, pogrešan symlink, nepostojeći canonical, dvoprolazni SHA preflight, duplirani alias, originalni `HERE`/`REPO` i čitanje GitHub navigacionog simlinka. Nisu testovi istinitih I41/I63 objektiva.
6. **Ponovljen lokalni I65 instrumentacioni test paket**: `python -m pytest -q -rx research/i65/test_*.py` → **54 passed, 3 xfailed** (I64 failed attempt undercount, mutable input snapshot after evaluation, original stagnation timestamp guard). Nema promene brojeva; ovo NIJE provereno unutar kompletnog novog repozitorijuma.
7. Sadržaj oba nova koda/tes­ta je nezavisno potvrđen Git blob SHA-om između lokalnog prolaznog testa i GitHub staging-a: `restore_legacy_paths.py` = `6908ce90ec1edb73ed7821f4ba8820617213bace`; `test_migration_compat.py` = `1d369d0f91b2b674a34403c3416d7e3d8aa7e54a`.

## Sledeća stvarna stopa / preostali blokatori

Na trenutnom okruženju nema pune lokalne Git klonirane biblioteke, niti instaliranih `cocoex`, `cma`, `gadapt`; konektor omogućava čitanje i pisanje GitHub izvora, ali ne i lokalni checkout za izvršavanje celog projekta. Zato **nisu** izvršeni: `python research/compat/restore_legacy_paths.py --apply --verify` nad stvarnih 341 originala, realni `research/test_iteration41_*.py`, `research/test_iteration63_replication.py`, I64 skripte ili originalni GA import-testovi u tom checkout-u. Eksplicitni `NOT_TESTED` je deo rezultata.

Završni realni gate na računaru sa punim klonom i zaključanim okruženjem, *bez* run-ova velikog budžeta:

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
python -m pytest -q research/test_iteration41_*.py
python -m pytest -q research/test_iteration63_replication.py
python -m pytest -q research/i64/test_e_common.py research/i64/test_e_algos.py
```

Prelazak na istraživački `FREEZE` ostaje blokiran: `I65 novelty not established`, integracioni GAdapt/CMA/COCO gate `NOT_TESTED`. Za današnji gate ishod je **instrumentacioni lokalni GO, ukupni regresioni NO-GO dok pune provere nisu izvršene**.
