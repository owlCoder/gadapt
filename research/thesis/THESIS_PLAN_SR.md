# Plan teze (izvor: Codex 094, 2026-10-29) — zamenski tekst CH1 §1.3–1.4, novi redosled CH1–CH9, tabela tvrdnja→dokaz→status, rečenice za dopunu

**1. Zamenski tekst za CH1, §1.3–1.4**

### 1.3 Istraživačka pitanja

**IP1.** Koja odstupanja između dokumentovanog i zabeleženog izvršavanja optimizacionih biblioteka utiču na računovodstvo evaluacija, prijavljene rezultate i reproduktivnost, i koliko se njihov detekcioni status prenosi sa sintetičkih funkcija na AC dispečing? Osnova su I49–I52 i korektivna studija I55.

**IP2.** U kojim ispitanim uslovima GAdapt ostvaruje prednost prema konfiguracijama iz mentorovog benchmarka kada se odvojeno mere efikasnost po stvarnim evaluacijama, završna tačnost i rizik loših ishoda? S0 i E daju različite ishode zamrznutog pravila; rezultat zavisi od mere i ispitane transformacije.

**IP3.** Da li unapred određene intervencije — preset, diferencijalni krosover, hibrid i kompenzaciona mutacija — ispunjavaju svoje kriterijume poboljšanja? E2 daje negativne, E3 mešovite rezultate; E4 ostaje otvorena. Poređenja celih konfiguracija ne identifikuju pojedinačni uzročni mehanizam.

**IP4.** Da li relativni učinak adaptivne i podešene fiksne politike mutacije zavisi od rukovanja ograničenjima na ispitanom diskretnom ORPD-u, i kakve su granice prenosa tog nalaza? H56a je mali lokalni nalaz, praktično zasnovan na case14. I61 i I63 završeni su STOP-om bez ocenjivanja svojih hipoteza; I63-D (završena) daje deskriptivnu procenu θ₆₃ = 0,0139 [−0,0090; 0,0372], istog znaka kao I56, ali male i neprecizne.

**IP5.** Kakav je položaj GAdapt-a i hibrida prema izabranim konkurentima na ORPD-u, i da li ugrađene standardne tehnike za ograničenja potvrđeno ubrzavaju dostizanje cilja? I57 je opisna; I58/I60 nisu potvrdile ubrzanje, I59 je razvojni NO-GO, a I64-I/I2 ostaju otvorene.

### 1.4 Doprinosi

Doprinosi su ograničeni empirijski nalazi i proverene softverske funkcionalnosti.

1. **Instrumentovana replikacija i proširenje mentorovog benchmarka.** S0/E razdvajaju efikasnost, završnu tačnost i repni rizik. S0 podržava usku prednost u efikasnosti; E daje suprotan ishod zamrznute H64a. Rezultati ne ustanovljavaju opštu superiornost ili industrijsku spremnost.
2. **Alat i empirijski nalazi o integritetu evaluacija.** I49–I52/I55 dokumentuju odabrana svojstva izvršavanja 21 bibliotečke konfiguracije, konkretne dijagnoze i ograničenja detektora. Saglasnost statusa 19/21 uključuje saglasna odsustva; C1 nije specifičan detektor skrivenih proba.
3. **Lokalna procena interakcije politike mutacije i ograničenja.** I56 podržava H56a: θ = +0,0205, 95% interval [0,0020; 0,0396], uz šest degenerisanih blokova. Mehanizam preko skalarnih signala nije potvrđen. I61 STOP i I63 STOP ostavljaju nalaz bez ostvarene konfirmatorne replikacije.
4. **Dokumentovane opcije i granice njihove koristi.** Standardne tehnike za ograničenja i opcioni operatori imaju implementacione provere; I58/I60 ne potvrđuju ubrzanje, E2 pokazuje pogoršanje, a E3 ne ispunjava ukupan kriterijum podrške. Zaseban doprinos GAdapt faze hibrida nije identifikovan.

Originalnost se vezuje za konkretne dokaze, dijagnoze i njihovu sintezu. Ne tvrde se nova optimizaciona metoda, teorema, prvenstvo evaluacionih postupaka niti validiran selektor algoritma zasnovan na κ.

**2. Redosled i naslovi poglavlja**

| Poglavlje | Sadržaj i izvor |
|---|---|
| **CH1. Uvod: pitanja, doprinosi i granice dokaza** | Postavlja empirijska pitanja i ograničava tvrdnje prema sintezi CH2–CH8 i beleškama mentora. |
| **CH2. Integritet evaluacija optimizacionih biblioteka** | Prikazuje alat, validaciju, nalaze i ograničenja detekcije iz I49–I52/I55 i rukopisa revizije integriteta. |
| **CH3. Mentorov benchmark: efikasnost, tačnost i rizik** | Prikazuje S0/E i ishode intervencija E2/E3, uz otvoreno mesto za E4; izvor su sadašnji CH8 i odgovarajući izveštaji I64. |
| **CH4. Dijagnostika GAdapt-a na infrastrukturnim modelima** | Razdvaja potvrđena svojstva implementacije od neidentifikovanih uzroka zaostatka prema I42–I48/I53 i sadašnjem CH2. |
| **CH5. Diskretni ORPD: model i eksperimentalni dizajn** | Definiše kontrole, ograničenja, reference i estimande prema sadašnjem CH3 i protokolu I56. |
| **CH6. Lokalna interakcija i granice replikacije** | Prikazuje I56, STOP ishode I61/I63 i završenu deskriptivnu I63-D prema sadašnjem CH4, §7.9 i izveštajima. |
| **CH7. Spoljna poređenja i prenos na ORPD** | Prikazuje opisnu I57 i rezerviše zaključke I64-I/I2 do završetka provera, prema sadašnjem CH5 i zamrznutim specifikacijama. |
| **CH8. Bibliotečka implementacija i provere korisnosti** | Povezuje implementaciju sa nepotvrđenim ubrzanjem I58/I60, razvojnim NO-GO I59 i odstupanjem D1, prema sadašnjim CH6/CH7. |
| **CH9. Sinteza nalaza, pretnje validnosti i zaključak** | Objedinjuje statuse dokaza iz prethodnih poglavlja i razdvaja istraživačke nalaze od preporuka za primenu. |

**3. Zastarele rečenice i zamene**

Oznake poglavlja u ovoj listi odnose se na postojeće datoteke.

- **CH1, napomena:** „Napisan pre rezultata studija I56–I59; doprinosi su formulisani uslovno i biće usklađeni sa ishodima bez naknadnog proširivanja tvrdnji.“  
  **Zamena:** „Usklađeno sa završenim I56–I61, I63 STOP i S0/E/E2/E3; I64-I/I2, I63-D i E4 ostaju otvorene.“

- **CH1, doprinos 2:** „Ishod se prijavljuje kakav god da je, uključujući i ‘interakcija nije otkrivena pri ovoj snazi’.“  
  **Zamena:** „H56a je lokalno podržana; I61 i I63 završeni su STOP-om bez konfirmatornog zaključka o prenosu.“

- **CH2, napomena:** „Poglavlje motiviše istraživanje i ne nosi tvrdnju o originalnosti.“  
  **Zamena:** „Evaluacioni postupci imaju prethodnike; empirijski doprinos čine konkretni nalazi, dijagnoze i ograničenja provera.“

- **CH3, §3.1:** „U prethodnim poglavljima videli smo da GAdapt na glatkom, kontinualnom dispečingu zaostaje za CMA-ES za nekoliko redova veličine.“  
  **Zamena:** „U I47 razlika se odnosila na jaz penalizovanog skora pri 3000 PF poziva; na case14–case57 nijedna metoda nije našla izvodljivost.“

- **CH3, §3.4:** „Najzad, rezultat ove studije je empirijsko znanje o jednoj biblioteci na jednoj klasi problema; praktična korist ugrađene opcije za rukovanje ograničenjima testira se zasebno, konfirmatorno, na svežim mrežama (I58) i u drugom domenu (I59).“  
  **Zamena:** „I58/I60 nisu potvrdile ubrzanje ugrađenih opcija; I59 nije stigao do potvrde.“

- **CH4, §4.4:** „Ovaj nalaz nije bio predmet preregistrovane hipoteze i ne sme se tumačiti konfirmatorno; on je kandidat za sledeću preregistrovanu proveru.“  
  **Zamena:** „Opisni ε nalaz motivisao je I60, koja nije potvrdila prenos koristi.“

- **CH4, §4.5:** „Uzrok je u definiciji cilja i procenjivača (na nekim scenarijima cilj je nedostižan u 12.000 poziva), ne u veličini budžeta.“  
  **Zamena:** „Razvojna pokretanja nisu zadovoljila pravilo izbora budžeta; nedostizanje ne dokazuje nedostižnost cilja niti isključuje uticaj budžeta.“

- **CH5, §5.8:** „Njena praktična korisnost proverava se zasebno u I58 i I59, prema unapred zamrznutim protokolima, bez pretpostavljanja povoljnog ishoda iz nalaza I57.“  
  **Zamena:** „I58/I60 nisu potvrdile ubrzanje; H59 je nedostupna posle razvojnog NO-GO.“

- **CH6, uvod:** „Opisuje opt-in funkciju koja je razvijena i recenzirana dok je studija I56 trajala; u biblioteku se unosi tek posle studija I56 i I57, a njena korisnost se konfirmatorno proverava u I58 i I59.“  
  **Zamena:** „Opcija je ugrađena; provere I58/I60 nisu potvrdile ubrzanje, a I59 nije izvršio potvrdu.“ Isti status zamenjuje buduću formulaciju u §6.5.

- **CH7, §7.9:** „Kriterijum se sa 1000 simulacija ne može ispuniti ni za test tačne veličine 5%, što je greška dizajna zamrznutog pravila, a ne podatak o H56a.“  
  **Zamena:** „I63 nije zadovoljio zamrznuti kriterijum kalibracije; zahtev za gornju granicu stope greške problematičan je pri nominalnoj veličini testa, ali nije matematički nemoguć ishod simulacije.“

- **CH7, §7.9:** „H56a ostaje lokalni, nereplikovan nalaz; nijedan naknadni naslednik se ne planira.“  
  **Zamena:** „H56a ostaje lokalni nalaz bez konfirmatorne replikacije; I63-D ima isključivo deskriptivan status.“

- **CH7, završetak:** „Ova dva koraka odgovaraju na različite preostale potrebe: I63 proverava ponovljivost empirijske interakcije, a I62 praktičan položaj biblioteke prema jačim poređenjima.“  
  **Zamena:** „I63 je završen STOP-om; I62 ostaje nezamrznut predlog bez rezultata.“

**4. Tabela tvrdnji za završnu sintezu**

| Tvrdnja | Dokaz | Status |
|---|---|---|
| Uža prednost GAdapt-a u efikasnosti u S0 | ΔA = 0,164/0,204/0,047; simultane donje granice > 0 | confirmed |
| H64a prema zamrznutom pravilu E | Tri CMA konfiguracije imaju veći A | opposite |
| Rangiranje zavisi od mere i transformisane varijante | E: različiti obrasci A, medijane i CVaR | descriptive |
| Preset ostvaruje zadato poboljšanje | H64b nije podržana | undecided |
| Diferencijalni krosover ispunjava kriterijume E2 | H64e1/e3 suprotne; e2 nerazrešena | opposite / undecided |
| Hibrid ispunjava kriterijume E3 | g1 podržana; g2 suprotna; g3 nerazrešena | confirmed / opposite / undecided |
| Lokalna interakcija H56a | I56: θ = 0,0205; šest degenerisanih blokova | confirmed |
| Mehanizam preko skalarnih signala | H56b nije podržana | undecided |
| Ostvarena konfirmatorna replikacija | I61: izbor budžeta; I63: kalibracija | STOP |
| FR/ε ubrzavaju dostizanje prema kazni 1000 | I58/I60 intervali obuhvataju nulu | undecided |
| Telekom potvrda koristi | I59 razvojni NO-GO | STOP |
| Prenos detekcionog statusa | I52: 19/21, uključujući odsustva | confirmed |
| Opšta industrijska spremnost | Nije ustanovljena postojećim studijama | undecided |

**5. Rečenice za dopunu po završetku otvorenih studija**

**I64-I:** „Na osam ORPD ćelija pri 12.000 stvarnih PF poziva, GAdapt-M ima verovatnoću nalaženja izvodljivosti 0,746 i CVaR₀,₉ 0,2973; simultani kontrasti daju H64c = neodlučena i H64d = suprotna. Zaključak važi za ispitane konfiguracije i ne ustanovljava industrijsku spremnost.“

**I64-I2:** „Za hibrid je CVaR(M) − CVaR(H) = −0,0799 [−0,2656; 0,1058] i CVaR(IPOP) − CVaR(H) = −0,1253 [−0,2502; −0,0004]; razlike izvodljivosti P(H) − P(M) = −0,0042 [−0,0355; 0,0271] i P(H) − P(IPOP) = −0,0292 [−0,0643; 0,0059]; H64h1 = neodlučena, H64h2 = suprotna (napomena: polje `i_run_sha256` u I2 arhivi je prazno). Zaseban doprinos GAdapt faze ostaje neidentifikovan.“

**I63-D:** „Deskriptivna procena θ₆₃ iznosi 0,0139, sa 95% intervalom [−0,0090; 0,0372] i 90% intervalom [−0,0052; 0,0332]; smer je isti kao u I56, ali je procena mala i neprecizna (case30 −0,006; case39 +0,034; case24_ieee_rts +0,014). Estimand se razlikuje od H56a; rezultat ne menja I63 STOP niti ostvaruje konfirmatornu replikaciju.“

**I64-E4:** „Posle zamene svih neispravnih `resample` zapisa, jedna simultana porodica od sedam kontrasta daje H64k1–k5 redom: neodlučena, podržana, neodlučena, neodlučena i suprotna; jezgro H64k1–k4 nije podržano. Poređenje sa `permuted` odnosi se na kompletne režime, `ungated` ostaje opisna kontrola, a algoritamska originalnost i industrijska korist nisu ustanovljene.“