# Poglavlje 3. Diskretni problem raspodele reaktivne snage i dizajn eksperimenta

*Nacrt, 24. oktobar 2026. Napisan pre rezultata studije I56; sadrži samo model, pretpostavke i dizajn.*

## 3.1 Zašto diskretni problem i zašto rukovanje ograničenjima

Optimizacija u elektroenergetskim sistemima retko je problem sa kontinualnim promenljivim i jednostavnim
granicama. Regulacioni transformatori menjaju prenosni odnos u koracima, kondenzatorske baterije i prigušnice
uključuju se po stepenima, a zadati naponi generatora u praksi se biraju sa konačnom rezolucijom. Istovremeno,
skoro svaka tačka koju optimizator predloži krši neko ograničenje: napon sabirnice izlazi iz dozvoljenog opsega,
generator ne može da proizvede traženu reaktivnu snagu ili je grana preopterećena. U I47 razlika se odnosila na jaz penalizovanog skora pri 3000 PF poziva; na case14–case57 nijedna metoda nije našla izvodljivost. Zbog toga je
prirodno pitanje gde se GAdapt-ove osobine, a pre svega rad na eksplicitnim mrežama vrednosti i samoadaptacija
vođena raznovrsnošću, susreću sa stvarnom potrebom infrastrukture. Diskretni problem raspodele reaktivne snage
(optimal reactive power dispatch, ORPD) je takvo mesto: odluke su prirodno na mreži vrednosti, a teškoća
problema je u velikoj meri teškoća pronalaženja izvodljivog rešenja.

Kada je izvodljivost teška, način na koji algoritam poredi neizvodljiva rešenja postaje deo samog algoritma.
Literatura nudi mnogo tehnika za rukovanje ograničenjima, od statičke kazne do Deb-ovih pravila izvodljivosti i
ε-ograničenja, i više radova ih poredi na problemima optimalnog toka snage (Biswas i sar. 2018; Mallipeddi i
sar. 2012; Ali i sar. 2024). Manje je poznato kako se izbor tehnike slaže sa samoadaptacijom parametara. U
evolutivnim strategijama to je teorijski proučeno (Arnold 2013; Hellwig i Arnold 2016), a u DE varijantama
numerički prekršaji već ulaze u adaptaciju parametara (Zamuda 2017). GAdapt je poseban slučaj: njegova adaptacija
čita *vrednosti* troškova preživelih jedinki, a ne samo njihov redosled. Ovo poglavlje opisuje problem i dizajn
kojim se to pitanje može ispitati kontrolisano.

## 3.2 Model

Polazimo od standardnih MATPOWER slučajeva kako ih isporučuje pypower: IEEE mreže sa 14, 57 i 118 sabirnica. Za
svaki slučaj definišemo radni scenario tako što opterećenje svih sabirnica pomnožimo zajedničkim faktorom i
dodatno, za svaku sabirnicu, faktorom izvučenim iz unapred zadatog semena u opsegu ±10%. Aktivnu proizvodnju
generatora zatim fiksiramo na rešenje kontinualnog AC optimalnog toka snage za taj scenario, tako da se
optimizacija odnosi isključivo na napone i reaktivnu snagu. Ako kontinualni optimalni tok za neki scenario nema
rešenje, scenario se ne koristi; to se desilo za dva od četiri test scenarija mreže sa 57 sabirnica.

Kontrole su zadati naponi generatora, prenosni odnosi transformatora koji su u pogonu i susceptanse šantova na
sabirnicama na kojima ih slučaj već ima. Napon se kreće u granicama napona sabirnice generatora, prenosni odnos
između 0,9 i 1,1, a šant sa vrednošću b u slučaju između nule i 2b (za prigušnice, između 2b i nule). Svaka
kontrola uzima jednu od R vrednosti ravnomerno raspoređenih u svom opsegu, sa R ∈ {9, 17, 33}; mreže su
ugnježdene, pa finija sadrži sve tačke grublje. Ovi opsezi i koraci su naše pretpostavke modelovanja, a ne
specifikacije opreme: pypower slučajevi sadrže radne vrednosti, a ne kataloge uređaja. To je ograničenje koje
navodimo uz svaki rezultat. Rezultujući problemi imaju 9, 27 i 77 kontrola.

Jedna evaluacija je jedan Njutn-Rafsonov proračun toka snage. Cilj je zbir gubitaka aktivne snage. Ograničenja
grupišemo u četiri kategorije: napone sabirnica, reaktivnu snagu generatora, aktivnu snagu balansnog generatora i
termička opterećenja grana. Za svaku kategoriju računamo zbir prekoračenja u relativnim jedinicama, oduzimamo
toleranciju 10⁻⁶ i odsecamo na nuli; ukupan prekršaj V je zbir te četiri veličine. Rešenje je izvodljivo tačno
onda kada je V = 0. Neuspeo proračun toka (nekonvergencija ili nekonačan rezultat) dobija konvencionalne vrednosti
i nikada se ne smatra izvodljivim. Na ovim slučajevima termička ograničenja praktično ne deluju (granice od
9900 MVA), pa se teškoća svodi na napone i reaktivnu snagu; validacija na svežim mrežama sa stvarnim termičkim
granicama je predmet studije I58.

## 3.3 Šta se meri

Pitanje je da li efekat GAdapt-ove samoadaptivne politike mutacije na brzinu pronalaženja dobrog izvodljivog
rešenja zavisi od tehnike za rukovanje ograničenjima. Kao meru brzine koristimo ograničeno vreme do cilja: broj
proračuna do prvog rešenja koje je izvodljivo i čiji su gubici najviše 1% (plus 0,01 MW) iznad najboljeg poznatog,
podeljen budžetom od 3000 proračuna; pokretanje koje cilj ne dostigne dobija vrednost 1. Najbolje poznato rešenje
dolazi iz nezavisnih, deset puta dužih referentnih pokretanja, a ne iz pokretanja koja se porede, i ono nije
dokazani optimum.

Tehnike za ograničenja ulaze u GAdapt na dva načina, i to je ključ dizajna. Prvi je redosled: elitizam zadržava
najbolju polovinu, a roditelji se biraju ruletom po rangu, pa je za oba koraka važan samo poredak jedinki. Drugi je
vrednost: broj mutiranih jedinki zavisi od normalizovanog logaritamskog raspona troškova preživelih, a verovatnoće
mutacije potomaka od razlike troškova roditelja. Statička kazna i Deb-ova pravila mogu dati isti poredak, a sasvim
različite vrednosti u ta dva signala. Zato posmatramo četiri tehnike (statičku kaznu, adaptivnu kaznu, pravila
izvodljivosti i ε-ograničenje), a svaku primenjujemo kroz istu podklasu GAdapt-ovog modula za ocenjivanje, koja
posle svake evaluacije ponovo računa skalar svih jedinki pod tekućim parametrima tehnike, pre odsecanja.

Prema svakoj tehnici postavljamo četiri varijante politike mutacije sa istim operatorima: podrazumevani GAdapt;
GAdapt čiji signali, bez obzira na tehniku, čitaju zajednički skalar pravila izvodljivosti; i dve fiksne politike
sa tačno zadatim brojem mutiranih jedinki, promenljivih i standardnom devijacijom Gausove mutacije. Prva fiksna
politika preuzima medijane onoga što podrazumevani GAdapt stvarno radi na razvojnim scenarijima, a druga je
podešena na tim scenarijima iz mreže od 27 konfiguracija. Razvojni i test scenariji su strogo odvojeni.

Primarna procena je kontrast interakcije: razlika između adaptivne i podešene fiksne politike pod pravilima
izvodljivosti, umanjena za istu razliku pod statičkom kaznom, uprosečena sa jednakim težinama po bloku (mreža ×
rezolucija) i po scenariju. Neizvesnost procenjujemo stratifikovanim bootstrap-om celih uparenih vektora unutar
ćelija mreža × rezolucija × scenario, sa 20.000 ponavljanja. Sekundarne procene (uloga signala pod statičkom
kaznom, adaptivna kazna i ε-ograničenje naspram kazne, druga fiksna politika i kontrola kodiranja kazne koja čuva
poredak) koriguju se Holm-ovim postupkom.

## 3.4 Zašto ovaj dizajn i šta on ne može da kaže

Tri odluke čine rezultat tumačljivim. Prvo, sve varijante kreću iz iste početne populacije, jer GAdapt-ov
generator slučajnih brojeva pre prve generacije ne zavisi od tehnike ni od politike; to je provereno i
proverava se u kodu. Drugo, kod studije je potvrđeno bit-identičan čistom GAdapt-u kada se skalar ne menja, pa
razlike ne mogu poticati od same infrastrukture eksperimenta. Treće, protokol, kod i analiza zamrznuti su i
nezavisno recenzirani pre ijednog test merenja, a svako pojašnjenje zapisano je pre merenja na koje se odnosi.

Ograničenja su jednako važna. Kontrast meri ceo paket adaptivne politike, ne pojedinačni mehanizam. Ablacija
zajedničkog signala menja vrednosti u signalima, ali ne može da izdvoji „posredovani udeo“ efekta. Tri mreže ne
dozvoljavaju zaključak o uticaju veličine mreže. Na razvojnim scenarijima, u četiri od devet blokova nijedna
varijanta nije dostigla cilj, pa je simulirana snaga od 0,968 uslovna i verovatno precenjena. I58/I60 nisu potvrdile ubrzanje ugrađenih opcija; I59 nije stigao do potvrde.
