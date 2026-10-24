# I58 (PREDLOG, napisan PRE rezultata I56): validacija ugrađenog `constraint_handling` u GAdapt-u na svežim mrežama

**Status:** predlog 2026-10-24, dok I56 radi (nijedan I56 test rezultat nije viđen). Povod: Codex 034 — najjači
napad komisije je „gde je stvarno poboljšanje GAdapt-a za infrastrukturu?“; I56 meri interakciju, ne korist.

## Pitanje (konfirmatorno)
Da li GAdapt sa ugrađenim opt-in `constraint_handling` (preporučena tehnika, izabrana unapred definisanim pravilom
iz I56) dostiže izvodljiv cilj brže od uobičajene upotrebe GAdapt-a (korisnikova statička kazna u skalarnoj funkciji
troška), na mrežama i semenima koje ni I56 ni I57 nisu videli?

## Pravilo izbora preporučene tehnike (zamrznuto pre I56 rezultata)
Među I56 AD-N granama {AP, FR, EC} (SP je kontrola) bira se ona sa najmanjim jednako ponderisanim srednjim T u I56
testu; veze → FR. Biblioteka koristi svoje podrazumevane konstante (iste kao I56) i f_ref iz početne populacije
(razlika od I56, gde je f_ref bio OPF — navesti).

## Instance (sveže, sa stvarnim termičkim ograničenjima)
case30 (8 kontrola, 41 ograničena grana), case39 (22, 46), case24_ieee_rts (39, 38), case300 (190, bez termike —
skala). Isti merni model (I56 merilo, PG iz OPF scenarija), R = 17; 3 nova scenarija po mreži (load_factor 0,95 /
1,00 / 1,05, spread 0,1, scenario_seed 301–303). Instanca kojoj OPF ne uspe izuzima se.

## Grane
- **G0:** GAdapt podrazumevano, skalar f + 1000·V (uobičajena upotreba; isto kao I56 SP/AD-N).
- **G1:** GAdapt sa `constraint_handling=<preporučena>` (biblioteka, posle primene patch-a v4).
- Kontekst (opisno): CMAwM/FR i SciPy DE/FR (I57 adapteri), nasumična pretraga.
- Budžeti: 3000 i 10.000 AC proračuna; 15 semena (namena 6).

## Ishod i analiza
T (vreme do cilja, kao I56) sa ciljem iz NEZAVISNIH referenci: najbolje izvodljivo iz referentnih pokretanja SVIH
metoda (G0, G1, CMAwM, DE; 30.000 poziva, 2 semena) — ne samo GAdapt (ispravka I57 ograničenja). Primarno:
θ = jednako ponderisan srednji T(G1) − T(G0) pri budžetu 3000; stratifikovani bootstrap (ćelije mreža × scenario),
20.000, seme 58; **H58 potvrđena ako je 95% interval potpuno ispod 0.** Sekundarno (opisno): budžet 10.000,
izvodljivost, najbolji izvodljiv gubitak, vreme izvršavanja, poređenje sa CMAwM/DE.

## Nezavisna provera
Vraćena rešenja G1 se ponovo proveravaju samostalnim `runpf` pozivom (izvan biblioteke); paket i skripta se
zamrzavaju heševima; drugo izvršavanje istog paketa u čistom okruženju (ponovljivost niza poziva).

## Budžet
(2 GAdapt + 3 kontekst) × 12 instanci × 15 semena × (3000 + 10.000) ≈ 11,7 miliona + reference ≈ 2,9 miliona PF
poziva ≈ 12 CPU-sati.
