**E2: FIX FIRST.** Pregled je urađen samo za čitanje; fajlovi nisu menjani.

1. **Hipoteze i porodica kontrasta**

[Specifikacija](/Users/danijel/Desktop/gadapt/research/ITERATION64_E2_SPEC.md:9) definiše tri hipoteze, ali **pet veličina koje određuju odluke**. Najjednostavnija ispravka jeste jedna simultana bootstrap porodica svih pet kontrasta, α = 0,05, 20.000 ponavljanja, seme 66. U svakom ponavljanju koristiti iste resamplovane indekse za sve konfiguracije unutar ćelije. Taj α pripada E2; nije automatski ukupni nivo greške celog I64 programa.

Za H64e2 usvojiti potpuno napisanu granicu **1,5**, a nedovršeno „1,25·...” izbrisati. Tačno pravilo glasi:

**H64e2 je podržana ako**  
`LB[A_D − A_M] ≥ −0,05` **i** `UB[C_D − 1,5·C_M] ≤ 0`,  
na orig+shift ćelijama, gde je C ponderisani prosek ćelijskih CVaR₀,₉. Ekvivalentno, drugi uslov je `LB[1,5·C_M − C_D] ≥ 0`. To dozvoljava do 50% veći rizik; naziv treba da navede tolerisanu štetu.

H64e1 mora zahtevati `C_M > 0`, jer dva nulta rizika nisu poboljšanje od 20%. Poboljšanje prema M samo po sebi ne znači zatvaranje jaza prema CMA. H64e3 testira **neinferiornost prema IPOP-u uz marginu 0,05**, ne ekvivalenciju niti celu CMA porodicu; njen CVaR ostaje opisan.

Za svaki uslov zamrznuti trostruku odluku: podržano ako odgovarajuća granica zadovoljava prag; suprotno ako ceo interval ostaje na neprihvatljivoj strani; inače neodlučeno. Nekonačne vrednosti ili nulta bootstrap varijansa blokiraju potvrdu. Neuspeh potvrđivanja nije automatski suprotan ishod.

2. **Uparivanje sa E arhivom**

Formule [cell_transform i seed_of](/Users/danijel/Desktop/gadapt/research/i64/e_study.py:57) odgovaraju E2: transformacija zavisi od `[64,3,c]`, a seme pokretanja iznosi `67.000.000 + 1000c + s`.

U dva nova procesa proverio sam identičnost svih 63 transformacije i 6.300 semena. Međutim, dostupni NumPy je **2.5.4**, dok E manifest beleži **1.26.4**. To potvrđuje determinizam sadašnjeg okruženja; istorijska bit-identičnost, naročito QR matrica Q, zahteva E numeričko okruženje. Dodatni nedostatak: `run_task` izračuna `info`, ali ga ne sačuva, pa arhiva nema neposredno zapisane o i Q.

Provereni su heševi svih 63 `run_part_*` prema komitu `ef067a7`, struktura 56.700 zapisa i SHA-256 zbirne arhive prema `analysis_v2`.

**Bibliotečko stablo nije identično E stablu:** promenjeni su `ga.py`, `ga_factory.py`, `definitions.py` i dodat `differential_crossover.py`. Diff podržava tvrdnju da je promena opt-in, ali tvrdnja „isti heš biblioteke” bila bi netačna. Dokumentovati dozvoljeni diff i proveriti reprodukciju arhiviranih blending tragova.

Različito vreme/proces samo po sebi ne poništava uparivanje metrika po broju evaluacija. Uparivati ključem `(cell, seed)`, uz iste funkcije, normalizatore, transformacije i proverenu semantiku baseline-a; ne rednim položajem zapisa.

3. **Restart i izolacija procesa**

[E runner](/Users/danijel/Desktop/gadapt/research/i64/e_algos.py:92) pravi nov GA i nove RNG tokove iz `[seed,k]`, dok `Budget` zadržava ukupan broj poziva i najbolje rešenje. `BudgetReached(BaseException)` prolazi kroz bibliotečki `except Exception`: taj deo je ispravan.

Blokirajući problem je ignorisanje rezultata `ga.execute()`. Biblioteka može internu grešku pretvoriti u `success=False`, a runner zatim restartuje. Proba je potvrdila da takve greške mogu potrošiti ceo budžet i završiti kao spolja uspešno pokretanje. Ispravka: proveriti `result.success`; neuspeh propagirati kao tehničku grešku, uz propisano jedno ponavljanje. Restartovati samo uspešan prevremeni završetak; beležiti razlog i broj restarta.

Za obećani nov proces po pokretanju potrebni su **`maxtasksperchild=1` i `chunksize=1`**. Postojeći E koristi 50 i 4; samo promena prvog parametra nije dovoljna.

4. **DifferentialCrossover**

[Implementacija](/Users/danijel/Desktop/gadapt/gadapt/operations/crossover/differential_crossover.py:16) ima ispravno ekvivarijantno **neograničeno predlaganje**:

`Q[m + F(a−b)] = Qm + F(Qa−Qb)`.

Tvrdnju ograničiti na taj korak. Koordinatna refleksija, diskretizacija, roditeljska raznovrsnost i kolonski mutacioni operatori ne daju rotacionu ekvivarijantnost celog algoritma.

- **Verovatnoća:** bazni `_mate_pair` ponavlja pokušaje dok `crossed=True`, povećavajući verovatnoću. Zato par konačno uvek prolazi diferencijalno ukrštanje; proba čak sa p=0 dala je pomerenu decu. Diferencijalni `_mate_pair` treba da izvrši jedan Bernoulli pokušaj, `random.random() < p`, i prihvati kopije kada pokušaj ne uspe. Zadržati završne updatere i metapodatke.
- **Refleksija:** modulo formula pravilno obrađuje višestruke prelaske granica, za konačne vrednosti i numerički predstavljiv period `2(high−low)`.
- **Mreža:** trenutno odsecanje može vratiti tačku van mreže: `[0,1]`, step=0,6, vrednost 1 → **1**, umesto 0,6. Naknadno zaokruživanje može prekršiti granice: `[0,06;0,16]`, step=0,1 → **0,2**. Koristiti `kmax=floor((high−low)/step)`, ograničiti celobrojni indeks k na `[0,kmax]`, pa vratiti `low+k·step`. Preciznost izvesti iz **low i step**, najbolje decimalnom aritmetikom; postojeći `decimal_places(step)` nije dovoljan. Uskladiti tretman veoma sitnih koraka sa `is_discrete`.
- **`step=None`:** pravilno ostaje kontinualan, bez zaokruživanja na početni `decimal_places=-1`.
- **Donori:** četiri uzorkovana člana mogu uključiti mother/father. Ako dokumentacija obećava „druge članove”, isključiti odgovarajuću bazu po identitetu i prilagoditi uslov dovoljne veličine skupa; inače precizirati dokumentaciju.
- **Mali skup:** postojeća rezervna grana daje interpolaciju, jer F≤1; ne ide „beyond”. Ispraviti opis. Jednaki roditelji daju nulti pomak.
- **Jedinstvenost:** isti roditelji generalno daju različitu decu zbog novih donora i F. Posle neuspelih pokušaja uključuje se mutaciona popravka, a završna grana dopušta duplikate. U E/E2 je jedinstvenost isključena.
- **Updateri:** `start_update` i `prepare_update` po promenljivoj pravilno održavaju postojeći API. Međutim, roditeljska raznovrsnost opisuje samo mother/father, zanemarujući donore. To dokumentovati; donorsku metriku bi trebalo zasebno definisati pre zamrzavanja.

5. **Tumačenje E**

Zamrznuti **H64a = opposite** ostaje ispravan: sva tri CMA ΔA intervala potpuno su negativna. „Dokazano” ovde znači statistički podržano zadatim bootstrap postupkom.

Rečenica „mentorova tvrdnja važi ako je izuzetak CMA porodica” **nije odbranjiva kao potvrda H64a**. Grupisanje je naknadno, a prednost nad presetom nije potvrđena. Prihvatljivo je samo opisati obrazac prema unapred navedenim konkurentima, uz eksplicitnu oznaku post hoc.

Izveštaj ne sme tvrditi opštu superiornost, ekvivalenciju preseta zbog nepodržane H64b, industrijsku spremnost ili da je krosover dokazan uzrok. Orig funkcije nisu sve separabilne; shift i rot koriste različite o, pa njihova razlika nije izolovan efekat rotacije.

Dodati razlaganje po funkciji/dimenziji i jasno razdvojiti jednake ćelijske od jednakih funkcijskih težina. Sa protokolskim težinama ROT GAdapt ima **A=0,6167, CVaR=0,0300**.

Iz arhive sam izračunao dodatnu, **post hoc** ROT porodicu: 24 simultana kontrasta, α=0,05, 20.000 ponavljanja. Za GAdapt−IPOP, ΔA≈−0,1463, interval **[−0,1593;−0,1332]**. I `(1+1)-ES` je efikasniji pod rotacijom; prema DE razlika A ostaje neodlučena. CMA ima bolji CVaR, dok razlike završnih medijana nisu razrešene. Time treba zameniti preširoko porodično tumačenje pre E2 FREEZE.