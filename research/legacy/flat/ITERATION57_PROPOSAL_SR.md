# I57 (PREDLOG, napisan PRE rezultata I56): GAdapt naspram spoljnih metoda na istom diskretnom ORPD-u

**Status:** predlog 2026-10-24, dok I56 radi (nijedan I56 test rezultat nije viđen). Protokol se zamrzava tek
posle Codex recenzije. Svrha: spoljni kontekst koji I56 namerno nema (§9 I56) — recenzent će pitati „koliko je
GAdapt dobar u apsolutnom smislu na ovom problemu?“.

## Pitanje
Pri istom budžetu AC proračuna, gde je GAdapt (podrazumevani i najbolja I56 grana — izbor se zamrzava UNAPRED
pravilom ispod, ne posle gledanja I57) u odnosu na jake metode za mešovito-celobrojne crne kutije, na istim
instancama, metama i ishodu T kao u I56?

## Poredbeni metodi (unapred)
- CMA-ES sa marginom (Hamano i sar. 2022, GECCO; DOI proveriti), paket `cmaes` 0.13.1 (`CMAwM`), podrazumevana
  podešavanja, celobrojni indeksi mreže.
- SciPy `differential_evolution` sa `integrality` (indeksi mreže), podrazumevano, `polish=False` (I52: poliranje
  troši budžet i odbacuje bolju tačku).
- Nasumična pretraga na mreži (donja kontrola).
- Opciono, ako postoji održavana implementacija koja prolazi smoke-test: L-SHADE / jDE (Tanabe 2024 preporuke).
- Ograničenja kod spoljnih metoda: isti FR skalar m iz I56 (Deb-ova pravila, skalarno izražena) i, posebno, SP.

## Pravilo izbora GAdapt grane (zamrznuto pre I56 rezultata)
1. GAdapt podrazumevano + SP (uobičajena upotreba).
2. GAdapt grana sa najmanjim srednjim T u I56 TEST podacima — dozvoljeno jer I57 koristi NOVA semena (namena 5)
   i ne menja I56 zaključke; prijavljuje se kao „izabrano na I56“ (rizik optimističnog izbora navesti).

## Instance, ishod, analiza
Iste test instance i reference kao I56 (L* iz I56 `test_ref`), novi tok semena; 10 semena; T kao u I56; poređenje
parova (metod − GAdapt) sa istim stratifikovanim bootstrap-om; bez tvrdnje o „najboljem“ algoritmu izvan ovih
instanci.

## Budžet
~ (3 + 2 GAdapt) metode × 30 instanci × 10 semena × 3000 ≈ 4,5 miliona PF poziva ≈ 4 CPU-sata.
