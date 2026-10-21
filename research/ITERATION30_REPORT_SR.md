# Iteracija 30 — prostorno različiti IEEE118 PD/QD scenariji: rani prekid nije povećao broj uspešnih GAdapt pokretanja

**21.10.2026; fork owlCoder/gadapt:main. Završen preregistrovan eksperimentski niz od 20 run-ova sa 3.580 zaista izvršenih originalnih PYPOWER AC NR proračuna.** Nula numerički nekonvergentnih AC. Protokol sačuvan pre svih novih simulator poziva: [I30 protokol](ITERATION30_PROTOCOL.md). Uspešno testiran fizički CI: [GitHub Actions #39671017417](https://github.com/owlCoder/gadapt/actions/runs/39671017417). Nije menjana GAdapt evolutivna logika niti originalni I29 opt-in screening evaluator.

## Model i razlog za nezavisni scenario test

I29 na prethodno kalibrisanom uniformnom PD/QD opterećenju 98%/100%/102% dao je benefit ranog source screening-a (legacy GAdapt 1/4 uspešnih seedova, early rejection 4/4), ali adaptivni redosled je imao potpuno isti učinak kao fiksni. Zato je u I30 unapred izabrana NOVA, prethodno netestirana prostorna raspodela izvornog javnog IEEE118 PD/QD, bez promene kontrolnih promenljivih:
- nominal: neizmenjeni originalni PD i QD svih 118 bus;
- odd_bus_heavier: originalni BUS_I neparni ×1,02, parni ×0,98, jednako za PD i QD;
- even_bus_heavier: originalni BUS_I parni ×1,02, neparni ×0,98, jednako za PD i QD.

**Ista javna IEEE118 topologija, nije nezavisna mreža ili industrijski izvor.** Originalnih 118 bus, 54 aktivna generatora i 186 branch; originalni PG (osim stvarnog AC slack outputa), generator Pmin/Pmax i Qmin/Qmax, bus Vmin/Vmax, positive RATE_A oba kraja, originalni gencost i complex AC KCL. Istih šest originalnih PV VG kontrola BUS103,32,34,92,19,74, iste uže prethodno informisane granice. Nema slobodnog punog ekonomskog AC-OPF dispečinga.

Svi candidate PV setpointi identični su kroz sva tri prostorna režima. **Robust source feasible** znači da svaki od tri stvarno izvršena originalna AC PF konvergira i zadovolji SVA pojedinačna generator PG/QG, bus VM, pozitivna terminalna RATE_A i complex KCL ograničenja. Ako se jedan stvarno konvergentan scenario nađe neizvodljiv, potpuno robusna izvodljivost te tačke je dokazano false; za preskočene scenarije nema merenja i nema originalne source ekonomske sredine. Numerički NR neuspeh bi ostao unknown, ali nijedan se ovde nije desio.

Pet fiksnih metoda: GAdapt sa full, fixed early i adaptive early evaluacijom; SciPy DE sa full i fixed early evaluacijom. Sva tri GA koriste isti izvorni legacy mutator, cost-diversity i pop12, DE koristi polish=False. Zamrznuta nova semena 2070,2071,2072,2073; 180 STVARNIH AC maksimum po seed-metodi, dakle najviše 3600 i ostvareno 3580 native PF. Nedovoljnih 1–2 preostalih AC u nekim run-ovima ne pokreću novi kandidat zato što bi njegova puna 3-scenario potvrda bila nemoguća; takvi pozivi nisu fiktivno naplaćeni.

## Izmereni rezultati svih 20 optimizer run-ova

| Metod | Seed runovi sa bar 1 full 3-scenario feasible (od 4) | Stvarno 3-scenario feasible kandidata | Kandidata potpuno proverena sa 3 AC | Dokazano neizvodljivi rano presečeni kandidati | STVARNI originalni AC | Najbolji provereno feasible mean original gencost |
|---|---:|---:|---:|---:|---:|---:|
| **GAdapt full** | **2/4** | **14** | 240 | 0 | **720** | 131.196,872164 |
| **GAdapt stop_fixed** | **2/4** | **58** | 58 | 513 | **712** | **131.196,411191** |
| GAdapt stop_adaptive | **2/4** | **60** | 60 | 514 | **714** | **131.196,411191** |
| DE full | **3/4** | **3** | 240 | 0 | **720** | 131.196,583381 |
| **DE stop_fixed** | **4/4** | **44** | 44 | 564 | **714** | **131.196,338388** |

**Glavni negativan nalaz za eventualni doktorski algoritam:** iako su screening GA režimi našli mnogo više potpuno potvrđenih candidate rešenja (58/60 prema14), **nisu imali bolju stopu uspešnih GA seedova** od potpunog baseline-a: u sva tri slučaja tačno **2/4**. Štaviše, za seed **2070** GAdapt full je našao 5 zaista all-three-feasible kandidata, a oba early screen moda **nula**; obrnuto za seed **2072** full nula, a oba screen moda 17. To su jasni primeri da censor score menja selekciju i GA populacione putanje i može biti koristan ili štetan, te povećan broj obrađenih kandidata nije sam po sebi dokaz robustnije konvergencije.

**Adaptivni redosled** dao je samo 2 više fizički feasible source kandidata (60 prema 58) po dodatna 2 realna AC i **bez ijednog dodatnog uspešnog semena ili boljeg minimuma troška**. Beta-smoothed empirijska izmerena stopa failure koristi samo stvarno AC, ali adaptivni redosled ima selektivno cenzurisane uzorke i njegova inferencija se ne može bez dodatnih dokaza nazvati optimalnom, originalnom ili nepristrasnom. U praksi ova adaptacija nije pokazala bitan dodatni benefit protiv jednostavnog fiksnog redosleda.

**DE** je zabeležio 4/4 potpuno all-three-feasible run-a sa screening-om i najbolju verifikovanu mean gencost vrednost 131196,338388. Time je jasno da benefit screening-a **nije jedinstven za GAdapt**, a jaka konkurentska metoda i dalje predstavlja važan baseline.

## Brojači i ograničenja

U originalnim stvarnim source simulator pozivima po nominal/odd_heavier/even_heavier:
- GAdapt full: [240,240,240] = 720 AC.
- GAdapt stop_fixed: [571,75,66] = 712 AC; **1001 drugih scenario PF nikada nisu izvršena**, pa nije legitimno koristiti njihove nepostojeće rezultate.
- GAdapt stop_adaptive: [574,71,69] = 714 AC; 1008 neizvršenih drugih scenario poziva *njegove različite candidate putanje*.
- DE full: [240,240,240] = 720 AC.
- DE stop_fixed: [608,55,51] = 714 AC; 1110 nedokazanih nedostajućih scenario PF samo u toj candidate putanji.

**3580 pravi AC od 3600 dostupnih**; 20 mesta preostalo zbog rezerve za kompletno proverljive triple-state kandidate. Nema besplatnih originalnih PF, nema naknadne „virtualne“ provere, nema stvarnih AC-OPF poziva, nema lažnih robust-feasible zapisa za preskočene scenarije. Izvorni KCL ponovno izračunat iz iste PYPOWER biblioteke, nezavisan drugi elektroenergetski solver nije korišćen.

## Šta znači za disertaciju

[I29 izveštaj](ITERATION29_REPORT_SR.md) i [I29 prior-art](ITERATION29_PRIOR_ART_SR.md) već pokazuju da je rano odbacivanje i scenarijska evaluacija poznata literatura (Sankary et al., 2018, doi:10.1002/2017WR022068). Naš doprinos softveru je reproducibilan, auditabilan GAdapt budžetski evaluator, ali **NIJE dokazana nova teorija GA**. Na novim prostornim scenarijima nije potvrđena viša stopa uspešnih GA seedova, a adaptivna komponenta praktično nema dodatnu dokazanu vrednost.

Sledeće istraživanje, ako mentor potvrdi ovaj smer, mora razdvojiti tri efekta: povećan broj genome-a na istoj AC budžetskoj granici, različit censored fitness score landscape i adaptivno biranje redosleda. Neophodni su mnogo više uparenih semena, benchmark neograničenog punog/source AC OPF, IEEE14 kao druga topologija, različite prostorne i lokalne Q promene, i nezavisan telekom industrijski test uz literaturno potvrđenu eventualnu novu hipotezu. **Nemamo dokaz da je doktorski naučni doprinos već ostvaren.**

## Trajni dokazi

- [Preregistracija I30](ITERATION30_PROTOCOL.md)
- [Originalni source-bus-parity i stvarni AC kod, neizmenjen I29 evaluator](iteration30_spatial_load_holdout.py)
- [Zero-AC originalni BUS_I parity/PG/VG/unit test](test_iteration30_spatial_load_holdout.py)
- [Sirovi CSV 20 runova](results/ieee118_iteration30_spatial_parity_holdout_20runs_3580_trueAC_20261021.csv)
- [Sirovi JSON svih originalnih AC brojača](results/ieee118_iteration30_spatial_parity_holdout_20runs_3580_trueAC_20261021.json)
- [CI svih 3580 stvarnih native AC #39671017417](https://github.com/owlCoder/gadapt/actions/runs/39671017417)
