# ITERATION64-I2: hibrid GAdapt → CMA-ES na stvarnom diskretnom ORPD-u — specifikacija (zamrznuta komitom PRE uvida u ijedan I64-I rezultat)

Pitanje: da li recept iz E3 (GAdapt 30% budžeta, zatim CMA-ES iz najboljeg rešenja) zadržava svoju prednost na stvarnom infrastrukturnom problemu, uz iste ćelije, semena, budžet i nezavisnu proveru svedoka kao I64-I?
Prior art (nema novine): memetički/hibridni algoritmi (Krasnogor & Smith 2005, 10.1109/TEVC.2005.850260). Hibrid NIJE GAdapt sam. frac = 0,3 je zamrznut iz E3 razvoja (nije podešavan na ORPD).

1. **Pokretanje**: 8 ORPD ćelija iz I64-I, 30 semena (isto seme kao I64-I: 68.000.000 + 1000·c + s), B = 12.000 stvarnih PF, SP skalar f + 1000·V, mreža indeksa R = 17 normalizovana na [0,1], isti `InfraBudget`, isti nezavisni proverivač svedoka. Faza 1: GAdapt-M na mreži (step 1/16) u podbudžetu 3.600 poziva (sa restartima); faza 2: CMA-ES (pycma 4.5.0) iz najbolje tačke faze 1, σ₀ = 0,05, granice [0,1], cilj zaokružuje na najbližu tačku mreže; posle prirodnog kraja restart iz slučajne tačke σ₀ = 0,3. 240 pokretanja ≈ 3–4 CPU-sata.
2. **Upoređenje**: uparivanje po (ćelija, seme) sa arhiviranim I64-I zapisima GAdapt-M i IPOP (isto okruženje `ienv`, isti manifest; proverava se heš I `run.json.gz`).
3. **Hipoteze** (jedna simultana porodica od četiri kontrasta, α = 0,05, 20.000 ponavljanja, seme 68, bootstrap celih uparenih vektora po ćeliji, jednake težine ćelija; α = 0,025 za aktivne, 0,025 za rezervni interval degenerisanih P-kontrasta, kao I-A2): c1 = CVaR(M) − CVaR(H); c2 = P(H) − P(M); c3 = CVaR(IPOP) − CVaR(H); c4 = P(H) − P(IPOP).
   - **H64h1** (hibrid bolji od GAdapt-M u repu bez gubitka izvodljivosti): podržano ako LB(c1) > 0 i LB(c2) ≥ −0,05; suprotno ako UB(c1) < 0 ili UB(c2) < −0,05; inače neodlučeno.
   - **H64h2** (hibrid bolji od IPOP u repu bez gubitka izvodljivosti): podržano ako LB(c3) > 0 i LB(c4) ≥ −0,05; suprotno ako UB(c3) < 0 ili UB(c4) < −0,05; inače neodlučeno.
   Beskonačne vrednosti blokiraju. Prijavljuju se oba ishoda i opisne mere (P, CVaR, medijana G).
4. **Obelodanjivanja**: E/E2/E3 rezultati su poznati; I64-I rezultati NISU viđeni; ORPD κ = 0,60–0,80 (spregnuto) i predikcija P-G1/P-G2 zamrznuta ranije. Okruženje `ienv`. I64-I `run.json.gz` mora biti kompletan pre analize.
