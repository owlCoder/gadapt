# Istraživački podaci, migracija i reproduktivnost

**Aktuelno 2026-11-01:** istorijski tekst prethodne verzije je u Git istoriji; ovaj tekst dokumentuje izvršenu fizičku migraciju i ima prednost za nove radnje.

1. **Izvršena migracija.** 341 istorijskih root fajlova iz `research/` premešten je bajt-identično u `research/legacy/flat/`. Mapa stare→nove putanje, originalni Git blob SHA i cilj navigacionih simlinkova nalaze se u [manifestu](MIGRATION_MANIFEST_2026-11-01.json). Pregled po iteracijama je u [studies/](studies/). Aktivni I64/I65 dokumenti i sirovi rezultati ostaju na originalnim putanjama.
2. **Nema prepravljanja istorije.** Stari protokoli, izveštaji, zaključci i naučni izvori zadržavaju svoj sadržaj. Bez retuširanja negativnih ishoda, rekonstrukcije izgubljenih podataka ili ponavljanja do pozitivnog rezultata.
3. **Kompatibilnost.** Za istorijske ulazne komande pokrenuti `python research/compat/restore_legacy_paths.py --apply --verify` na lokalnom checkout-u. Ova opt-in procedura pravi samo nepostojeće simlinkove bez prepisa; ne komitovati rekonstruisane linkove. Puna regresija posle migracije još nije demonstrirana.
4. **Rezultati.** [results/](results/) (2.717 praćenih izvora bez generisanih cache fajlova) nije pomeran niti ponovo računat. Ne mešati sirove podatke, probe instrumentacije, razvojne i konfirmatorne serije. Velike arhive čuvati izvan obične Git istorije sa SHA-256, lokacijom i manifestom.
5. **Reproduktivnost.** Pre konfirmacije zamrznuti izvore, verzije, instance, semena, budžet svih stvarnih poziva, optimizacione tragove i pravila validacije. Neuspehe i rezultate `NOT_SOLVED` čuvati jednako kao uspehe.
6. **Novi rad.** Kod i testovi nove iteracije u `research/iNN/`, aktivni protokoli u root `research/ITERATIONNN_*`, zamrznuti dokumenti ne smeju se tiho menjati. Nakon završetka aktivne serije prvo pregledati reference i tek zatim arhivirati.
7. **Bezbednost procesa.** Ne dirati `bpzoran/gadapt`, ne menjati podrazumevano ponašanje GAdapt-a, ne pokretati skupe CI workflow-e automatski. `[skip ci]` nije garancija neaktiviranja svih GitHub Actions.
8. **Posebna poštenost I65.** `DRAFT / NO-FREEZE / NOT_RUN`: instrumentacioni testovi nisu COCO f21/f24 optimizacioni rezultati. Originalne izjave „GitHub nije menjan“ u prethodnom lokalnom paketu označavaju tadašnji istorijski trenutak; kasniji upload/migracija imaju zasebne commit-ove.
