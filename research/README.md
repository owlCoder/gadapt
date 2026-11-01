# GAdapt research — početna stranica

**Status: 2026-11-01.** [Istraživački handoff](PHD_PROGRESS.md) i [obavezna pravila](../AGENTS.md) imaju prednost. Stara merenja nisu prepravljana niti ponovo pokretana.

## Navigacija

- [**Studije po iteracijama (I02–I65)**](studies/) — protokoli, izveštaji, testovi i kod, sortirani po iteracijama.
- [**Sirovi rezultati**](results/) — postojeća struktura i hash-evi nepromenjeni; [pravila za podatke](DATA_POLICY.md).
- [**Literatura, novost, negativne hipoteze**](literature/).
- [**Metodologija, doktorski plan, odluke**](overview/) · [Infrastrukturni domeni](domains/).
- [**Istraživački alati**](tools/) · [I64 implementacija](i64/) · [I65 instrumentacija](i65/).
- [**Mentorski sažetak**](MENTOR_SUMMARY_2026-10-28_SR.md) · [beleške sa sastanka](MENTOR_MEETING_NOTES_SR.md).
- [**Codex recenzije**](codex/) · [Rad za TELO](paper_integrity_audit/) · [Teza](thesis/).
- [**Istorijski izvori**](legacy/) · [Kompatibilnost](compat/) · [Kompletan manifest migracije](MIGRATION_MANIFEST_2026-11-01.json).

## Sadašnje naučno stanje

- I64-S0/E/E3/A/R/I/I2 već testirani i dokumentovani; nalaz o rotacijskoj osetljivosti i nepouzdanom prenosu sintetičkog hibrida na ORPD ostaje ograničen na testirane ćelije.
- **I65 = DRAFT / NO-FREEZE / COCO f21/f24 NOT_RUN.** Instrumentacioni testovi nisu dokaz uspeha optimizatora.
- Nema potvrde originalne metode, univerzalne superiornosti ili industrijske spremnosti.

## Kompatibilnost nakon fizičke migracije

Iz korena je premešteno **341 istorijskih fajlova** u [legacy/flat](legacy/flat/) bez promene njihovog Git blob SHA. Za navigaciju su izložene simboličke veze u studijama, literaturi i alatima. Stare eksplicitne putanje se ne nalaze u čistom checkout-u. Za reprodukciju starih CLI komandi u lokalnom clone-u:

```sh
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

Prva komanda je dry-run. Druga pravi samo nedostajuće symlink-ove, bez prepisivanja podataka. **Puna regresiona kompatibilnost istorijskih skripti nije još demonstrirana.** Ne pokreći skupe testove bez istraživačkih kapija.
