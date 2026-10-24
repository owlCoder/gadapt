**REVISE pre zamrzavanja:** predlog je održiv, ali mora eksplicitno definisati budžet koji upravlja ε. Ništa nisam menjao; izvršene su samo male provere sa sintetičkom funkcijom, bez istraživačkih pokretanja.

1. **Broj evaluacija.** Inicijalizacija troši 32 poziva; zatim ostaje 16 preživelih, a osam parova proizvodi 16 potomaka. [Mutacija bira neevaluirane potomke](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/population_mutation/base_candidate_solution_mutation_selector.py:85), bez dodatnih kandidata/evaluacija. Popravke duplikata prethode evaluaciji; posle ograničenih pokušaja [duplikati ipak mogu proći](/Users/danijel/Desktop/gadapt/gadapt/operations/crossover/base_crossover.py:56). Oni ponovo troše PF pozive. Dakle, **e_g=16 poziva, ne nužno različitih genotipova**. Sintetičke provere potvrdile su 32+16g.

2. **Raspored.** Za jednu putanju od 10.000 poziva preporučujem **B=10.000, N=625**: ε postaje nula pri g=313, posle 5.040 poziva. To je dovoljno robusno uz zamrznuta podešavanja; wrapper nije potreban. Međutim, primarni presek na 3.000 nastaje pre završetka rasporeda. `N=188`, izveden iz 3.000, prekida produženu putanju na 3.024 poziva — reprodukovano. Ako želite ε=0 oko 1.500, potreban je zasebno zamrznut wrapper koji menja samo `_progress()` na `calls/3000`, uz veliki generacijski limit; to je druga konfiguracija.

3. **Reference i blokade.** Ponovna upotreba I58 instanci/referenci je legitimna ako pravilo zamrznete pre I58 rezultata, bez naknadnog izbora blokova/ciljeva. `p=8` je odvojen od `p=6,7`; zaključivanje ostaje uslovno na zajedničke reference. Nedostizanje u I58 ne znači nužno nedostizanje G2. I58 drajver nije neposredno upotrebljiv: treba prilagoditi grane, uparivanje, potpune jedinice, checker za G2, analizu i manifeste. Njegova puna jednakost provenance-a odbila bi namerne I60 razlike.

**Predloženi tekst za zamrzavanje** — bira izvorni generacijski raspored:

> **Status: ZAMRZNUTO pre ijednog I58 rezultata.** I60, motivisan opisnim I56 nalazom, proverava GAdapt patch v4 sa `constraint_handling="epsilon"` (G2) prema istom buildu sa `constraint_handling=None`, f+1000V (G0). I58 ostaje nepromenjen.
>
> Podešavanja nasleđuju I58: populacija 32, elitizam 50%, bez sondiranja i imigracije. Obe grane koriste `exit_check="generations"`, `number_of_generations=625`, budžetski `exit_function`, timeout 10⁶. Svaka izvršava jednu putanju od 10.000 stvarnih PF poziva; prvih 3.000 određuje primarni ishod. Broje se inicijalizacija, ponovljeni genotipovi i neuspešni PF; nema prekida pri cilju. ε koristi izvorni v4 raspored, početni 20. percentil i eksponent 5; nula nastupa posle 5.040 poziva.
>
> Primarne mreže: case30, case39, case24_ieee_rts; case300 opisno. R=17; scenariji (0,95;301), (1,00;302), (1,05;303), spread=0,1; jedna VG po generatorskoj sabirnici. Nasleđuju se I58 OPF izuzimanja bez zamene; bez scenarija neke primarne mreže nema primarnog zaključivanja.
>
> Semena: 10⁷p+10⁵i+10³R+100j+s; i=0..3 navedenim redom, j=0..2, p=8, s=1..15. Seju se svi RNG-ovi; identičnost početnih G0/G2 populacija proverava se asercijom.
>
> Koriste se isključivo I58 reference svih pet metoda, p=7, s=1,2, po 30.000 poziva. Njihov SHA-256 i manifest vezuju se za I60 pre testiranja. I58 test rezultati ne menjaju reference, instance ili protokol. Cilj: V=0 i f≤L*(1+0,01)+0,01 MW; bez izvodljive reference samo izvodljivost.
>
> T=min(prvi poziv dostizanja/3000,1), uz nedostizanje=1. θ prosečava T(G2)−T(G0), jednako po mrežama i preostalim scenarijima. Bootstrap uparenih vektora unutar mreža×scenario: 20.000, seme 60, percentilni 95% interval. H60 je podržana samo ako je ceo interval ispod nule. Ostali ishodi su opisni.
>
> Nasleđuju se I58 pravila grešaka, ponavljanja i osetljivosti, uz potpune G0/G2 parove. Nezavisna provera obuhvata obe grane i sve svedoke cilja; neuspeh blokira zaključak. Arhiviraju se kompletna podešavanja, kod, okruženje i manifesti; drugi istraživač ponavlja paket ili se navodi ograničenje. Maksimum: 3,6 miliona novih PF poziva, bez provera/ponavljanja. Tvrdnja se ograničava na ovu konfiguraciju i skup.