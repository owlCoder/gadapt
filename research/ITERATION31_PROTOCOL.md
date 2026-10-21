# Iteracija 31 — unapred registrovana dekompozicija ocene i troška AC simulacija

**Datum protokola: 21.10.2026. Status: plan/pre fizičkih I31 AC poziva.** Grana `research/i31-fitness-budget-ablation` zasnovana na I30 commitu `9f8f33b`. I29/I30 rezultati i originalna GAdapt implementacija ostaju nepromenjeni. Ovaj rad **nije** novo dokazani optimizacioni algoritam.

## Pitanje i hipoteze

I29/I30 nisu razdvojili korist *više obrađenih kandidata pod fiksnim AC budžetom* od promenjenog **censored fitness** signala. I31 poredi tri principijelno različite grupe, uz četvrtu proveru redosleda:

1. `full_true`: originalni `SequentialScenarioBudgetCost(mode="full")`: sva tri stvarna scenarija, kompletna izvorna mean-gencost + fizička penalizacija.
2. `full_censored`: **nova isključivo eksperimentalna kontrola**: obavezno sva tri stvarna AC, ali za selekciju vraća **istu** cenzurisanu vrednost `1e9+1e5*first_measured_violation` kao stop-fixed kad su sva tri solvera konvergentna i bar prvi izmereni scenario fizički neizvodljiv. Za sve potpuno izvodljive kandidate vraća pravi kompletni objective. Pri numeričkom neuspehu vraća numerically unknown; ništa se ne proglašava feasible bez sva tri izmerena scenarija. Prava puna metrika i dalje se posebno meri i čuva.
3. `stop_fixed`: originalni I29 `mode="stop_fixed"`, identičan first-failure censored score pri istom kandidatu bez kasnijeg solver neuspeha, uz preskakanje neizmerenih scenarija.
4. `stop_adaptive`: originalni I29 `mode="stop_adaptive"`, empirijski redosled samo iz stvarno merenih source ograničenja.

**Kontrasti pre gledanja rezultata:** (1)–(2) je efekat **promene selekcionog fitnesa** uz isti broj AC po kandidatu, (2)–(3) je uticaj mogućnosti da se od istog AC budžeta obradi više kandidata uz zajedničku definiciju selekcionog fitnesa (različita stohastička pretražna putanja i dalje može otežati kauzalno tumačenje); (3)–(4) je inkrementalni efekt empirijskog redosleda. Nisu jedinstveno identifikovani nezavisni kauzalni efekti, jer optimizacioni tokovi mogu divergirati. `full_censored` služi samo kao kontrola, ne kao predlog naučne inovacije.

## Nema novog podešavanja prema I31 rezultatima

Fizika je **isti javni originalni IEEE118, ista I30 tri prostorna režima** `nominal`, `odd_bus_heavier`, `even_bus_heavier`. Nepromenjeni case118 source PG/QG/V/positive RATE_A/KCL, 6 originalnih VG kontrola BUS103/32/34/92/19/74 i identične granice iz I27–I30; PD/QD jedine prostorno perturbovane veličine. I31 **nije nezavisna topologija i nije slepi scenario holdout** (I30 scenariji su već viđeni); **12 novih unapred izabranih semena: 2080–2091 uključivo**. Ista legacy GAdapt `GA` populacija=12, `cost_diversity_metric="log_relative"`, `population_mutation="cost_diversity,parent_diversity"`, `exit_check="generations"`, `number_of_generations=128`, i isti timeout i simulator counter.

**Fiksno 4 GA metoda × 12 seeds × najviše 180 stvarnih AC = najviše 8640 stvarnih PYPOWER runpf poziva.** Kod pred izvršavanje proverava ove konstante. Rezervacija tri slobodna AC pre svakog novog kandidata ostaje ista za sve metode; dozvoljeno 1–2 nepotrošena AC po run-u kod screening-a. Bez stvarnih poziva nema dodavanja brojača. Numerička nekonvergencija ostaje `unknown`, nikada „dokazana fizička neizvodljivost“.

## Unapred definisane glavne metrike

- **Primarna:** broj semena sa bar jednim potpuno potvrđenim feasible x (od 12) po metodi; zasebno broj zaista izvršenih AC. Za uparene kontraste prijaviti 2×2 seed raspored discordantnih uspeha; nema naknadnog biranja jedne povoljne metrike.
- **Sekundarna:** ukupno potpuno provereni kandidati, broj potvrđenih feasible među njima (to nisu nezavisne statističke jedinice), broj candidate objektivnih zahteva, broj najranije dokazanih neizvodljivih skrininga, vreme do prvog confirmed-feasible brojača stvarnih AC, najbolja srednja originalna source cost **samo** među tri puta zaista fizički potvrđenim feasible slučajevima; izveštavati i neuspešne seedove.
- Dodatna kontrola: `full_censored` mora potrošiti tačno 3 prava source AC po započetom kandidatu i `unobserved` mora biti 0; kada nema numeričkih neuspeha, vraćeni fitness pri prvom stvarnom neizvodljivom scenariju mora biti istovetan `stop_fixed` na **istom** ulazu; strict counter and original real-source feasibility semantics se ne menjaju.
- Nema statističke superiornosti ni originalnosti iz samog uspeha na 12 semena. Nema automatskog proglašavanja kandidata feasible kad nisu proverena sva 3 scenarija. U svakom slučaju arhivirati pozitivan/negativan rezultat.

## Plan izvršenja

Prvo **zero-AC sintetički** jedinični i preflight testovi; zatim tačno prethodno definisana fizička evaluacija, bez promene seeds/box/scenarios ili budgeta posle rezultata. Čuvati sve per-run originalne brojače u raw JSON, CSV, logove i verzije softvera; naknadni opis rezultata posebno, bez retroaktivnih promena protokola. I31 ne tvrdi novel GAdapt operator, nezavisnu IEEE14 mrežu niti industrial telecom validaciju. Ti koraci zahtevaju odvojeni eksperiment i pregled literature.
