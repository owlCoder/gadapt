# Iteracija 21 — IEEE118 QMIN screening: samo BUS32 +0,01 p.u. poboljšao ukupan sistemski Q

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** završeno preregistrovanih **8 novih stvarnih originalnih PYPOWER `runpf` AC proračuna**, svi konvergentni, nijedan potpuno source-izvodljiv; nije testiran niti izmenjen GAdapt. Originalni upstream `bpzoran/gadapt` netaknut. [GitHub Actions #39654472814](https://github.com/owlCoder/gadapt/actions/runs/39654472814) prošao sve unit testove i osam električnih proračuna.

## Zaleđena referentna tačka, bez besplatnog AC

Nakon originalnog IEEE118 izvornog baseline iz I19 (ukupno 78,099 MVAr Q prekoračenja), deterministički I20 dobio je **32,345807697 MVAr** uz gen BUS103 VG -0,02 (izvorni VG 1,01→0,99 p.u.). U I20 su tada BUS103 i BUS105 individualno zadovoljavali izvorni QMIN/QMAX, ali još **četiri** PV generatora kršila QMIN: BUS34 (gen #16), BUS92 (#43), BUS19 (#9) i BUS32 (#15). Ovaj I20 stvarni AC rezultat, [sirovi JSON](results/ieee118_iteration20_q_sensitivity_8_real_ac_20261021.json), pročitan je kao prethodna referenca, **nije ponovo izvršen niti dodavan u 8 novih AC poziva**.

[Protokol I21](ITERATION21_PROTOCOL.md) commit `0dda3a18f39e1c5ac7e8316ceeee17f5094fdf89` zamrznut je pre eksperimenta: ista originalna javna IEEE118 AC mreža; svih 54 PG izvorno fiksno, gen BUS103 VG fiksiran 0,99, a svaki od četiri preostala QMIN PV izvora je **pojedinačno** pertubovan za -0,01 i +0,01 p.u. u originalnim bus VMIN/VMAX. Tokom PF Q nije nasilno nametnut, ali je fizička Q izvodljivost svakog generatora posebno naknadno proverena. Svi P/V, termički pozitivni RATE_A oba kraja i kompleksni AC balans provereni.

## Rezultati osam *stvarnih* source IEEE118 NR AC

| Samo jedan originalni VG setpoint promenjen | Originalni ciljni generator QG (MVAr) | Ukupni Q exces svih 54 gen (MVAr) | Promena ukupnog Q u odnosu na I20 | Q-offendera |
|---|---:|---:|---:|---:|
| Prethodni I20 baseline — **nije novi AC** | — | **32,346** | 0 | 4 |
| BUS34 -0,01 | −91,875 | 131,468 | +99,122 | 5 |
| BUS34 +0,01 | +51,760 | 83,661 | +51,315 | 5 |
| BUS92 -0,01 | −61,464 | 79,850 | +47,504 | 4 |
| BUS92 +0,01 | +34,539 | 46,926 | +14,580 | 4 |
| BUS19 -0,01 | −62,932 | 78,369 | +46,023 | 5 |
| BUS19 +0,01 | +35,458 | 49,394 | +17,048 | 5 |
| BUS32 -0,01 | −55,731 | 71,320 | +38,974 | 4 |
| **BUS32 +0,01** | **+24,040** | **30,526** | **−1,820** | **3** |

**Samo jedan od osam** dodatnih pokušaja popravio je ukupni Q exces: **gen #15 BUS32** sa izvornog VG 0,963 na 0,973 p.u., gde QG postaje +24,04 MVAr, unutar izvornog intervala [−14,+42]. Ostala su **tri** QMIN prekršaja: BUS34 **12,8422 MVAr**, BUS92 **10,9599 MVAr**, BUS19 **6,7238 MVAr** ispod originalnog QMIN. Svi osam proračuna su konvergirali, **0 pojedinačnih originalnih P, 0 bus V, 0 izvorno rated-thermal** kršenja; njihova konvergencija se **ne smatra** punom AC-OPF izvodljivošću.

**Važan negativan rezultat:** +0,01 p.u. za BUS34, BUS92 ili BUS19 učinio je ciljnu Q vrednost previše pozitivnom, često **iznad QMAX**; -0,01 je duboko pogoršao QMIN. Ovo su **jako osetljive lokalne PV kontrole** — grubo podešavanje čak i u pravom smeru može pokvariti ukupnu Q izvodljivost. Nije pokazano da je postojećem GAdapt-u potreban novi operator; pokazano je da raspon kontrolne perturbacije i izbor fizičkih resursa moraju biti pažljivo razmotreni.

## Reproduktivni dokazi

- [I21 preregistrovani protokol](ITERATION21_PROTOCOL.md)
- [I21 stvarni originalni `runpf` kod](iteration21_ieee118_four_qmin_controls.py)
- [I21 unit testovi, 0 AC](test_iteration21_ieee118_four_qmin_controls.py)
- [Raw CSV sa 8 source AC rezultata](results/ieee118_iteration21_four_qmin_8_real_ac_20261021.csv)
- [Raw JSON sa svim izvornim Q/P/V/RATE_A/KCL detaljima](results/ieee118_iteration21_four_qmin_8_real_ac_20261021.json)
- [Uspešni GitHub Actions #39654472814](https://github.com/owlCoder/gadapt/actions/runs/39654472814)

## Sledeća naučno korisna hipoteza

Pošto su simetrične `±0,01` probe bile pregrube za tri preostala QMIN generatora, **jednostavna klasična centralna konačna razlika Q/VG** iz ovih prethodno izmerenih osam stvarnih AC može motivisati *zaseban, pre-registriran* mali budžet sa tri pojedinačno predložena, **znatno manja** VG koraka i kontrolisanim kombinacijama. To je **domenski feasibility repair screen**, ne tvrdnja o novom genetskom operatoru; novost AOS, operator kredit i adaptacija izvodljivosti tek treba da se stručno proveri u literaturi.

Originalni puni IEEE118 AC-OPF u iteraciji16 ima post-hoc provereno izvodljivu referentnu tačku, ali to nije isti ograničeni podskup Q/VG kontrole. Ne postoji novi optimalan ekonomični rezultat za ove osam neizvodljivih PF slučajeva. Nema statističkog dokaza superiornosti, ni realne industrijske validacije.
