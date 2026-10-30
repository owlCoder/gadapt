# Poglavlje 9. Smernice za primenu zasnovane na dokazima

*Nacrt, 30. oktobar 2026. Svaka stavka navodi studiju i meru; ništa ovde nije nova tvrdnja, već sažetak dokaza iz poglavlja 4, 7 i 8. Smernice nisu opšta industrijska preporuka: važe za ispitane funkcije, ćelije, konfiguracije i budžete.*

## 9.1 Šta znači „stabilan, tačan, primenjiv“ u ovom radu

Mentorov kriterijum je preveden u mere koje se mogu izračunati: **efikasnost** (ECDF površina A pri 12.000 stvarnih poziva), **tačnost** (medijana normalizovanog jaza), **stabilnost kao rizik lošeg ishoda** (CVaR₀,₉ ishoda L = g/(1+g)) i **izvodljivost** na ograničenim problemima (verovatnoća nalaska izvodljivog rešenja). Stabilnost kao ponovljivost istog semena i prag prihvatljivosti nisu dogovoreni sa mentorom (pitanje za sastanak).

## 9.2 Tabela smernica

| Situacija | Dokaz | Smernica | Ne sme se tvrditi |
|---|---|---|---|
| Osno-poravnata (neokrenuta) kontinualna funkcija, do 12.000 poziva | S0 (efikasnost ΔA prema PyGAD-ovima i DE-u > 0), E (CVaR₀,₉ GAdapt-a 0,0033 na orig/shift, najniži rep među devet konfiguracija na ovom podskupu) | GAdapt je opravdan izbor; ima najbolji rep i konkurentnu preciznost na ispitanim ćelijama | Opšta veća preciznost (DE ima nižu završnu medijanu u 14/21 ćelija); prednost van 21 ćelije |
| Promenljive spregnute rotacijom (ortogonalna transformacija) | E, R: isti pomeraj, uvođenje Q smanjuje A GAdapt-M za 0,081 [0,072; 0,090], IPOP za 0,010 [0,004; 0,017] | CMA porodica (IPOP/BIPOP) je pouzdaniji izbor; GAdapt-M pod ovom transformacijom gubi | Da je rotacija jedini mehanizam; da je osno poravnanje isto što i separabilnost |
| Globalna faza pa lokalno doterivanje | E3 (hibrid poboljšava A pod rotacijom prema GAdapt-M, ali nije dokazano jednak IPOP-u i ima lošiji rep na orig/shift), A (zamena GAdapt faze slučajnim uzorkovanjem smanjuje A za 0,131 pod rotacijom i 0,178 na orig/shift) | Ako se koristi hibrid, GAdapt faza doprinosi; hibrid nije zamena za IPOP | Da hibrid nadmašuje IPOP; da je σ₀ = 0,05 optimalno; prenos na ORPD (I2 ne potvrđuje korist) |
| Diskretni ograničeni problem tipa ORPD (osam ćelija, 12.000 PF poziva) | I64-I (izvodljivost GAdapt-M 0,746, bolja od PyGAD-a i DE-a; prema CMA/IPOP/BIPOP intervali obuhvataju nulu) | GAdapt-M je konkurentna opcija; smer razlike prema CMA porodici nije razrešen | Preporuka „GAdapt umesto CMA“; opšta industrijska spremnost |
| Odabir algoritma po indeksu sprege κ | G (predikcija neodlučena, 5/8 i 7/8) | Ne koristiti κ kao selektor | Da κ predviđa nadmoć CMA |

## 9.3 Opcione funkcije biblioteke

Preset stabilnosti (E, H64b), diferencijalni krosover (E2), kompenzaciona mutacija (E4), ugrađeni FR/ε (I58/I60) nisu pokazali potvrđenu korist; podrazumevano su isključeni i ponašanje je bit-identično. Njihova korisnost za industrijsku primenu nije ustanovljena.

## 9.4 Preostala pitanja za sastanak

(1) Koji je „jedan algoritam“ koji GAdapt ne nadmašuje; (2) da li industrijski problemi koje mentor ima na umu imaju spregu promenljivih (tada CMA/hibrid) ili su osno-poravnati (tada GAdapt); (3) šta znači stabilnost (ponovljivost, raspon ili rizik) i koji su pragovi; (4) da li je empirijski doktorat sa ovim granicama prihvatljiv.
