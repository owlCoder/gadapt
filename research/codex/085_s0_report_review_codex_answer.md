**„H64a supported“ je računski opravdano prema zamrznutom pravilu, uz precizno ograničenje na S0 konfiguracije, funkcije i metrike.** Izveštaj zahteva dopune o odstupanjima i tumačenju. Pregled i proračuni bili su samo za čitanje; ništa nije menjano.

**1. Nezavisni proračun**

Iz `runs.json.gz`, uz arhivirane normalizatore, zasebno sam rekonstruisao putanje i agregate, bez pozivanja analizatora projekta.

| Konfiguracija | A | M: ponderisani prosek ćelijskih medijana g | CVaR₀,₉(L) |
|---|---:|---:|---:|
| GAdapt | 0,698303601 | 0,000998124 | 0,006271343 |
| PyGAD random | 0,534453807 | 0,046259481 | 0,053188327 |
| PyGAD adaptive | 0,493858230 | 0,044443641 | 0,058865958 |
| DE | 0,650989558 | 0,008139336 | 0,015709956 |

| Konkurent j | ΔA = A_G − A_j | ΔM = M_j − M_G |
|---|---:|---:|
| PyGAD random | 0,163849794 | 0,045261357 |
| PyGAD adaptive | 0,204445370 | 0,043445517 |
| DE | 0,047314043 | 0,007141212 |

Broj ćelijskih pobeda takođe odgovara [izveštaju](/Users/danijel/Desktop/gadapt/research/ITERATION64_S0_REPORT_SR.md):

| Konkurent | Manja medijana: GAdapt / konkurent / veza | Veći A: GAdapt / konkurent |
|---|---:|---:|
| PyGAD random | 10 / 9 / 2 | 20 / 1 |
| PyGAD adaptive | 10 / 9 / 2 | 20 / 1 |
| DE | 6 / 14 / 1 | 17 / 4 |

**Sve se poklapa do numeričkog zaokruživanja.** Nezavisno sam ponovio i 20.000 bootstrap uzoraka: \(t^*=3,213803224\), sa istim granicama. Svih 1.680 zapisa ima usklađene zbirove faza, ispravne indekse događaja i očekivana uparena semena.

**2. Provera protokola i DEVIATIONS**

Primarna [analiza](/Users/danijel/Desktop/gadapt/research/i64/s0_replication.py:298) pravilno sprovodi:

- težine 1/9 po funkciji, odnosno 1/27 po dimenziji funkcija sa tri dimenzije;
- pozitivan ΔM kao prednost GAdapt-a;
- fizičko indeksiranje od 1 i doprinos `(12000 − T + 1)/12000`;
- zanemarivanje dostizanja posle 12.000 i konstantan nastavak najbolje vrednosti posle ranijeg završetka;
- iste resamplovane indekse za sve četiri konfiguracije unutar ćelije;
- maksimum apsolutnih standardizovanih odstupanja preko šest kontrasta, zajedničku kritičnu vrednost i porodično α=0,01.

U tim primarnim računskim koracima **nema odstupanja**. Postoje sledeća odstupanja i nedorečenosti prema [protokolu](/Users/danijel/Desktop/gadapt/research/ITERATION64_PROTOCOL.md:22):

- **Pomoćni „search-only“ A ima grešku na nultom indeksu.** Koristi i poboljšanja iz nepretraživačkih faza. Ručna inicijalizacija PyGAD-a daje `T_search=0`: po 53 dostizanja ciljeva u obe konfiguracije. Formula tada daje doprinos veći od 1. To ne utiče na primarni fizički A, ali pomoćnu kolonu treba korigovati i opisati kao promenu obračuna troška uz zadržavanje opaženih rezultata.
- **Nepotpuna provenijencija.** Manifest sadrži heševe drajvera i protokola, koji odgovaraju sadašnjim datotekama, ali ne zahteva­ne heševe svih tranzitivnih izvora i sva razrešena podešavanja. Normalizator arhivira `s`, `f_star`, minimum uzorka; ne arhivira same uniformne tačke/vrednosti, a njegovo seme nije u manifestu.
- **Nepotpuni podaci o fazama.** Kompresovani događaji omogućavaju tačnu rekonstrukciju primarne najbolje putanje, ali faza najboljeg svedoka i faza svakog događaja nisu sačuvane.
- **Zaštita instrumenta nije potpuna.** Granica ispod \(f^*−10^{-12}s_i\) proverava se za uzorke normalizatora, ne tokom optimizacije. U arhiviranim poboljšanjima takvo kršenje nisam našao. Styblinski–Tang minimum računa se dvostrukom preciznošću, umesto zahtevane visoke preciznosti.
- **Semena odstupaju od zapisane mape:** kod koristi redosled `FUNCS` i `c=i`, umesto sortirane mape `c=3i+v`. Uparivanje konfiguracija ipak je očuvano. PyGAD dobija globalno postavljena semena, bez eksplicitnog `random_seed`.
- **CVaR za S0 nije eksplicitno definisan protokolom:** kod uzima dva najlošija od 20 ishoda, što je razumna generalizacija pravila za 100 ishoda, ali treba je navesti.

**3. Kako formulisati naslov**

Predložena formulacija:

> „S0 podržava operacionalizovanu H64a: među četiri ispitane konfiguracije GAdapt ima veći ponderisani prosečni ECDF A do 12.000 fizičkih poziva od sva tri konkurenta, prema simultanim bootstrap intervalima sa nominalnim porodičnim α=0,01.“

Prolaz nastaje već granom **„svi ΔA pozitivni“**. Nije potrebno imenovati jednog „izuzetka“; `exception_candidates` ne identifikuje stvarnog izuzetka.

Za završnu preciznost mora stajati: **manji ponderisani prosek ćelijskih medijana pri izvornom zaustavljanju**. Dve ćelije, Rastrigin-20 i Griewank-7, zajedno daju oko **104,6% neto ΔM prema DE**, dok ostale zbirno umanjuju prednost. To objašnjava istovremene rezultate 6:14 po medijanama i 17:4 po A. Ćelijske pobede su opisne; vrlo male razlike blizu numeričke nule nisu dokaz praktične prednosti.

Završna preciznost nije poređena pri jednakom budžetu. Ponderisani proseci poziva su približno 10.184/16.515/25.155/11.887; **25.155 je prosek**, dok PyGAD adaptive dostiže 57.632 poziva. DE na nekim 20D ćelijama troši oko 36.000.

Brojanje PyGAD `best_solution()` reevaluacija odgovara protokolu i meri trošak mentorove implementacije. Zaključak zato obuhvata i njenu režiju.

**4. Osetljivosti koje sada treba dodati iz arhive**

Već sam izračunao preciznost pri **najviše 12.000 fizičkih poziva**, uz zadržavanje rezultata ranije završenih pokretanja:

| Konfiguracija | M₁₂₀₀₀ |
|---|---:|
| GAdapt | 0,001319812 |
| PyGAD random | 0,046261205 |
| PyGAD adaptive | 0,046539867 |
| DE | 0,009336169 |

Ćelijski odnos GAdapt–DE postaje **10:10:1**, a prema obe PyGAD konfiguracije **13:6:2**. Dodati CVaR, dostizanja i intervale za ovaj presek; on ne predstavlja nastavak svih algoritama do punog budžeta.

Dodati još:

- korigovanu analizu „search-only“ i zasebno isključivanje callback troška, uz jasno zadržavanje inicijalizacionih evaluacija;
- rezultate po funkciji, dimenziji i cilju, doprinose svakom ΔM i analizu izostavljanja pojedinačnih funkcija;
- opisni presek na 3.000 poziva;
- osetljivost bez semena 1–3, čiji su ishodi bili viđeni u probi pre glavnog pokretanja.

Promena obračuna troška nije simulacija izvršavanja bez callback-a; takav kontračinjenični eksperiment arhiva ne omogućava.

**5. Šta izveštaj sme da kaže mentoru**

Sme da iznese reprodukovanu prednost agregatnog A, ograničenu prednost agregatnog završnog M i opisno niži CVaR na ovom skupu.

Ne sme da tvrdi opštu veću preciznost, prednost u većini ćelija, industrijsku pouzdanost, korist preseta ili uzročnu prednost mutacionog operatora. Funkcije nisu pomerene ni rotirane; četiri imaju optimum u ishodištu, a Rosenbrock uzak domen. S0 ostaje ograničena replikacija sa 20 semena, uz obavezno obelodanjivanje prethodnog uvida u tri semena.