# Poglavlje 9. Smernice za primenu zasnovane na dokazima

*Nacrt, 30. oktobar 2026. Svaka stavka navodi studiju i meru; ništa ovde nije nova tvrdnja, već sažetak dokaza iz poglavlja 4, 7 i 8. Smernice nisu opšta industrijska preporuka: važe za ispitane funkcije, ćelije, konfiguracije i budžete.*

## 9.1 Šta znači „stabilan, tačan, primenjiv“ u ovom radu

Mentorov kriterijum je preveden u mere koje se mogu izračunati: **efikasnost** (ECDF površina A pri 12.000 stvarnih poziva), **tačnost** (medijana normalizovanog jaza), **stabilnost kao rizik lošeg ishoda** (CVaR₀,₉ ishoda L = g/(1+g)) i **izvodljivost** na ograničenim problemima (verovatnoća nalaska izvodljivog rešenja). Stabilnost kao ponovljivost istog semena i prag prihvatljivosti nisu dogovoreni sa mentorom (pitanje za sastanak).

## 9.2 Nalazi i smernice po situacijama

Svaka stavka daje nalaz (studija, mera, neizvesnost) i smernicu uz eksplicitnu granicu. Intervali obuhvataju samo varijaciju algoritamskih semena, ne izbor funkcija, dimenzija, transformacija ni pomeraja.

**(a) Osno-poravnate klasične funkcije.** *Nalaz:* na 21 klasičnoj ćeliji S0, među četiri konfiguracije i sa 20 semena, GAdapt-M je imao veći ponderisani ECDF A do 12.000 stvarnih poziva od oba PyGAD-a i DE-a; u post hoc analizi E njegov CVaR₀,₉ iznosio je 0,0033 na originalnim i pomerenim ćelijama, dok je preset imao 0,0031 odnosno 0,0032. Post hoc, DE ima nižu završnu medijanu u 14/21 ćelija pri izvornom zaustavljanju; pri najviše 12.000 poziva odnos je 10 : 10 : 1. *Smernica:* na ispitanim osno-poravnatim klasičnim funkcijama nalaz podržava veću efikasnost GAdapt-M prema konkurentima iz S0, ali ne ustanovljava najbolji rep, opštu veću preciznost niti pravilo izbora algoritma.

**(b) Ortogonalna transformacija promenljivih.** *Nalaz:* u R, na 21 fiksnoj ćeliji i samo dve konfiguracije, uvođenje Haar-ortogonalne matrice Q uz isti pomeraj smanjilo je A GAdapt-M za 0,081 [0,072; 0,090], a IPOP-a za 0,010 [0,004; 0,017]. *Smernica:* na tim ćelijama GAdapt-M je bio znatno osetljiviji od IPOP-a na ispitanu transformaciju; nalaz ne ustanovljava opštu pouzdanost CMA porodice, mehanizam, niti univerzalno pravilo izbora (osno poravnanje nije separabilnost).

**(c) Hibrid GAdapt → CMA-ES.** *Nalaz:* u fiksiranom hibridu sa 30% GAdapt-M, 70% CMA-ES i σ₀ = 0,05, zamena prve faze uniformnim slučajnim uzorkovanjem smanjila je A za 0,131 [0,124; 0,139] pod ortogonalnom transformacijom i za 0,178 [0,174; 0,182] na orig+shift (studija A); time je ustanovljen efekat zamene u ovoj konfiguraciji. *Smernica:* u ovom fiksiranom hibridu GAdapt faza nije bila zamenljiva slučajnim uzorkovanjem; neinferiornost prema IPOP-u na sintetičkim ćelijama nije potvrđena (E3, H64g3 neodlučena), a na ORPD-u hibrid nije bio dokazano bolji od GAdapt-M i imao je lošiji rep od IPOP-a (I2).

**(d) Diskretni ograničeni ORPD.** *Nalaz:* na osam ORPD ćelija iz tri mreže, sa 30 semena i 12.000 stvarnih PF poziva, GAdapt-M je imao izvodljivost 0,746 i bio je dokazano bolji od oba PyGAD-a i DE-a po toj meri; razlike prema CMA, IPOP i BIPOP nisu razrešene (H64c neodlučena), a agregat zavisi pretežno od šest ćelija (dve su gotovo potpuno neizvodljive). *Smernica:* nalaz ne daje osnov za preporuku GAdapt-M umesto CMA porodice niti za tvrdnju o industrijskoj spremnosti.

**(e) Indeks sprege κ.** *Nalaz:* razvojni nalaz za κ u E bio je post hoc; preregistrovana ORPD predikcija dala je 5/8 ćelija po CVaR-u i 7/8 po medijani prema pragu 6/8 za oba ishoda, pa je ukupni ishod neodlučen. *Smernica:* κ se ne koristi kao selektor algoritma.

## 9.3 Opcione funkcije biblioteke

Preset stabilnosti (E, H64b), diferencijalni krosover (E2), kompenzaciona mutacija (E4), ugrađeni FR/ε (I58/I60) nisu pokazali potvrđenu korist; podrazumevano su isključeni i ponašanje je bit-identično. Njihova korisnost za industrijsku primenu nije ustanovljena.

## 9.4 Preostala pitanja za sastanak

(1) Koji je „jedan algoritam“ koji GAdapt ne nadmašuje; (2) da li industrijski problemi imaju spregu promenljivih i koje su dodatne instance potrebne za poređenje GAdapt-a, CMA porodice i hibrida (sadašnji nalazi ne opravdavaju izbor algoritma samo prema spregnutosti ili osnom poravnanju); (3) šta znači stabilnost (ponovljivost, raspon ili rizik) i koji su pragovi; (4) da li je empirijski doktorat sa ovim granicama prihvatljiv.
