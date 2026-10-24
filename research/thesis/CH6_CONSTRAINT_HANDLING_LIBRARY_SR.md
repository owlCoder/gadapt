# Poglavlje 6. Rukovanje ograničenjima u biblioteci GAdapt

*Nacrt, 24. oktobar 2026. Opisuje opt-in funkciju koja je razvijena i recenzirana dok je studija I56 trajala; u
biblioteku se unosi tek posle studija I56 i I57, a njena korisnost se konfirmatorno proverava u I58 i I59.*

## 6.1 Polazno stanje

GAdapt je do sada prihvatao samo jedan broj po jedinki: funkcija troška vraća realan broj, a sve ostalo,
elitizam, izbor roditelja i samoadaptacija, radi nad tim brojem. Korisnik koji ima ograničenja mora sam da ih
pretvori u kaznu i doda cilju. To je jednostavno, ali ima dve posledice koje su za infrastrukturne probleme važne.
Prvo, tehnike koje ne mogu da se izraze jednim nepromenljivim brojem, kao što su Deb-ova pravila izvodljivosti,
adaptivna kazna ili ε-ograničenje, uopšte nisu dostupne: kod adaptivne kazne i ε-ograničenja menja se i poredak
jedinki koje su već ocenjene, a to omotač funkcije troška ne može da uradi. Drugo, kazna ulazi u signale
samoadaptacije kao obična vrednost troška, pa adaptacija dok populacija nije izvodljiva reaguje na veličinu
prekršaja, a ne na napredak po cilju. Studija I56 meri koliko je ovo drugo važno; ovo poglavlje opisuje kako je
prvo rešeno.

## 6.2 Interfejs

Nova opcija je potpuno opt-in. Bez nje se biblioteka ponaša bit-identično kao ranije, što je provereno heševima
celog niza poziva funkcije troška na devet sejanih pokretanja sa kontinualnim, diskretnim i mešovitim
promenljivim. Kada korisnik zada `constraint_handling`, funkcija troška vraća par (cilj, prekršaj), gde je
prekršaj nenegativan broj, jednak nuli tačno za izvodljiva rešenja. Ponuđene su četiri tehnike: statička kazna,
adaptivna kazna po Ben Hadj-Alouane i Bean-u (težina se udvostručuje posle tri uzastopne generacije sa neizvodljivim
najboljim rešenjem i deli sa 1,5 posle tri izvodljive), Deb-ova pravila izvodljivosti i ε-ograničenje po Takahama i
Sakai-ju (prekršaji do nivoa koji opada do nule u prvoj polovini generacija smatraju se izvodljivim). Jedini
dodatni parametar je težina kazne; ostale konstante su fiksne i iste kao u studiji I56, jer bi dodatne opcije bez
dokaza o njihovoj koristi samo povećale prostor za podešavanje.

Rezultat optimizacije dobija tri nova polja: cilj i prekršaj najboljeg rešenja i oznaku izvodljivosti. „Najbolje“
ovde znači najbolje ocenjeno rešenje celog pokretanja po jednostavnom pravilu: izvodljivo sa najmanjim ciljem, a
ako izvodljivog nema, ono sa najmanjim prekršajem. Vrednosti promenljivih u rezultatu su vrednosti tog rešenja. Ovo
je namerna razlika od pobednika po internom skalaru: pod slabom kaznom poslednja populacija može biti predvođena
neizvodljivim rešenjem iako je izvodljivo rešenje ranije viđeno, a korisnik infrastrukturnog problema treba
izvodljivo rešenje.

## 6.3 Redosled događaja i dva odvojena puta

Najosetljiviji deo implementacije je redosled. U svakoj generaciji modul za ocenjivanje najpre evaluira nove
jedinke, zatim ažurira parametre tehnike iz završene istorije (težinu kazne, nivo ε), pa ponovo izračunava skalar
svih jedinki, i zatečenih i novih, pod tim parametrima, i tek tada bira elitu. Tako se nikad ne porede jedinke
ocenjene pod različitim parametrima. Iz istog razloga se pod tekućim parametrima preračunavaju i minimum i prosek
prethodne generacije, inače bi promena težine kazne izgledala kao poboljšanje ili pogoršanje i poremetila
pravila zaustavljanja i brojač stagnacije.

Poredak i vrednost su razdvojeni. Elita se bira po tačnom ključu tehnike, paru (klasa, vrednost), koji ne gubi
poredak ni za veoma velike ili veoma male vrednosti. Ostatak biblioteke, signali samoadaptacije, izbor roditelja i
imigracija, i dalje čita jedan broj: kod kaznenih tehnika to je kažnjeni cilj ograničen na ±10¹², a kod pravila
izvodljivosti i ε-ograničenja vrednost u opsegu [1, 3] (izvodljiva rešenja 1 + u(cilj), neizvodljiva
2 + V/(1 + V), neuspele evaluacije 3, sa u(f) = 1/2 + arctan(f/f_ref)/π i f_ref jednakim medijani apsolutnih
ciljeva početne populacije). Ovaj broj može da izgubi poredak samo daleko izvan skale početnih ciljeva, i to je
dokumentovano. Domen ulaza je ograničen na |cilj|, prekršaj ≤ 10¹⁵⁰, a težina kazne na 10¹⁰⁰, tako da je kažnjeni
cilj uvek konačan i tačno uporediv.

## 6.4 Kako je validirano

Funkcija je prošla četiri kruga nezavisne recenzije koda pre unošenja u biblioteku. Recenzije su našle tri vrste
grešaka koje testovi u prvoj verziji nisu hvatali: gubitak poretka kod zasićenja skalara, prekoračenje opsega
brojeva kod adaptivne kazne i poređenje sa prethodnom generacijom pod promenjenom skalom. Svaka je ispravljena i
pokrivena regresionim testom; četvrti krug nije našao nove greške. Biblioteka sada ima 71 test, od toga 13 za ovu
funkciju, uključujući test koji proverava da se pod slabom kaznom vraća izvodljivo rešenje iako je pobednik po
skalaru neizvodljiv. Podrazumevano ponašanje je posle svake izmene ponovo provereno heševima niza poziva.

Ista logika je pre toga korišćena u studiji I56 kao istraživačka podklasa, gde je posebno provereno da je
statička kazna kroz novi modul bit-identična čistom GAdapt-u na istom skalaru. Biblioteka se od istraživačkog koda
razlikuje u dve stvari, koje su eksplicitno navedene u protokolu I58: skala f_ref dolazi iz početne populacije
(u I56 iz kontinualnog optimalnog toka, koji biblioteka ne zna), a raspored ε prati generacije umesto potrošenih
evaluacija.

## 6.5 Šta ovo poglavlje tvrdi, a šta ne

Tvrdnja je inženjerska: GAdapt sada ima ispravno implementirane, dokumentovane i testirane standardne tehnike za
rukovanje ograničenjima, bez promene podrazumevanog ponašanja. Same tehnike nisu nove i navedene su sa izvorima.
Da li ugrađena opcija stvarno ubrzava pronalaženje dobrih izvodljivih rešenja u odnosu na uobičajenu upotrebu sa
kaznom pitanje je na koje odgovaraju konfirmatorne studije I58 (sveže elektroenergetske mreže sa termičkim
ograničenjima) i I59 (planiranje kapaciteta telekom mreže); ovo poglavlje taj odgovor ne pretpostavlja.
