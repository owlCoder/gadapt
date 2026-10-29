**Sažetak treba revidirati pre slanja.** Arhivirane procene i intervali podržavaju ishode: S0 **podržano**, E **suprotno**, E2 **suprotno/neodlučeno/suprotno**, E3 **podržano/suprotno/neodlučeno**. Bootstrap nisam ponavljao. Ništa nije menjano.

Oznake: [P = poglavlje](/Users/danijel/Desktop/gadapt/research/thesis/CH8_MENTOR_BENCHMARK_SR.md), [M = sažetak](/Users/danijel/Desktop/gadapt/research/MENTOR_SUMMARY_2026-10-28_SR.md), [S0](/Users/danijel/Desktop/gadapt/research/ITERATION64_S0_REPORT_SR.md), [E](/Users/danijel/Desktop/gadapt/research/ITERATION64_E_REPORT_SR.md), [E2](/Users/danijel/Desktop/gadapt/research/ITERATION64_E2_REPORT_SR.md), [E3](/Users/danijel/Desktop/gadapt/research/ITERATION64_E3_REPORT_SR.md), [G](/Users/danijel/Desktop/gadapt/research/ITERATION64_G_SPEC.md). Brojevi označavaju redove; navodnici daju tekst zamene.

- **M7–8; P15**, „nepromenjen“, „jedina novina“, „sve brojke“: „S0 zadržava mentorove funkcije i konfiguracije, uz instrumentaciju, seedovanje DE-a i obelodanjena odstupanja. Primarni kontrasti nezavisno su reprodukovani; semena 1–3 bila su prethodno viđena.“

- **P11; M14–15**, računovodstvo i zaključak o pristrasnosti: „S0 beleži približno 32/64/96 poziva po generaciji za GAdapt/PyGAD random/adaptive. Na pojedinim 20D ćelijama DE troši oko 36.000, GAdapt oko 19.000 poziva. Generacije zato nisu uporediva jedinica troška.“ Adaptive nije još 2× random; uzročna tvrdnja o preciznosti nije proverena.

- **P17**, netačno prepričano H64a: „H64a prolazi ako su svi ΔA pozitivni prema simultanim granicama, ili uz najviše jedan izuzetak prema kojem je ΔM pozitivan. S0 prolazi prvom granom.“

- **P19; M12–13**, dve ćelije i „glatke funkcije“: „GAdapt ima niži ponderisani prosek ćelijskih završnih medijana g. Dve navedene ćelije nose prednost prema DE-u; ovo objašnjenje ne važi za sva poređenja.“ Brisati generalizaciju numeričke preciznosti na glatke funkcije; postoje protivprimeri.

- **Ista mesta**, ćelijski odnosi: „Post hoc, opisno: DE ima nižu završnu medijanu u 14/21 ćelija, GAdapt veći A u 17/21; pri najviše 12.000 poziva odnos medijana je 10:10:1.“

- **S0:19; E:21 i agregatni nazivi kolona**, „medijana“: koristiti „ponderisani prosek ćelijskih medijana normalizovanog jaza“. Agregatni CVaR označiti „ponderisani prosek ćelijskih CVaR₀,₉(L)“.

- **P27; M19**, „dokazano efikasniji“: „Prema simultanim intervalima E, CMA, IPOP i BIPOP imaju veći ponderisani A od GAdapt-M; GAdapt-M ima veći A od oba PyGAD-a, DE-a i (1+1)-ES.“

- **P29; M19**, „najbolji od svih devet“: „Post hoc, uz jednake težine ćelija, GAdapt-M ima CVaR 0,0033 na orig/shift i 0,0386 na rot; preset ima niže orig/shift vrednosti, 0,0031/0,0032.“ Ostale navedene neponderisane brojke odgovaraju E.

- **P29**, „najniži… zato što“: „Ponderisani agregat 0,0117 najniži je među devet konfiguracija; dve trećine težine pripadaju orig/shift varijantama.“

- **P29, M19; G3**, zavisnost od osa, separabilnost i infrastruktura: „Opisne razlike prate transformacije; različiti pomeraji ne izoluju efekat rotacije. Osno poravnanje ne podrazumeva separabilnost; nalaz ne ustanovljava prednost na klasama infrastrukturnih problema.“

- **P31; M19**, „ne menja“, „ne pomaže“: „H64b nije podržana; procenjeni CVaR raste sa 0,0117 na 0,0121.“

- **P35**, objašnjenje krosoverom: „E2 proverava da li zamena krosovera poboljšava unapred definisane ishode.“

- **E2:56; M20**, značajnost „na svim varijantama“: „A je niži pod rotacijom i na objedinjenom orig+shift podskupu, uz simultane intervale ispod nule; pojedinačne varijante opisno prate isti smer.“ Poslednju mehanističku rečenicu E2 zameniti: „Uzrok neuspeha nije izolovan.“

- **P39; E3:67**, „industrijski recept“: „empirijska provera hibrida na klasičnim funkcijama“.

- **P41**, „učenje koordinata nije pomoglo“: „Razvojni pokušaj GAdapt-PCA na četiri rotirane ćelije i tri semena nije dao dovoljnu korist; nije formalno testiran.“

- **M23**, „najbolji praktični recept“, „jaz zatvoren“: „E3 poboljšava rotacijske ishode prema GAdapt-M; H64g1 je podržana, H64g2 suprotna, H64g3 neodlučena. Ukupni kriterijum nije ispunjen.“

- **P43; M23**, „najniži“, „blizu IPOP-a“: „Post hoc: među šest prikazanih konfiguracija hibrid ima najniže agregate CVaR/M, 0,0070/0,00293; A je 0,7511 prema IPOP-ovih 0,7699. Neinferiornost nije potvrđena.“

- **P43**, pripisivanje doprinosa fazama: „Bez ablacija nije utvrđen zaseban doprinos GAdapt i CMA faze.“

- **E3:67**, „osim GAdapt-M“: „Opisno, hibrid ima viši orig/shift CVaR od GAdapt-M i preseta, a niži od prikazanih CMA varijanti; pod rotacijom A zaostaje za IPOP-om.“

- **E2/E3:20**, „ćelije jednako ponderisane“: „Funkcije imaju jednake težine, dimenzije jednake težine unutar funkcije.“ **E3:1:** „ITERATION64-E3“.

- **P45–47**: „I64-I je zamrznut dopunom I-A2, komit a17f7dc; rezultati nisu kompletirani. Industrijska spremnost nije ustanovljena.“

- **P51; M27**, „preset stabilnosti“, „inženjerski ispravne“: „Implementirane su opcione funkcije sa dokumentovanim proverama; njihova opšta pouzdanost nije ustanovljena.“ **M26:** „Navedene studije ne ustanovljavaju novu metodu; broj odbačenih kandidata zahteva zaseban trag izvora.“

- **G1,3–4**, „jeftina“, „operativna“ dijagnostika: „κ je kandidat za dijagnostiku; računanje zahteva 20–30·(2D²+1) poziva. ORPD arhiva beleži ukupno 147.060 poziva.“ **G4:** „κ opisuje procenjene Hesijane u uzorkovanim tačkama; ne dokazuje globalnu separabilnost.“

- **G7–8,12:** „Post hoc: korelacije su −0,389/−0,523; navedene p-vrednosti su nominalne, uz zavisne ćelije. Za κ≥0,01 udeli pobeda su 14,3% po A i 11,9% po CVaR; za κ≥0,3 CVaR udeo je 16,7%.“

- **G11:** „κ je između 0,5976 i 0,8020; sedam od osam vrednosti je ≥0,6.“ **G14–15:** „Prag 6/8 proverava konzistentnost; zavisne ćelije ne opravdavaju nezavisni sign-test. Pozitivan ishod ne validira κ kao pravilo izbora algoritma.“

**Post hoc oznake nisu potpune:** dodati ih S0 §4b i odgovarajućem delu §8, E §4b–4c, prenetim analizama u P/M i E3 §2b. Planirane opisne mere ne treba automatski nazivati post hoc.

Pre slanja nedostaju ove korekcije, obelodanjivanje S0 probe u sažetku, ažuran status I/I2 i odgovor nezavisne provere #89. Kao jasno označeno međustanje, sažetak ne mora čekati završetak I/I2. Industrijsku spremnost ni njihov završetak sam po sebi neće dokazati.