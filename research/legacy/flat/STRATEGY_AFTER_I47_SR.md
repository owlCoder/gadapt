# Strateški presek posle I42–I47 (23. oktobar 2026)

## Šta je sada utvrđeno (preregistrovano, jednim pokretanjem po eksperimentu)
1. **Binarni izbor ruta (I43–I46, 24 topologije):**
   - GAdapt je značajno lošiji od (1+1)-EA na 14 od 18 topologija i nije bolji ni na jednoj;
   - lošiji je i od fiksnog udžbeničkog GA-a (5/6);
   - nijedna pojedinačna GAdapt opcija ne objašnjava deficit.
2. **Kontinualni infrastrukturni problemi (I5 i I47):**
   - CMA-ES je pri istom budžetu bolji od GAdapt-a na IEEE14 naponima (12/12);
   - na AC dispečingu (MATPOWER 14/30/39/57/118) CMA-ES je **3–5 redova veličine** bliži najboljem rešenju.
3. **Mehanizam (eksplorativno + I46/I47):** GAdapt-ovi mehanizmi raznovrsnosti sprečavaju intenzifikaciju oko
   najboljeg rešenja. Ispravke invarijantnosti i intenziteta mutacije tu slabost ne rešavaju.
4. **Ispravke biblioteke (opt-in, podrazumevano bit-identično):**
   - `probe_cost_function`;
   - `strict_mutation_decision_variable_limit`;
   - `columnar_diversity_metric="linear"`.
5. **Artefakt u ranijem radu:** validator troši 2 skrivene evaluacije, a u I39 je verovatno davao „trivijalno
   najbolje rešenje“.

## Šta NIJE utvrđeno
Nijedna originalna PhD metoda. Invarijantnost, intenzifikacija, (1+1)-EA, memetički hibridi i PX su poznati.

## Opcije
- **A. Konsolidacija:** rigorozna dijagnostička studija samoadaptivnog GA-a na infrastrukturnim problemima, uz
  jednake budžete, skrivene evaluacije, invarijantnost, deficit intenzifikacije i preregistraciju. Doprinos je
  metodološki i empirijski, a ne nova metoda. Bezbedno, odmah izvodljivo, poglavlje teze ili rad.
- **B. Praktično zatvaranje razlike:** opt-in hibrid (GAdapt raznovrsnost + lokalna intenzifikacija, npr. CMA-ES ili
  (1+1) faza posle stagnacije). Verovatno velik praktičan dobitak, ali **novost nije utvrđena** (memetički i hibridni
  algoritmi su poznati: Krasnogor i Smith 2005, [10.1109/TEVC.2005.850260](https://doi.org/10.1109/TEVC.2005.850260)).
- **C. Falsifikacija GAdapt-ovog razloga postojanja:** da li GAdapt-ova raznovrsnost donosi prednost na **multimodalnim**
  infrastrukturnim problemima, pri istom budžetu protiv CMA-ES-a sa restartima (IPOP) i DE-a? Primer je ekonomski
  dispečing sa valve-point efektom, uz proverene javne podatke. Ako izgubi i tu, odgovor za A je jasan; ako pobedi,
  to je prva pozitivna i braniva tvrdnja o GAdapt-u.
- **D. Razgovor sa mentorom** pre daljeg ulaganja, uz ovaj presek kao materijal.

**Preporuka:** C (jedan preregistrovan eksperiment), pa A kao poglavlje bez obzira na ishod. B samo kao opt-in
praktična funkcija, uz eksplicitnu napomenu da nije PhD doprinos.
