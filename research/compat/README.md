# Kompatibilnost sa starim istraživačkim putanjama

**Bezbednosni gate 2026-11-01.** Migrirano je 341 istorijski root fajl bez promene sadržaja. Izvorni Git blob SHA i kanonska putanja nalaze se u [MIGRATION_MANIFEST](../MIGRATION_MANIFEST_2026-11-01.json). Simboličke veze u studies/, tools/ i literature/ **služe za pregled**, ne za pokretanje istorijskih CLI eksperimenata: moduli I56/I58/I61/I63 izračunavaju HERE, REPO i OUT iz __file__.

## Opt-in obnova

Na stvarnom lokalnom checkout-u u korenu repozitorijuma:

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

Prva proverava samo izolovane sintetičke slučajeve, druga je readonly preflight sa Git blob proverom svih 341 izvora, a treća pravi stare **root** symlink putanje. Ako ima bilo kakvog SHA, duplikata, nedostajućeg ili korisničkog fajl konflikta, preflight staje bez kreiranja ijednog symlink-a. Postojeće validne veze se ne prepisuju. Precizno imenovane veze ignorisane su kroz research/.gitignore.

**Ne pokretati** istraživačke skripte iz `research/legacy/flat/` ili `research/studies/iNN/`; za reprodukciju koristiti stare `python research/iterationNN_....py` putanje tek nakon restauracije. Python `research.iterationNN_...` import pre restauracije namerno NE koristi automatski fallback. Svi originalni zamrznuti izvori ostali su neizmenjeni.

## Šta i dalje nije potvrđeno

Potpuna regresija istorijskih I41, I56, I61, I63 i I64 studija u stvarnom klonu **nije** pokrenuta. Sintetički testovi ne dokazuju fizičku optimizacionu korektnost. [Izveštaj gate-a](../ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md) sadrži testne granice i komande za narednu nezavisnu proveru.
