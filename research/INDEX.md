# GAdapt research — indeks dokaza

**Stanje 2026-11-01.** Ne menja protokole niti istorijske zaključke.

| Serija | Glavni izvori | Status i ključna granica |
|---|---|---|
| I64-S0 | [Protokol](ITERATION64_PROTOCOL.md), [izveštaj](ITERATION64_S0_REPORT_SR.md) | Rani ECDF GAdapt bolji; DE završna medijana bolja u 14/21 ćeliji |
| I64-E | [Spec](ITERATION64_E_SPEC.md), [izveštaj](ITERATION64_E_REPORT_SR.md) | 12k fizičkih poziva, pomeraji/transformacije; CMA porodica jača u agregatu |
| I64-E3 | [Spec](ITERATION64_E3_SPEC.md), [izveštaj](ITERATION64_E3_REPORT_SR.md) | Fiksni 30/70 hibrid; mešani rezultat, ne nova metoda |
| I64-R | [Izveštaj](ITERATION64_R_REPORT_SR.md) | Izolovana ortogonalna osetljivost GAdapt-a |
| I64-A | [Izveštaj](ITERATION64_A_REPORT_SR.md) | Ablacija: GAdapt faza korisna za konkretan hibrid |
| I64-I | [Izveštaj](ITERATION64_I_REPORT_SR.md) | ORPD izvodljivost; razlike prema CMA neodlučene |
| I64-I2 | [Izveštaj](ITERATION64_I2_REPORT_SR.md) | Hibrid nije potvrđeno bolji na ORPD-u; rep lošiji od IPOP |
| I64-C/N | [C](ITERATION64_C_REPORT_SR.md), [N](ITERATION64_N_DEV_NOTE_SR.md) | Negativno/neodlučeno; ne ponavljati radi pozitivnog rezultata |
| I65 | [Prior art](ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md), [protokol](ITERATION65_DRAFT_PROTOCOL_SR.md), [gate](ITERATION65_INSTRUMENTATION_GATE_REPORT_SR.md) | **DRAFT / NOT_RUN** |

## Kako čitati rezultate
Stagnacija nije uspeh; `optimizer.success` nije potvrđena izvodljivost. Primarno
porediti stvarne evaluacije. Za infrastrukturu proveriti ograničenja, trošak i
fallback. [PHD_PROGRESS](PHD_PROGRESS.md) ima najnoviji plan.
