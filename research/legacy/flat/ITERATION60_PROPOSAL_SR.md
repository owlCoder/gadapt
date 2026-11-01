# I60 (PREDLOG): konfirmatorna provera ε-ograničenja u GAdapt-u (iz opisnog nalaza I56)

**Status:** predlog 2026-10-24, posle I56, PRE pokretanja I58 (nijedan I58 rezultat ne postoji). Povod: u I56 je
ε-ograničenje opisno višestruko skratilo vreme do cilja na case14 (T 0,28 naspram 0,77), ali to nije bila hipoteza.
I58 je zamrznut sa pravilima izvodljivosti i ostaje nepromenjen; I60 je zasebna preregistracija.

## Pitanje (konfirmatorno)
Da li GAdapt sa ugrađenim `constraint_handling="epsilon"` (G2) dostiže izvodljiv cilj brže od uobičajene upotrebe sa
kaznom f + 1000·V (G0), na svežim mrežama I58 i novim semenima?

## Ključni detalj implementacije
U biblioteci ε opada do nule tokom prve polovine `number_of_generations` (u I56 tokom prve polovine potrošenih
evaluacija). Uz zaustavljanje po budžetu I60 postavlja `number_of_generations = ceil(B / e_g)`, gde je e_g broj novih
evaluacija po generaciji pri podrazumevanim podešavanjima (32 jedinke, 50% elitizma → 16; proveriti u kodu pre
zamrzavanja), pa se zaustavljanje i dalje vrši po budžetu (`exit_function`), a ε raspored prati budžet kao u I56.
G0 dobija ista podešavanja (broj generacija ne utiče na G0 jer se zaustavlja po budžetu).

## Instance, reference, analiza
Iste kao I58 (case30, case39, case24_ieee_rts primarno; case300 opisno; R = 17; scenariji 301–303; jedna VG po
sabirnici), reference I58 (`i58_refs.json.gz`, svih pet metoda, heš zabeležen pre I60 pokretanja). Novi tok semena
(p = 8), 15 parova; budžeti 3000 (primarni) i 10.000 (opisni). T kao I58. θ = jednako ponderisan srednji
T(G2) − T(G0); stratifikovani bootstrap unutar mreža × scenario, 20.000, seme 60. **H60 podržana ako je 95% interval
potpuno ispod nule.** Nezavisna provera, manifesti i pravila neuspeha kao u I58.

## Rizik
Ako I58 pokaže degenerisane blokove (cilj nedostižan za sve), isto važi i za I60; to se ne može ispraviti posle
uvida u I58. Zato je I60 zamrznut PRE I58 i prihvata taj rizik.
