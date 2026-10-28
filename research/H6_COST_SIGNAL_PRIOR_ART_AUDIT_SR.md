# H6: karakterizacija zavisnosti adaptacije od predstavljanja troška — prior-art audit (2026-10-28)

Izvor: literature-auditor (adversarijalno), po Codex 076 §2. DOI proveravani na Crossref-u (osim Auger & Hansen 2016, 429: NEPROVERENO, ne oslanjati se).
**Zaključak: novina NIJE USTANOVLJENA; NO-GO** za studiju „dokaz + predikcija“ u zadatom obliku.
- Invarijantna polovina = poseban slučaj Storch 2005/2006 Teorema 5 (rank-based algoritmi su invarijantni na rastuće g): 10.1145/1068009.1068151, 10.1007/s10710-006-9004-8.
- Neinvarijantna polovina + posledica na vreme izvršavanja = manja varijanta Storch §3 (PathPeak) i Neumann/Oliveto/Witt 2009 (10.1145/1569901.1570016), Happ i sar. 2008 (10.1145/1389095.1389277); tvrdnja za kontrolu parametara već u Fialho/Schoenauer/Sebag 2010 (10.1145/1830483.1830619).
- Doerr & Winzen (10.1007/s00453-012-9684-9), Atamna/Auger/Hansen (10.1016/j.tcs.2018.10.006, objavljeno 2020), Sakamoto & Akimoto (10.1162/evco_a_00310), Runarsson & Yao (10.1109/4235.873238), Coello (10.1016/S0045-7825(01)00323-1).
- Statistika GAdapt-a (log((c−c_min)+1), raspon, odnos prema generaciji 0) je invarijantna na pomak, ne na pozitivno skaliranje (zbog +1), slepa na unutrašnje troškove: elementarna algebra, ne doprinos.
- Jači oblici koji bi mogli biti novi (nijedan nije proveren do kraja): (a) tačna grupa invarijantnosti uz dihotomiju za hitting time; (b) zakon praga za kaznu λ: λ* iznad kog se signal adaptacije zasiti i menja red očekivanog broja evaluacija, za f + λ·v (preostaje samo ovo kao uska mogućnost; traži posebnu pretragu literature o adaptivnim kaznama); (c) pozitivan rezultat sa rangovnom zamenom signala (protivreči K6/Jump_k).
Posledica: bez (a) ili (b) pravac se zatvara. Ukupno odbačenih kandidata: 13+.
