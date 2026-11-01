# Kompatibilnost istorijskih putanja

U [manifestu](../MIGRATION_MANIFEST_2026-11-01.json) je navedeno svih **341** originalnih putanja, novih canonical putanja i identičnih Git blob SHA vrednosti. Ovaj modul ne menja GAdapt.

```sh
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

Alat podrazumevano samo pregleda. `--apply` kreira isključivo nedostajuće lokalne symlink-ove u `research/`, bez prepisa. Ne komitovati ih. GitHub prikaz ostaje uredan; putanje `research/iterationXX*.py` rade samo nakon povratka tih lokalnih aliasa. Python paketski importi `research.iterationXX...` pokušavaju kompatibilno traženje kroz `research/legacy/flat`. To NIJE dokaz da sve istorijske studije rade u novom rasporedu ili novom okruženju.
