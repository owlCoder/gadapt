# Nezavisna (slepa) lista, krug 2 — Claude, 2026-10-28

Zapisano i komitovano PRE čitanja Codex 081 odgovora. Procene novine su moje i pre provere prior art-a; većina verovatno pada.

| # | Pitanje | Skica | Prior art za proveru | Moja procena |
|---|---|---|---|---|
| L1 | Tačna statistika uniknosti na mreži vrednosti: koliko stvarnih evaluacija štedi `ensure_unique_individuals` naspram keša, i uvodi li popravka duplikata pristrasnost u raspodelu mutacije? | formalni model „popravka odbijanjem“ na diskretnoj mreži; očekivani broj pokušaja kao funkcija popunjenosti; jedini efekat na putanju dolazi od pomeranja raspodele | Biedrzycki 2020 (darvinovska popravka), resampling/rejection u EA, tabu/memoizacija | 5–10% |
| L2 | Budžet-svesna samoadaptacija: raspored GAdapt-a zavisi od broja generacija, ne od preostalog broja evaluacija; da li povezivanje raspodele rasipanja sa preostalim budžetom daje garanciju „bez gubitka“ pri skraćenom budžetu? | dokaz monotonosti: skraćen budžet ne sme pogoršati unapred zadati rang | budžet-zavisne šeme (Jansen, Niewiadomski, NSGA-II budget-aware), „anytime“ raspored | < 5% |
| L3 | Predikcija pobednika (adaptivna vs podešena fiksna politika) iz jeftinih osobina instance (ELA/frakcija izvodljivih/rastojanje do granica) na ORPD: validirano „pravilo odabira politike“ | model + prospektivna provera na svežim mrežama | algorithm selection (Kerschke i sar. 2019), ELA | 5–10% |
| L4 | Prostor rešenja ORPD kao celobrojna rešetka: egzaktno prebrojavanje izvodljivog dela (uzorkovanje + sertifikat) da bi se mereno „dostizanje cilja“ prevelo u verovatnoću pogotka slučajnom pretragom (apsolutno težinsko merilo instance) | procena frakcije izvodljivih/dobrih tačaka sa intervalom; nezavisna baza za sve poređenje | random-search baseline (COCO), fitness landscape | 5% |

Moj izbor pre poređenja: nijedan jak; L1 (formalno, malo ali čisto) pa L4 (korisno kao merilo težine u tezi). Očekivanje: većina pada na gate-u ili je inženjerska/ablaciona.
