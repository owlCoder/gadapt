# Istraživački podaci i pravila organizacije

Dodatak 2026-11-01: **nedestruktivna organizacija**.

1. Istorijske `ITERATION*` specifikacije, skripte i sirove podatke ne premeštati: veze, manifesti i heševi zavise od starih putanja. Originalni veliki `research/README.md` arhiviran bajt-identično u `research/archive/`.
2. Nove studije: `research/iNN/` kod/testovi, `research/ITERATIONNN_*` protokoli i izveštaji. Jasni statusi DRAFT, FREEZE, NOT_RUN, GO/NO-GO.
3. Male fixtures i izvodi testova mogu u Git. Velike `.json.gz` i srodne arhive čuvati izvan obične Git istorije sa tačnom lokacijom, SHA-256 i manifestom. Ne rekonstruisati izgubljene izvore.
4. Pre konfirmacije sačuvati/verifikovati verzije biblioteka, semena, instance, evaluacione pozive, izvore i heševe; odvojiti razvojne i held-out podatke.
5. Bez skupih CI workflow-a, destruktivnog čišćenja, menjanja istorije ili izmene `bpzoran/gadapt`. `[skip ci]` na dokumentacionim commit-ovima nije garancija da platforma neće pokrenuti ni jedan workflow.
6. Originalni I65 dokumenti i manifesti sa izjavom „GitHub nije menjan“ ostaju kao istorijske izjave na dan nastanka; upload označiti zasebnim addendum-om.
7. Pre eventualnog masovnog premeštanja napraviti zaseban inventar referenci i plan migracije. Sada zadržati sve stare putanje.
