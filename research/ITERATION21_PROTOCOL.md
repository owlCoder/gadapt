# Iteracija 21 — diferencijalna Q osetljivost preostala četiri IEEE118 generatora

**Pre-registracija 21.10.2026 pre svih novih pravih AC poziva iteracije 21.** Samo owlCoder/gadapt:main; originalni upstream bpzoran/gadapt nije menjan. Ovo je deterministički **1-at-a-time** IEEE118 Q-screen, **NIJE** nova GAdapt adaptacija, nema statističkih zaključaka.

## Dokazani polazni fizički status

Originalni početni izvorni IEEE118 PG/VG ima šest generatorskih Q prekoračenja i ukupno **78,0991950173 MVAr** (iteracija 19). I20 preregistrovana jednofaktorska promena **gen BUS103 originalni VG 1.01→0.99 p.u.**, svih 54 PG i drugih VG fiksnih, dala je **stvarno izmeren** potpuno AC-konvergentan ali **neizvodljiv** PF: oba prvobitno uporna Q prekršaja BUS103 i BUS105 su uklonjena, bez P/V/pozitivnog RATE_A prekršaja, a zbir preostalih Q prekršaja je **32,3458076968 MVAr**. Originalni gen #16 BUS34 je ispod QMIN za **12,8270246331 MVAr**, gen #43 BUS92 za **10,9597519466**, gen #9 BUS19 za **6,2741894049**, gen #15 BUS32 za **2,2848417122**. Ovi četiri izvora originalno su **PV bus type2**. Referenca je **samo prethodno arhivirani** rezultat I20 `research/results/ieee118_iteration20_q_sensitivity_8_real_ac_20261021.json`, scenario `gen103_minus`; baseline se **ne** rekalkuliše besplatno.

## Precizno zamrznuti novi eksperimenti

Originalni `pypower.case118()`, originalni BUS69 slack, originalnih 118 bus / 54 aktivna GEN / 186 BRANCH; source P/Q/V/RATE_A/topologija, svi loads, taps i shunts netaknuti. **Svih 54 PG fiksno na izvornim vrednostima.** Gen originalni red#46 BUS103 VG je fiksiran na 0.99 (I20 best screening tačka), ostalih 53 VG na source originalnim vrednostima **osim tačno jednog** od četiri izvorna QMIN prekršajna generatora u svakom scenariju:
- gen **red#16, 0-based 15, BUS34**, originalni VG **0.984**;
- gen **red#43, 0-based 42, BUS92**, VG **0.99**;
- gen **red#9, 0-based 8, BUS19**, VG **0.962**;
- gen **red#15, 0-based 14, BUS32**, VG **0.963**.

Svaki jedinstveno naizmenično -0.01 / +0.01 p.u., ne birati smer na osnovu prvog rezultata. Fiksirani tačan redosled **8 NOVIH pravih AC NR poziva**:
1. BUS34 -0.01; 2. BUS34 +0.01;
3. BUS92 -0.01; 4. BUS92 +0.01;
5. BUS19 -0.01; 6. BUS19 +0.01;
7. BUS32 -0.01; 8. BUS32 +0.01.

Očekivani +/- VG ostaje unutar **originalnih VMIN 0.94 / VMAX 1.06** svih tih PV sabirnica. Izvorni `pypower.runpf` 5.1.19, `PF_ALG=1,PF_DC=0,PF_TOL=1e-8,PF_MAX_IT=40,ENFORCE_Q_LIMS=0,VERBOSE=0,OUT_ALL=0`, single-thread BLAS, Python3.12, scipy1.13.1/pandas2.2.3/pandapower2.14.11. Q se **naknadno** upoređuje sa individualnim originalnim QMIN/QMAX; svako kršenje isključuje originalno fizički `feasible`. Za svih 54 gen PG limiti, bus VMIN/VMAX svih 118, source-positive RATE_A MVA oba kraja, kompleksni nodalni bilans, bez novih izmišljenih ograničenja. Svaki ulaz u runpf broji se stvarno i na exception. Ako solver fail sve fizičke metrike `null`.

Za svaki od osam stanja evidentirati ciljnu generator QG, originalnu QMIN/QMAX, individualni excess, sve Q offenders, ukupni Q excess i promenu od **izmerene prethodne I20 source reference 32,3458 MVAr**, P/V/RATE_A i KCL; ciljnu originalnu ekonomsku cenu samo kao diagnostičku vrednost neizvodljivog PF, a **ne** izvodljiv OPF optimum. Ako makar jedno stanje postane potpuno source-feasible, to je samo deterministički lokalni kandidat koji zahteva nezavisnu proveru, ne dokaz nove heuristike ni GA boljeg od DE.

**Maksimum 8 pravih AC PF poziva, 0 AC-OPF poziva, 0 pokretanja optimizatora, 0 besplatnih kontrola**. CI testovi za izvorne identitete, osam source-valid delta scenarija, prethodno izmerenu baseline Q i bez lažnog brojanja. Arhivirati raw JSON/CSV, srpski izveštaj, sve pozitivne i negativne rezultate, ostati otvoren prema scenarijima gde svi +/- pogoršavaju Q.

## Naučna granica

Pozitivna osetljivost selektovanih lokalnih PV generatora motiviše **reprezentaciju kontrolnih resursa** za budući GAdapt i moguće ograničenjima uslovljeno adaptiranje operatora, ali AOS/sensitivity-aware operator izbor već postoje u literaturi; originalnost i statistička efikasnost u industriji NISU dokazane. IEEE118 je javni testni sistem, ne stvarni operativni dispečing.
