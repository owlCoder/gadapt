# Sažetak za mentora (2026-10-24, kasno)

Stanje posle konfirmatornih studija I58, I60, I59 (sve zamrznute pre svojih podataka; nezavisne provere rešenja; svi
izveštaji u `research/ITERATION5*_REPORT_SR.md`, `ITERATION60_REPORT_SR.md`):

- **Praktično ubrzanje ugrađenih tehnika za ograničenja nije potvrđeno: H58/H60/H59 = N/N/nedostupno.**
  FR (I58): θ = −0,014 [−0,035; +0,006]; ε (I60): θ = −0,011 [−0,035; +0,012]; oba intervala obuhvataju nulu.
  I59 (telekom) zaustavljen unapred zadatim razvojnim pravilom (NO-GO) — to nije negativan potvrdni rezultat.
- **H56a (interakcija adaptacija × tehnika za ograničenja) je mali, lokalni nalaz** (θ = +0,0205 [0,0020; 0,0396],
  praktično case14). Njegova konceptualna replikacija **I61** je zamrznuta pre ovih rezultata i radi (≈ 1 dan
  računanja; realan ishod je i STOP zbog nedovoljne snage).
- **I57 (opisno):** CMA-ES sa marginom brži od GAdapt-a na case14 (R = 17/33); GAdapt jedini uvek nalazi izvodljivo
  rešenje na case57. Konkurentnost GAdapt-a nije ustanovljena i teza je ne tvrdi.
- **Najozbiljniji kandidat za samostalnu okosnicu doprinosa je revizija integriteta evaluacija** (alat + studije
  I49–I52/I55 na 21 biblioteci, prenos na AC dispečing); traži zasebno centralno poglavlje i strogu procenu originalnosti
  integracije i validnosti detektora.
- **Potrebna je eksplicitna procena dovoljnog originalnog doprinosa za doktorat**: količina eksperimenata, urednost
  postupka (preregistracija, nezavisne provere) i ispravan softver (opt-in `constraint_handling` u GAdapt-u) to sami ne
  garantuju.

Biblioteka: `constraint_handling` (FR, ε, kazna, adaptivna kazna) ostaje opt-in, podrazumevano ponašanje bit-identično
(heš niza poziva), bez preporuke zasnovane na brzini. Revizija tvrdnji u poglavljima teze: Codex 075 (uneto).
