# H6: karakterizacija zavisnosti adaptacije od predstavljanja troška — prior-art audit (2026-10-28)

Izvor: literature-auditor (adversarijalno), po Codex 076 §2. DOI proveravani na Crossref-u (osim Auger & Hansen 2016, 429: NEPROVERENO, ne oslanjati se).
**Zaključak: novina NIJE USTANOVLJENA; NO-GO** za studiju „dokaz + predikcija“ u zadatom obliku.
- Invarijantna polovina = poseban slučaj Storch 2005/2006 Teorema 5 (rank-based algoritmi su invarijantni na rastuće g): 10.1145/1068009.1068151, 10.1007/s10710-006-9004-8.
- Neinvarijantna polovina + posledica na vreme izvršavanja = manja varijanta Storch §3 (PathPeak) i Neumann/Oliveto/Witt 2009 (10.1145/1569901.1570016), Happ i sar. 2008 (10.1145/1389095.1389277); tvrdnja za kontrolu parametara već u Fialho/Schoenauer/Sebag 2010 (10.1145/1830483.1830619).
- Doerr & Winzen (10.1007/s00453-012-9684-9), Atamna/Auger/Hansen (10.1016/j.tcs.2018.10.006, objavljeno 2020), Sakamoto & Akimoto (10.1162/evco_a_00310), Runarsson & Yao (10.1109/4235.873238), Coello (10.1016/S0045-7825(01)00323-1).
- Statistika GAdapt-a (log((c−c_min)+1), raspon, odnos prema generaciji 0) je invarijantna na pomak, ne na pozitivno skaliranje (zbog +1), slepa na unutrašnje troškove: elementarna algebra, ne doprinos.
- Jači oblici koji bi mogli biti novi (nijedan nije proveren do kraja): (a) tačna grupa invarijantnosti uz dihotomiju za hitting time; (b) zakon praga za kaznu λ: λ* iznad kog se signal adaptacije zasiti i menja red očekivanog broja evaluacija, za f + λ·v (preostaje samo ovo kao uska mogućnost; traži posebnu pretragu literature o adaptivnim kaznama); (c) pozitivan rezultat sa rangovnom zamenom signala (protivreči K6/Jump_k).
Posledica: bez (a) ili (b) pravac se zatvara. Ukupno odbačenih kandidata: 13+.

## Dodatak (2026-10-28): jači oblik (b) — zakon praga kazne λ* za signal adaptacije — NIJE USTANOVLJEN, NO-GO
Adversarijalna provera (literature-auditor; DOI proveravani na Crossref-u, osim Lemonge & Barbosa 2004 — NEPROVERENO):
- Zhou & He 2007 (10.1109/TEVC.2006.888929): vreme prvog pogotka EA nad f + λ·v prelazi iz polinomnog u eksponencijalno zavisno od λ (kanal: selekcija).
- Runarsson & Yao 2000 (10.1109/4235.873238) i Li & Zhang 2015 (10.1007/s10589-014-9676-6): eksplicitni kritični/minimalni λ iz veličina instance (kanal: rangiranje).
- Atamna/Auger/Hansen (10.1016/j.tcs.2018.10.006; 10.1145/3040718.3040732), Arnold & Porter 2015 (10.1145/2739480.2754813): adaptivni faktor kazne spregnut sa adaptacijom koraka (kontinualno).
- Adaptivne kazne iz statistike populacije: Farmani & Wright 2003 (10.1109/TEVC.2003.817236), Tessema & Yen 2006, Coit-Smith-Tate 1996, Ben Hadj-Alouane & Bean 1997, ASCHEA, Takahama-Sakai ε; Kramer & Schwefel 2006 (prerano smanjenje koraka, kvalitativno).
- Uzak neproveren deo: teorema o redu veličine gde je selekcija invarijantna na λ, pa promena dolazi samo iz numeričkog signala koji postavlja jačinu mutacije. Slabosti: prag je algebra (λ* ≈ Δf₀/Δv₀); broj mutacija je ograničen (1..N/5), pa je promena reda verovatno moguća samo veštačkom konstrukcijom (K6: GAdapt ≈ statička mutacija na Jump_k); u I56 mehanizam kroz numeričke signale nije potvrđen (H56b, SP-T).
- Odluka (2026-10-28): NO-GO. Ukupno odbačenih kandidata za metodu/doprinos: 14.
