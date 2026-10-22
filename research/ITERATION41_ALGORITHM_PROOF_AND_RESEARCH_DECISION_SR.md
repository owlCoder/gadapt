# I41 — dokazivo uklanjanje suvišnih vremenskih ograničenja: algoritam, teorema, testovi i naučni status

**22. oktobar 2026.** Za repozitorijum isključivo `owlCoder/gadapt`, bez menjanja originalnog upstream-a. [Preregistracija metodskog testa](ITERATION41_PROTOCOL.md) je komitovana pre implementacije, bez izmene I39 izvornog problema. Ovaj dokument je rezultat završenog rada na algoritmu, a **nije potvrda originalnosti doktorske teze niti benchmark nad stvarnim DFN saobraćajem**.

## 1. Algoritamski problem, neposredno vezan za postojeći GAdapt zadatak

U [I39 modelu](ITERATION39_REPORT_SR.md) se jedna zajednička modularna oprema mora dimenzionisati tako da može preneti sve zahteve iz 192 trening matrice. Za 26 fizičkih linkova MILP eksplicitno formira **4.992 vremenska kapacitetna ograničenja** i 272 binarne odluke o izboru između dve dozvoljene putanje za svaki usmereni OD par. Referentni HiGHS je potrošio ~169 s za 1%-gap cilj i dobio validan source-optimality bound. Nije legitimno menjati cene, originalne podatke ili krajnji cilj radi ubrzanja.

Naš **I41 modul** prepoznaje pojedinačna `(link e, time t)` ograničenja koja su implicirana nekim drugim `(e,s)` ograničenjem *za svaki mogući izbor 272 binarne rute*. Ona su **trajno uklonjiva iz MILP-a** bez gubitka ijednog dozvoljenog modularnog plana. Za razliku od aproksimativnog izbora scenarija, ovo je redukcija samog istog matematičkog problema, ne promena zahteva za bezbednost.

## 2. Propozicija i dokaz

Neka je `q[t,d] >= 0` količina saobraćaja OD para `d` u stanju `t`. Neka su `a[e,d,0]`, `a[e,d,1]` dve nula-jedan incidence dozvoljenih statičkih putanja po fizičkom linku `e`. Za binarni vektor izbora ruta `z[d]` opterećenje linka iznosi

```
L[e,t](z) = sum_d q[t,d] * a[e,d,z[d]]
```

Definišimo analitički donji minimum razlike dva vremenska opterećenja:

```
M[e;s,t] =
    sum_d min( (q[s,d]-q[t,d])*a[e,d,0],
               (q[s,d]-q[t,d])*a[e,d,1] ).
```

**Teorema (ispravnost sertifikata za dve nezavisno birane putanje).** U realnoj aritmetici, `M[e;s,t]` je **jednako** `min_{z in {0,1}^D}(L[e,s](z)-L[e,t](z))`. Ako je `M[e;s,t] >= 0`, onda je ograničenje `L[e,t](z)<=C[e](y)` redundantno uz `L[e,s](z)<=C[e](y)`, za bilo kakav zajednički trajni vektor modularnih instalacija `y`. Zamena originalnih scenarijskih redova po fizičkim linkovima njihovim zadržanim dominatorima **ne menja izvodljiv skup nijedne originalne binarne route/module odluke ni optimum MILP-a**.

**Dokaz.** Izraz `L[e,s](z)-L[e,t](z)` je zbir `D` sabiraka, a svaki sabirak zavisi isključivo od jednog `z[d]`. Stoga je minimizacija zbira po nezavisnim binarnim odlukama jednaka zbiru pojedinačnih minimuma (gornji izraz `M`). Ako je taj minimum nenegativan, razlika `L[e,s](z)-L[e,t](z)` je nenegativna za *svaki* dozvoljeni `z`, pa zadržana gornja granica `L[e,s](z)<=C[e](y)` implicira odbačenu `L[e,t](z)<=C[e](y)`. Pošto se nijedan red ne odbacuje bez direktno proverene veze sa **na kraju zadržanim** redom, obe formulacije imaju identične izvodljive skupove, a ciljna funkcija u njima je ista. QED.

**Granice teoreme:** zahteva dva nezavisno birana route kandidata po OD paru, statički zajednički kapacitet po linku i **jednake nonanticipativne rute u svim stanjima**. Ne primenjivati automatski na scenario-wise routing recourse, demand coupling, promenljiv broj putanja, failure-dependent topologiju ili model sa drugim fizičkim ograničenjima.

## 3. Implementirana numerička bezbednost i integracija

- [Presolver + originalni sertifikati](iteration41_certified_temporal_rows.py) koristi brzu proveru komponentno dominiranih izvornih zahteva i route-aware formulu minimalne razlike. Sumnjive skoro-jednake slučajeve zadržava umesto nasumičnog odbacivanja.
- Svaki izbačeni red sadrži direktno povezani, fizički zadržan dominantni red sa opservacionim računovodstvom. Ne koristi se nepouzdan lanac aproksimativne tranzitivnosti. Promene sertifikata (pogrešan link, lažni dominator, izostavljeni red, neispravan broj redova) se odbijaju **PRE solvera**.
- Konačna provera je sada rađena **bez zaokruživanja** na celobrojnim brojiocima sa zajedničkim stepenom dvojke za svaku ulaznu IEEE-754 double vrednost; čuva se realna vrednost tačno predstavljena tim binarnim zapisom, i Python `int` nije ograničen na 64 bita. Ovim je predikat `M>=0` matematički validiran **za numeričke vrednosti koje su stvarno učitane**; to samo po sebi ne vraća nepoznatu izvornu decimalnu preciznost.
- [Pravi I39 `exact_modular_milp`](iteration39_source_modular_capacity.py) prihvata opcioni `certified_rows`. Bez argumenta se poziva izvorna **puna I39 formulacija**, ne kompromituju se stari rezultati. Sa argumentom funkcija poziva obaveznu punu egzaktnu proveru sertifikata, gradi samo dokazano neophodne edge×time redove, i zatim **nezavisno revalidira ceo fizički TRAIN panel**, a ne samo redove viđene u redukovanom MILP-u.
- Računarska složenost jednostavnog agresivnog screeninga je najviše približno `O(|E|*|T|^2*|D|)` u najgorem slučaju. Takav overhead MOŽE nadmašiti dobit, posebno ako stvarni međusobno varirajući scenariji ne dominiraju jedan drugi. Zato ubrzanje treba meriti **sa vremenom sertifikacije uračunatim**, bez neprijavljene cene preprocessing-a.

## 4. Provereni rezultati, bez izmišljanja merenja

[Završni I41 GitHub Actions #39836240752](https://github.com/owlCoder/gadapt/actions/runs/39836240752) završio je SUCCESS: osam metodskih testova (uključujući nezavisnu racionalnu aritmetiku), četiri postojeća testa izvornog modularnog modela i sedam testova bezbednog lokalnog SNDlib loader-a, ukupno **19/19**. Od toga je **12** direktnih algoritamskih i regresionih I39/I41 provera. Nije izvršena nijedna stvarna DFN I41 mrežna optimizacija.

- Sintetički primer sa 3 linka, 128 monotono rastućih matrica i dve statičke alternative po OD zahtevu: **384 originalnih ograničenja, 3 zadržana, 381 sertifikovano uklonjeno** (99,21875% manje REDOVA). Ovaj konstrukt namenski favorizuje dominaciju i **ne dokazuje** da će isto važiti za originalne istorijske DFN matrice.
- Iscrpna enumeracija svih izbora ruta na malom modelu potvrdila je identične per-link maksimumе opterećenja za originalna i komprimovana vremenska stanja.
- Primer sa jednakim ukupnim saobraćajem, ali suprotnim rasporedom između OD parova, pravilno **ne uklanja** nijedno ograničenje: ne zaključuje se pogrešna lokalna dominacija iz globalne ukupne sume.
- Pun i redukovan MILP na istom malom, izvorno modularno naplaćenom modelu daju isti validni optimum i dual bound; neispravni sertifikat pada **pre** HiGHS poziva.

## 5. Kako ovo pripada disertaciji, a šta JOŠ nemamo

**Postignuto:** precizna teorema, računarski verifikator i opcioni metod za presolving stvarnog GAdapt infrastrukturnog MILP referentnog zadatka, povezan sa matematičkim ograničenjima, nezavisan od izmišljene simulacije i kompatibilan sa starim kodom.

**Nedostaje:** nije proverena originalnost. Scenario reduction, constraint presolve i exact/iterative robust separation su ustaljeni u literaturi. Za kontekst koristiti Goerigk & Khosravi (2023, [EJOR DOI](https://doi.org/10.1016/j.ejor.2023.03.019)), Zagorowska i sar. (2024, [IJRNC DOI](https://doi.org/10.1002/rnc.7038)) i noviji rad Chen & Wu (2026, [SSRN 7428860](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428860)). Nije dovoljno napisati „dokazano egzaktno“ da bi metod automatski postao originalan doktorat.

**Data-blocker:** originalna izvorna SNDlib arhiva nije sačuvana kao bajtovi u I39 artefaktu, a originalni server kasnije vraća TLS grešku / 404. Zato nema potvrđenog rezultata I41 za originalnih 26×192=4.992 redova i nema izmišljene tvrdnje o ubrzanju za 169 s I39 benchmark. [I40 hash-locked offline loader](iteration40_pinned_source_loader.py) sada može čitati **isključivo identične lokalno pronađene originalne datoteke** uz oba I39 SHA256. To ne može i ne sme rekonstruisati izgubljene vremenske matrice iz originalnih optimizacionih izlaza.

**GO / NO-GO:** ispitati preciznu route-aware konstrukciju protiv verifikovanog prior art i uz jake standardne HiGHS presolve/constraint-generation baseline-ove. Ako originalni realni podaci daju zanemarljivu redukciju ili literatura sadrži ekvivalentan model, metod ostaje vredno inženjersko unapređenje, a ne centralni PhD doprinos. Nikakva nova I41 real domain evaluacija pre oporavka originalnih bajtova i zasebne preregistracije za realni benchmark.
