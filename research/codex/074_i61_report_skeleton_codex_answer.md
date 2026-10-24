# ITERATION61: replikacija interakcije H56a (KOSTUR IZVEŠTAJA)

**Status: KOSTUR PRE UVIDA U REZULTATE.** Izvori: [zamrznuti protokol](research/ITERATION61_PROTOCOL.md), [izvršni kod](research/iteration61_replication.py), [I58 stilski obrazac](research/ITERATION58_REPORT_SR.md). Nijedan I61 rezultat ni log nije otvoren. Sve vrednosti ostaju `[UPISATI]`; nedostignute faze označiti „nije izvršeno“, nezapisane ključeve „nedostupno“.

## 1. Pitanje, domet i izvršavanje

Da li AD-N relativno više gubi prema podešenom FX-T pod FR nego pod SP? I61 konceptualno replicira pozitivan H56a kontrast na case30, case39 i case24_ieee_rts, R=17, sa novim scenarijima. Koristi I56 CHT instrument, `constraint_handling=None`, razvojno izabrane budžete i globalni FX-T vektor zasebno za SP/FR.

Razvoj: j=0,1; test: j=2,3,4. Navesti zadržane scenarije, izuzimanja bez zamene, biblioteku, gate, heševe, trajanje i eventualna odstupanja. Redosled: gate → dev_ref → select_b → fxt → stopcheck → rehearsal → power → test_ref → test → check → analyse.

Kontekst centralne tvrdnje: **H58/H60/H59 = N/N/nedostupno**. N označava neispunjen uslov podrške, bez automatskog dokaza odsustva efekta.

## 2. Zamrznuta pravila odlučivanja — doslovno

**Instance i reference (§2, §4):**

> Potrebna su oba razvojna i najmanje jedan test scenario svake mreže; inače STOP.

> Bez izvodljive reference cilj je samo izvodljivost; bez nijedne uspešne reference STOP.

**Gate (§3):**

> Svako nepoklapanje blokira trenutnu biblioteku; tada isti gate na `17e9ce7` u odvojenom stablu.

**Budžet i komparator (§5–§6):**

> B prolazi ako je medijana T_B **za svaku od dve grane na svakom razvojnom scenariju** u [0,3; 0,8].

> Po mreži se bira najmanji prolazni B; bez prolaznog B za bilo koju mrežu: STOP (bez proširivanja skupa mreža ili budžeta).

> Nepotpuna kalibracija = STOP.

**Proba i snaga (§7):**

> Svaka mreža mora imati: medijanu T obe AD-N grane u [0,3; 0,8] na oba scenarija; ≥ 20% dostizanja u svakoj grani; pozitivnu empirijsku varijansu kontrasta d. Neprolaz = STOP bez ponovnog izbora.

> Snaga: zahteva se svih 20 potpunih četvorovektora probe po mreži; inače STOP.

> zahteva se stroga dostižnost, greška sredine ≤ 10⁻⁸ i ESS_i = 1/Σ_u w_iu² ≥ 10.

> bira se najmanji n sa dvostranom 95% Wilsonovom donjom granicom snage ≥ 0,8.

> Izabrani n se nezavisno potvrđuje sa 1000 eksperimenata i 20.000 ponavljanja (seme 61024): potrebno ≥ 825 pozitivnih primarnih zaključaka.

> Nula θ = 0 se nezavisno kalibriše sa 1000 eksperimenata i 20.000 ponavljanja (seme 61025): dozvoljeno ≤ 36 pozitivnih primarnih zaključaka.

> Nedostižna alternativa/nula, ESS ispod praga, n > 480 ili neprolaz potvrde/kalibracije = STOP bez pokušaja većeg n.

**Zaključivanje (§8):**

> **H61 podržana** ako je donja granica 95% intervala > 0; gornja < 0 podržava suprotan smer.

> **Praktična ekvivalencija** prosečnog kontrasta ako je 90% interval strogo unutar [−0,02; +0,02] (TOST-analogno, bootstrap aproksimacija). Oznake smera i ekvivalencije prijavljuju se odvojeno (mogu važiti istovremeno); ostalo = neodlučno. Tvrdnja „efekat ≥ 0,02“ zahtevala bi donju granicu > 0,02.

> STOP ne daje empirijski zaključak o H61.

**Dostupnost zaključka (§10):**

> Prazna ćelija onemogućava primarno zaključivanje.

> neuspeh = nedostupan zaključak.

## 3. Razvoj, zamrzavanje i provera

U tabelama `F:$.x` znači JSON putanju u `research/results/iteration61/F.json.gz`; `m`=mreža, `c`=CHT, `j`=scenario. Svaki red ima vrednost `[UPISATI]`.

| Stavka | Tačan izvor |
|---|---|
| Roster i OPF izuzimanja | `roster:$.dev`, `$.test`, `$.excluded` |
| Gate i izabrana biblioteka | `gate:$.passed`, `$.selected`, `$.library_root` |
| Razvojni L* / cilj izvodljivosti (`null`) | `dev_ref:$.references["m|j"]` |
| Izabrani B; sve četiri medijane po kandidatu | `select_b:$.chosen[m]`; `$.medians["m|B"]["c|j"]` |
| Globalni FX-T vektori | `fxt:$.chosen.SP`, `$.chosen.FR` |
| Validacija prekida | `stopcheck:$.decision`, `$.attained`, `$.mismatches` |
| Proba, po mreži | `rehearsal:$.criteria[m].{complete,medians,attained,variance,passed}`; `$.passed` |
| Naginjanje alternative/nule | `power:$.alternative`, `$.null`: `{lam,weights,error,ess,max_weight,weighted_attainment}` |
| Preliminarna snaga | `power:$.screening["n"].{positives,wilson}` |
| Potvrda i kalibracija nule | `power:$.confirmation.{positives,wilson}`, `$.null_calibration.{positives,wilson}` |
| Konačan n / prolaz | `power:$.chosen_n`, `$.passed` |
| Zamrznuti izbori i heševi | `manifest_frozen:$.choices`, `$.hashes` |
| Test reference | `test_ref:$.references`, `$.excluded` |
| Test i vezivanje referenci | `test:$.choices`, `$.test_ref_sha256`, `$.records` |
| Nezavisna provera | `check:$.expected`, `$.rows`, `$.failures`, `$.bound` |

`stopcheck=allowed` dozvoljava prekid pri cilju; `blocked` ili `inconclusive` zahteva puni budžet. To samo po sebi nije STOP studije niti ishod H61. Rani STOP u `power` može ostaviti kasnije ključeve nezapisane.

## 4. Primarni ishod, izuzimanja i opisno

T=h/B, odnosno 1 pri nedostizanju; d=[T(AD,FR)−T(FX,FR)]−[T(AD,SP)−T(FX,SP)]. θ daje jednake težine mrežama i preostalim scenarijima. Bootstrap: 20.000 celih uparenih četvorovektora, stratifikovano po ćeliji, seme 61; oba intervala iz istih izvlačenja.

| Izveštajna tabela — sve vrednosti `[UPISATI]` | JSON putanje u `analysis` |
|---|---|
| θ; 95% CI; 90% CI; tri nezavisne oznake | `$.H61.{estimate,ci95,ci90,supported,opposite,equivalent}` |
| Planirano/potpuno/izuzeto; globalna stopa i oznaka >5% | `$.planned_units`, `$.complete_units`, `$.excluded_units`, `$.exclusion_rate`, `$.exclusion_flag` |
| Po ćeliji: planirano, izuzeto, stopa; prazne ćelije | `$.per_cell["m|j"].{planned,excluded,rate}`, `$.empty_cells` |
| Osetljivost: procena, intervali i oznake | `$.sensitivity.{estimate,ci95,ci90,supported,opposite,equivalent}` |
| Opisno: srednji T, dostizanje, izvodljivost; d i n | `$.descriptive["m|j|c|arm"].{mean_T,attained,feasible}`; `["m|j|d"].{mean,n}` |

Osetljivost se prikazuje posle **svakog** izuzimanja: uspešni ishodi ostaju, samo nedostupne grane dobijaju T=1. `sensitivity=null` znači da nije aktivirana. Opisna je; ne nadomešta praznu ćeliju.

## 5. Unapred napisane grane prekida

Za svaku granu upisati konkretan razlog i poslednju završenu fazu.

| Grana | Tumačenje i posledica za H56a |
|---|---|
| §2: nedostaje razvojni ili svi test scenariji neke mreže | Roster nije podoban; H56a ostaje bez replikacione ocene. |
| Gate ne prolazi ni na rezervnoj biblioteci | Instrument nije potvrđen; nema novog dokaza o H56a. |
| §4: nema uspešne reference | Cilj nije uspostavljen; H56a nije ocenjena. |
| §5: nema B ili nepotpune medijane | Nije uspostavljen dozvoljeni informativni budžet; bez zaključka o H56a. |
| §6: nepotpun FX-T | Komparator nije kalibrisan; bez ocene H56a. |
| §7: proba pada, uključujući nepotpunih 20 vektora | Razvojni uslovi nisu ispunjeni; H56a nije testirana potvrdno. |
| Alternativa ili nula nedostižna | Empirijska kalibracija nije moguća; to ne pobija H56a. |
| ESS<10 ili greška >10⁻⁸ | Naginjanje nije prihvatljivo; bez empirijske ocene H56a. |
| Nema prolaznog n≤480 | Dozvoljeni dizajn nema zahtevanu simuliranu snagu; H56a ostaje neocenjena. |
| Potvrda <825, kalibracija nule >36 ili oba | Dizajn nije potvrđen; nema potvrdnog testa H56a. |
| Check neuspešan/nepotpun/nevezan heševima | Zaključak nedostupan; numerički ishod ne koristiti za H56a. |
| Narušeno poreklo, zamrzavanje ili struktura zapisa | Integritet nije potvrđen; H56a bez validne nove ocene. |
| Prazna test ćelija; `H61=null` | Primarno zaključivanje nedostupno; osetljivost ne potvrđuje H56a. |

**U svakoj grani:** uz N/N/nedostupno nema nove potvrde centralne tvrdnje; STOP nije N niti dokaz protiv efekta.

## 6. Unapred napisani zaključci validne analize

| Oznake | Tekst zaključka i posledica za tezu |
|---|---|
| supported, bez equivalent | Pozitivna interakcija replicirana; H56a dobija uslovnu podršku. N/N/nedostupno ostaje: nema potvrde opšte koristi adaptacije ili ugrađenog FR. |
| opposite | Podržan suprotan smer; H56a nije replicirana i njena generalizacija je oslabljena. Ako važi i equivalent, suprotan efekat je praktično mali. |
| equivalent, bez smera | Prosečni kontrast praktično ekvivalentan nuli unutar ±0,02; nema podrške pozitivnoj H56a niti širenju centralne tvrdnje. |
| supported+equivalent | Pozitivan, praktično mali kontrast; H56a replicirana po smeru, uz ograničenu veličinu. N/N/nedostupno ne menja se. |
| inconclusive | Nema podrške smeru ni ekvivalenciji; H56a nije potvrđena niti pobijena, centralna tvrdnja ostaje ograničena. |

Ograničenja svih grana: fiksne topologije, novi scenariji na I58 mrežama, uslovne reference i razvojna selekcija; različito podešavanje FX-T za SP/FR ulazi u kontrast. Pozitivna interakcija sama ne pokazuje superiornost adaptacije niti efekat ≥0,02.