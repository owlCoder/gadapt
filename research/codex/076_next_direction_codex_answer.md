**I63 može biti legitimna nova studija, ali prosto povećanje budžeta sada nema dobro opravdanje. Najperspektivniji preostali pravac biram pod (c): dokaziva karakterizacija štetnog uticaja numeričkih signala adaptacije, povezana sa infrastrukturnim eksperimentom. Originalnost tog doprinosa još nije ustanovljena.**

1. **I63: dozvoljen naslednik, pod jasnim uslovima.**

[I61 protokol](/Users/danijel/Desktop/gadapt/research/ITERATION61_PROTOCOL.md) §5 zatvara I61: nema proširivanja budžeta ili mreža. [Sirovi izlaz](/Users/danijel/Desktop/gadapt/research/results/iteration61/select_b.json.gz) potvrđuje `chosen = {}`. H61 nije ocenjena; nema ni potvrde ni opovrgavanja interakcije.

Mala ispravka premise: case30/FR|1 prolazi pri **6000**, sa T≈0,486; pri 12.000 ima T≈0,243, dakle ne prolazi.

Postoji važnija prepreka: na istim putanjama, uz isti cilj, za već dostignuti cilj važi T=h/B. Zato veći B dodatno smanjuje već prenisku medijanu. Case30/FR|1 i case39/SP|0 već su ispod 0,3 pri 12.000. **Mreža {12.000,24.000,48.000}, uz postojeći prozor, ne može popraviti njihov prolaz na tim podacima.** Nova semena daju neizvesnost, ali ne uklanjaju ovaj dokaz lošeg razvojnog kriterijuma.

Naslednik je odbranjiv ako:

- I61 ostane zatvoren i arhiviran kao STOP, bez zamene njegovog ishoda.
- Promena dobije metodološko opravdanje: cilj je informativan test interakcije, a ne prihvatanje uslova koji daju povoljan znak.
- I61 razvojni podaci budu eksplicitno označeni kao pilot za I63. Preregistracija može važiti za buduću potvrdu; ne može retroaktivno učiniti pilot neviđenim.
- Pre novih merenja budu zamrznuti kompletan razvojni postupak, konačna mreža budžeta, prozor, pravilo izbora, kalibracija FX-T, proba, snaga, analiza i završni STOP.
- Izbori koriste isključivo razvojne podatke. Sveža razvojna proba proverava izbor bez naknadnog ponovnog izbora. Potvrdna semena budu nova; neotvoreni I61 potvrdni scenariji mogu se koristiti uz obelodanjivanje ponovne upotrebe topologija i odsustva uvida u njihove optimizacione ishode.
- Ostanu zaštite od cenzure i degeneracije: dostizanje svake grane, varijansa kontrasta, realistična simulacija snage i kalibracija nule. Prozor koji dopušta T=1 ne sme automatski proglasiti potpuno neinformativne ćelije prihvatljivim.
- Postoji jedan konačan naslednik, sa obavezom izveštavanja svakog ishoda. Serija I63→I64→… sa ublažavanjem uslova bila bi upravo zabranjeno ponavljanje do pozitivnog rezultata.

Promena B menja i normalizovani estimand i značenje efekta 0,02. To treba ponovo obrazložiti. Pošto I61 nije stigao do testa, ovde nema dva izvršena potvrdna testa iste hipoteze.

Predloženo obelodanjivanje:

> „I63 je prospektivno preregistrovan naslednik, motivisan razvojnim STOP-om I61. Nakon uvida u I61 razvojne medijane promenjeni su [tačno navesti kriterijume]. I61 ostaje zaustavljena studija bez zaključka o H61. Njeni razvojni podaci korišćeni su za projektovanje I63; potvrdni optimizacioni ishodi nisu korišćeni za izbore. I63 procenjuje interakciju uslovno na novi razvojni postupak i budžete i ne predstavlja nezavisnu potvrdu izbora dizajna.“

Trošak, uz nasleđeni obim I61, maksimalni B=48.000 svuda i konzervativno devet potvrdnih scenarija:

| Obim | PF pozivi | CPU-sati | Idealno, 10 jezgara |
|---|---:|---:|---:|
| Sam izbor B: 60 putanja × 48.000 | 2,88 M | 2,6–3,6 | 0,26–0,36 h |
| Ceo postupak, n=80 po ćeliji | ≈204,7 M | 188–256 | 18,8–25,6 h |
| Ceo postupak, n=480 | ≈895,9 M | 821–1120 | 82–112 h |

Poslednja dva reda uključuju reference, FX-T, probu, proveru prekida i približan gate; ne uključuju ponavljanja, OPF, proverivače, simulaciju snage i režiju. Prekid pri cilju može smanjiti potrošnju. **Preporuka: NO-GO za I63 u obliku „samo veći B“; uslovni GO za novi, obrazloženi dizajn.**

2. **Prvi izbor: karakterizacija zavisnosti adaptacije od predstavljanja troška.**

Istraživačko pitanje: kada promena numeričkog predstavljanja kvaliteta, koja čuva poredak kandidata, menja GAdapt-ovu adaptaciju toliko da pogoršava dostizanje infrastrukturnog cilja?

Najbliži prior art već ozbiljno ograničava novinu:

- Atamna, Auger i Hansen analiziraju gubitak invarijantnosti i vezu sa konvergencijom: DOI **10.1016/j.tcs.2018.10.006**. [Izvorni rad](https://www.sciencedirect.com/science/article/pii/S030439751830611X).
- Sakamoto i Akimoto, ARCH, koriste rangiranje radi invarijantnosti: DOI **10.1162/evco_a_00310**. [Autorski rad](https://arxiv.org/abs/1811.00764).

Dakle, „vrednosti troška utiču na adaptaciju“ i „rangovi uklanjaju zavisnost od monotonih transformacija“ nisu novina. Ni ponavljanje H56b/SP-T nije novi pravac; njihova nepodržanost mora ostati vidljiva. Odbačeni K6 takođe se ne vraća pod drugim imenom.

**Tačna kandidat-novina:** oštra karakterizacija kako GAdapt-ova početna normalizacija log-raspona, roditeljski signal, zaokruživanje i zasićenje zajedno ograničavaju ili pojačavaju promenu stvarne raspodele mutacije, sa posledicom po vreme dostizanja na eksplicitnoj klasi diskretnih problema. **Novina nije ustanovljena.**

Pretpostavke: deterministički evaluator, fiksna strogo rastuća transformacija tokom celog pokretanja, isti poredak i pravila veza, ista inicijalizacija i operateri. Predložena teorema mora povezati promenu signala sa netrivijalnom granicom očekivanog broja evaluacija na definisanoj klasi problema. Dokaz da se signal promenio nije dovoljan.

Falsifikacija: četiri grane, dve unapred izabrane transformacije × adaptivna/podešena fiksna politika. Transformacija ulazi samo u numeričke adaptivne signale; selekcija i fizički cilj ostaju isti. Fiksne grane moraju imati identične tragove. Razvoj bira transformacije i predviđa smer; sveži scenariji proveravaju predikciju. Uključiti slučajeve gde teorija predviđa mali efekat. Ovo ispituje prediktivno objašnjenje, bez tvrdnje o posredovanom udelu.

Budžet: najpre **dve nedelje za literaturu i dokaz, bez novih PF eksperimenata**. Posle prolaza: okvirno 3 mreže × 3 scenarija × 30 semena × 4 grane × 12.000 = 12,96 M PF; sa razvojem i referencama plafon 20 M, odnosno **18–25 CPU-sati**. Snagu proveriti pre testa.

**GO samo za proveru novine i dokazivosti. NO-GO za implementaciju dok novina nije ustanovljena.** Ako rezultat ostane elementarna neinvarijantnost, već poznata interakcija ili model bez odbranjive veze sa GAdapt-om, pravac zatvoriti.

3. **Drugi izbor: merna studija posledica pogrešnog računovodstva.**

COCO već postavlja broj poziva kao centralnu meru: DOI **10.1080/10556788.2020.1808977**. IOHexperimenter pruža prilagodljivo evidentiranje: DOI **10.1162/evco_a_00342**. [COCO](https://coco-platform.org/), [IOHexperimenter](https://github.com/IOHprofiler/IOHexperimenter).

Još bliži konkurent je Ravber i sar. (2025): DOI **10.15388/25-INFOR603**. Već analiziraju različite implementacije, dodatne evaluacije i posledice po performanse. [Izvorni rad](https://informatica.vu.lt/journal/INFORMATICA/article/1384/read).

Zato brojanje, klasifikacija poziva, jednaki budžeti i revizija biblioteka nisu dovoljna novina. Ocena postojećeg audit-rada kao internog dokumenta ne rešava se promenom naslova.

**Kandidat-tvrdnja:** unapred definisane osobine računovodstva predviđaju veličinu i smer promene poređenja GAdapt-a sa konkurentima kada se uvede stvarni zajednički budžet simulatora, uz odvojeno merenje kvaliteta inicijalizacije, prekoračenja i vraćenog rezultata. **Novina nije ustanovljena.**

Formalno treba razdvojiti zahtev optimizatora, fizički poziv simulatora, keširani odgovor i pripremni rad. Predloženi teorijski cilj bile bi oštre granice stabilnosti rangiranja uz nepotpuno računovodstvo i uslovi valjanog preračunavanja tragova. Sam identitet „ukupno = zbir faza“ nije doprinos. Ako algoritam menja raspored prema nominalnom B, skraćivanje dužeg traga ne zamenjuje novo izvršavanje.

Falsifikacija: preregistrovano poređenje nominalnog i strogo sprovedenog PF budžeta za GAdapt, CMAwM i validirani L-SHADE; zasebna kontrola probnih tačaka; isti razvojni trud; predikcije proverene na svežim scenarijima i nezavisnim izvršavanjem. Bez prediktivnog rezultata izvan već poznatih pojedinačnih grešaka, nema nove okosnice.

Budžet: nedelja za razlikovanje od Ravbera/COCO; zatim plafon **30 M PF = 27,5–37,5 CPU-sati**. **GO za proveru merne hipoteze; trenutno NO-GO kao ustanovljen doktorski doprinos.**

Benchmark pravac (b) rangiram niže. COCO/IOH već daju infrastrukturu eksperimenta; CEC realni ograničeni skup ima DOI **10.1016/j.swevo.2020.100693**, a PGLib standardizuje AC-OPF model i podatke. [CEC autorski paket](https://github.com/P-N-Suganthan/2020-RW-Constrained-Optimisation), [PGLib izveštaj](https://www.coffrin.com/publication/pglib-opf/). Njihova integracija za diskretni ORPD može biti koristan artefakt, ali doktorska novina nije ustanovljena. I62 daje potreban spoljni kontekst, bez rešavanja originalnosti.

4. **Ako novih rezultata nema, poštena odbrambena linija glasi:**

> Disertacija daje kontrolisanu empirijsku karakterizaciju GAdapt-a na odabranim infrastrukturnim modelima, instrumente za proveru evaluacija i proverenu opcionu integraciju standardnih tehnika rukovanja ograničenjima. I56 podržava malu interakciju politike mutacije i rukovanja ograničenjima, praktično zasnovanu na case14; mehanizam preko numeričkih signala nije potvrđen. I61 je zaustavljena razvojnim pravilom, pa prenos interakcije ostaje nepoznat. I58/I60 nisu potvrdile ubrzanje, a I59 nije stigla do potvrdnog testa. Domet rada jeste proverljivo znanje o ponašanju biblioteke i granicama njene primene; originalna optimizaciona metoda, opšta konkurentnost i industrijska korist nisu ustanovljene.

Tri najjača napada komisije:

- **Originalnost i dovoljnost:** šta tačno prevazilazi poznatu evaluacionu praksu, postojeće dijagnostike i integraciju standardnih metoda?
- **Čvrstina centralnog nalaza:** mali H56a, zavisnost od case14, degenerisani blokovi, uslovna snaga i nereplikovan rezultat.
- **Veza sa mentorovim zahtevom:** pretpostavljene diskretizacije, malo topologija, nepotpun konkurentski kontekst i odsustvo potvrđenog korisnog unapređenja GAdapt-a.

**Sa sadašnjim dokazima ne bih tvrdio da je mentorov zahtev već ispunjen.**