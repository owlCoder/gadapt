# ITERATION59: FR naspram kazne u telekom modelu — skelet izveštaja

**Status: SKELET, bez uvida u rezultate.** Rezultati I59 i logovi I59/I60 nisu otvarani; fajlovi nisu menjani. Vreme nastanka rezultata nije proveravano. Merodavni su [zamrznuti protokol](/Users/danijel/Desktop/gadapt/research/ITERATION59_PROTOCOL.md) i [pojašnjenja](/Users/danijel/Desktop/gadapt/research/ITERATION59_CLARIFICATIONS.md), ispred predloga. Struktura prati izveštaj I58.

## 1. Pitanje, instance i izvršavanje

Da li integrisani FR, G1, skraćuje ograničeno vreme do cilja prema G0, kazni f + 1000·V? Razvoj: Abilene i PDH; potvrda: Polska, Nobel-Germany i Nobel-US. GÉANT nije deo H59.

Model koristi originalne statičke zahteve, deljive tokove i zajednički kapacitet oba smera. Moduli i cene jesu sintetičke pretpostavke planiranja. Navesti raniju izloženost topologijama i LP probe.

Protokol:

> Nasleđuju se I58 kontrole izvršavanja, populacija 32, isključeno sondiranje i imigracija. Početne populacije su identične (asercija); bez ubacivanja SP/MILP rešenja.

> p = 0: izbor, 10 parova; p = 1: razvojna validacija, 10 novih parova; p = 2: potvrda, 15 parova; s = 1..10, odnosno 1..15. Seju se svi RNG-ovi; bootstrap seme 59.

## 2. Zamrznuta pravila odlučivanja

**Evaluacija i neuspeh:**

> Svaki uspešan LP mora zadovoljiti elastične jednačine, kapacitete i granice do 1e-7. V ≤ 1e-8 postaje nula samo ako tok zadovoljava i PUNE zahteve, na svim čvorovima, do 1e-7. Broji se svaki poziv, uključujući inicijalizaciju, duplikate i neuspehe; bez keširanja i ranog prekida. Trajna greška posle jednog ponavljanja istim semenom sprečava primarni zaključak.

**Reference i cilj:**

> Nezavisno se proverava incumbent. Razvojne reference prethode razvoju; potvrdne slede posle zamrzavanja (B, ε), pre potvrdnih putanja.

> Cilj: V = 0 i C ≤ (1 + ε)C*. **Bez sertifikovanog optimuma na bilo kojoj potrebnoj instanci: nema H59 zaključka**; granice ostaju opisne. Zahteva se i (1 + ε)C* < C_sp; inače se cilj označava trivijalnim, bez zamene instance ili ponovnog podešavanja.

P2:

> „Sertifikovano“ = status 0 I provera svedoka (celobrojnost, granice, ravnoteže u SVIM čvorovima, kapaciteti, rekonstruisan trošak = `res.fun`) I nema neočekivanih upozorenja.

**Razvojni izbor:**

> Putanje do 30.000 poziva. Iz prefiksa se bira najmanji B ∈ {3000, 10.000, 30.000}, zatim najmanji ε ∈ {0,05; 0,10; 0,20}, sa zbirnim G0/G1 dostizanjem 20–80% na SVAKOJ razvojnoj mreži. Izabrani par mora proći isti uslov na novim validacionim semenima. Neuspeh znači NO-GO; nema ponovnog izbora.

**Analiza:**

> T = min(prvi pogodak/B, 1); nedostizanje daje 1. Jednake težine mreža; upareni bootstrap unutar mreža, 20.000 ponavljanja, percentilni 95% interval. **H59: θ = E[T_G1 − T_G0] < 0, podržana samo intervalom potpuno ispod nule.** Potpuno cenzurisani blokovi se zadržavaju.

**Provera:**

> Nezavisan proverivač rekonstruiše trošak, granice i tokove za vraćena rešenja i svedoke koji određuju cilj/T.

P6:

> redosled faza: `development` → `confirmation` → `check` → `analyse`; H59 se računa samo ako je razvoj GO, reference sertifikovane I nezavisno proverene, inventar tačan (3 mreže × 15 semena × 2 grane, jedinstveni, isti budžet), nema trajnih neuspeha i `check` nema grešaka. Cilj bez dodatne tolerancije (C ≤ (1 + ε)C*). Trivijalni ciljevi se označavaju i za razvojne mreže posle izbora ε (bez zamene).

## 3. Tabele za popunjavanje

Oznake artefakata iz koda: D=`development.json`, F=`confirmation_refs.json`, C=`confirmation.json`, K=`check.json`, A=`analysis.json`; na disku imaju nastavak `.gz`. `n` označava mrežu, `i` indeks zapisa. Svaku parametrizovanu ćeliju ponoviti za odgovarajuće mreže/zapise. Neproizveden artefakt označiti „nije proizvedeno“.

| JSON putanja | Ćelija |
|---|---|
| D.decision | ⟦D.decision⟧ |
| D.chosen | ⟦D.chosen⟧ |
| D.trivial[n] | ⟦D.trivial[n]⟧ |
| D.selection[i].{task,ok,calls,hits} | ⟦po jedna ćelija za svaki navedeni ključ⟧ |
| D.validation[i].{task,ok,calls,hits} | ⟦po jedna ćelija za svaki navedeni ključ⟧ |
| F.chosen / C.chosen | ⟦F.chosen⟧ / ⟦C.chosen⟧ |
| F.trivial[n] / C.trivial[n] | ⟦F.trivial[n]⟧ / ⟦C.trivial[n]⟧ |
| C.records[i].{task,ok,calls,errors,hits} | ⟦po jedna ćelija za svaki navedeni ključ⟧ |
| D/F/C.references[n].certified | ⟦D/F/C.references[n].certified⟧ |
| D/F/C.references[n].usable | ⟦D/F/C.references[n].usable⟧ |
| D/F/C.references[n].{C,dual_bound,gap,independent} | ⟦po jedna ćelija za svaki navedeni ključ⟧ |
| K.rows / K.failures / K.bound | ⟦K.rows⟧ / ⟦K.failures⟧ / ⟦K.bound⟧ |

`K.rows` je niz, ne broj redova; broj izvesti kao njegovu dužinu. Zbirno razvojno dostizanje izvesti iz `hits`, po mreži, za izabrani B i ε; nije zaseban izlazni ključ.

| JSON putanja | Ćelija |
|---|---|
| A.chosen | ⟦A.chosen⟧ |
| A.development_decision | ⟦A.development_decision⟧ |
| A.certified | ⟦A.certified⟧ |
| A.development_certified | ⟦A.development_certified⟧ |
| A.choice_ok | ⟦A.choice_ok⟧ |
| A.provenance_ok | ⟦A.provenance_ok⟧ |
| A.inventory_ok | ⟦A.inventory_ok⟧ |
| A.checks_ok | ⟦A.checks_ok⟧ |
| A.development_trivial | ⟦A.development_trivial⟧ |
| A.trivial | ⟦A.trivial⟧ |
| A.persistent_failures | ⟦A.persistent_failures⟧ |
| A.H59 | ⟦A.H59⟧ |
| A.H59.estimate | ⟦A.H59.estimate⟧ |
| A.H59.ci | ⟦A.H59.ci⟧ |
| A.H59.supported | ⟦A.H59.supported⟧ |
| A.per_network[n].mean_d | ⟦A.per_network[n].mean_d⟧ |
| A.per_network[n].n | ⟦A.per_network[n].n⟧ |

## 4. Unapred napisana tumačenja

| Grana | Rečenica izveštaja |
|---|---|
| `NO-GO: no (B, eps) with 20-80% attainment on every development network` | Nijedan dozvoljeni par nije zadovoljio razvojni uslov; H59 zaključak je nedostupan, bez ponovnog izbora. |
| `NO-GO: validation seeds outside 20-80%` | Izabrani par nije prošao nova validaciona semena; potvrda se zaustavlja, bez ponovnog izbora. |
| `NO-GO: development optimum not certified/verified` ili potvrdni STOP | Potrebna referenca nije sertifikovana i nezavisno proverena; nema H59 zaključka, a granice ostaju opisne. |
| `NO PRIMARY: persistent execution failure in selection/validation` ili neprazan `persistent_failures` | Trajni izvršni neuspeh sprečava primarni zaključak. |
| Neuspešan `check`, `checks_ok`, `provenance_ok`, `choice_ok` ili `inventory_ok` | Uslovi valjanosti nisu ispunjeni; nema zaključka o H59. |
| Valjana analiza, `H59.supported=true` | H59 je podržana: ceo 95% interval je ispod nule. |
| Valjana analiza, `H59.supported=false` | H59 nije podržana; interval ne ispunjava zamrznuti uslov, što ne dokazuje jednakost ili odsustvo koristi. |
| `trivial[n]=true` | Cilj je označen trivijalnim; mreža se ne zamenjuje i podešavanje se ne ponavlja. |

`H59=null` označava nedostupan zaključak; nije isto što i `supported=false`.

## 5. Odstupanja i nepotpune programske zaštite

Prema [kodu](/Users/danijel/Desktop/gadapt/research/iteration59_telecom.py):

- Uslov `(1+ε)C* < C_sp` samo se označava kroz `trivial`; nije uslov `eligible`. Protokol ne daje zasebnu STOP granu za trivijalnost; ovu napetost prikazati izričito.
- Populacija 32 i imigracija 0 nisu eksplicitno zadate konstruktoru GA niti proverene; kod se oslanja na podrazumevane vrednosti, koje manifest beleži.
- P4 zahteva „ulaz evaluatora mora biti konačan ceo vektor u [0, 16]“, ali omotač zaokružuje ulaz pre provere.
- Ako LP vrati tačno `V=0`, neuspešna provera punih zahteva ne odbacuje tu nulu; uslovna naredba kontroliše samo pretvaranje u nulu.

To su nalazi pregleda koda, ne tvrdnje da su uticali na izvršavanje.

## 6. Zaključak prema Codex 052

Redosled je **H58/H60/H59**; H58=N, H60 ostaje nepoznat.

| H59 | H60=P | H60=N |
|---|---|---|
| P | **N/P/P:** ograničena korist ε u elektroenergetici i FR u telekomu. | **N/N/P:** potvrđena korist samo FR u telekom modelu. |
| N | **N/P/N:** potvrđena korist samo ε u elektroenergetici. | **N/N/N:** bez potvrđenog ubrzanja u tri studije. |
| Nedostupan | **N/P/?** | **N/N/?** |

Sve NO-GO, STOP i neuspešne zaštite pripadaju grani „neodlučno/prekinuto“ [mape 052](/Users/danijel/Desktop/gadapt/research/codex/052_thesis_outcome_map_codex_answer.md), bez pretvaranja u N. Ako je i H60 nedostupan, ostaje `N/?/…`.

P1 ograničava tvrdnju prema odgovarajućoj grani; P6 prikazuje sve ishode i razloge prekida. README ne izvodi preporuku iz prekinute studije. `constraint_handling` ostaje opt-in. Domet ostaje tri mreže, sintetički model i kazna 1000; I59 ne replikuje H56 interakciju niti dokazuje opštu superiornost.