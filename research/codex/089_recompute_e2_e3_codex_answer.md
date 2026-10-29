Sve statističke brojke u oba izveštaja reprodukovane su **pri prikazanoj preciznosti**, kao i sve odluke. Postoje greške u opisima i naslovu, navedene ispod. Projektni analizatori nisu pozivani; datoteke nisu menjane.

Nezavisno sam obradio 69.300 pokretanja i 12.659.277 događaja. Provereni su jedinstveni ključevi `(ćelija, konfiguracija, seme)`, svih 100 očekivanih semena, budžet od 12.000 poziva, monotonost tragova i saglasnost završnog minimuma sa poslednjim događajem. Nema neuspešnih zapisa.

Izračunati su \(g=\max(0,(f-f^*)/s)\), \(L=g/(1+g)\), A kao prosek doprinosa \((12000-c+1)/12000\) za tri cilja i ćelijski CVaR kao prosek najvećih 10 od 100 vrednosti L. Ponder ćelije je \(1/(9d_f·3)\), gde je \(d_f\) broj dimenzija funkcije; unutar podskupa ponderi su renormalizovani.

Bootstrap koristi 20.000 ponavljanja, `default_rng(66)`, nezavisno resamplovanje unutar svake ćelije i iste indekse za uparene konfiguracije. Standardne greške računane su sa `ddof=1`; simultani faktor je 0,95-kvantil maksimuma \(|\theta^*-\hat\theta|/SE\). Nema beskonačnih vrednosti ni nultih varijansi.

Za X=D u E2, odnosno X=H u E3, kontrasti su redom:

\(c_1=\Delta A_{rot}(X-M)\), \(c_2=0,8C_{rot}(M)-C_{rot}(X)\), \(c_3=\Delta A_{nonrot}(X-M)\), \(c_4=1,5C_{nonrot}(M)-C_{nonrot}(X)\), \(c_5=\Delta A_{rot}(X-IPOP)\).

| Studija | Kontrast | Procena | Donja granica | Gornja granica |
|---|---|---:|---:|---:|
| E2 | c1 | −0.036188148 | −0.047220795 | −0.025155501 |
| E2 | c2 | −0.025335381 | −0.029407149 | −0.021263612 |
| E2 | c3 | −0.042154686 | −0.046106482 | −0.038202891 |
| E2 | c4 | 0.000091497 | −0.000238003 | 0.000420996 |
| E2 | c5 | −0.182439074 | −0.192034980 | −0.172843168 |
| E3 | c1 | 0.102900216 | 0.092637453 | 0.113162979 |
| E3 | c2 | 0.012115536 | 0.009442553 | 0.014788519 |
| E3 | c3 | 0.065347546 | 0.060730702 | 0.069964390 |
| E3 | c4 | −0.000696428 | −0.001109104 | −0.000283751 |
| E3 | c5 | −0.043350710 | −0.051885269 | −0.034816151 |

Dobijeno je \(t^*_{E2}=2.559287260945\), \(t^*_{E3}=2.557948119740\) i \(C_{rot}(M)=0.030039505248\).

- **E2:** H64e1 suprotno; H64e2 neodlučeno; H64e3 suprotno.
- **E3:** H64g1 podržano; H64g2 suprotno; H64g3 neodlučeno.
- Ukupno podržano: **False** u obe studije.

Poređenje obuhvata svih 69 tabelarnih vrednosti E2 i 87 vrednosti E3, uključujući ukupnu tabelu E3. Nema nepoklapanja nakon odgovarajućeg zaokruživanja. Maksimalna apsolutna razlika prema nezaokruženim `analysis.json.gz` rezultatima iznosi **1,33·10⁻¹⁵ za E2**, odnosno **4,88·10⁻¹⁵ za E3**. Prema štampanim vrednostima maksimum je **2,87260945·10⁻⁴ za E2** i **5,18802598·10⁻⁵ za E3**, oba zbog zaokruživanja \(t^*\). Samo u tabelama maksimum je **4,90097181·10⁻⁵** u oba izveštaja.

Ponovo izračunat ukupni „prosek tri varijante“ E3:

| Konfiguracija | A | CVaR₀,₉ | Ponderisani prosek ćelijskih medijana g |
|---|---:|---:|---:|
| gadapt | 0.673205014 | 0.011723969 | 0.004288673 |
| gadapt_hyb | 0.751070117 | 0.007002508 | 0.002927837 |
| ipop | 0.769867843 | 0.014224841 | 0.007786134 |
| cma | 0.761808570 | 0.014471136 | 0.009207957 |
| bipop | 0.768816481 | 0.014214070 | 0.007305708 |
| de | 0.639621307 | 0.018490359 | 0.015035093 |

Provera prema zamrznutim specifikacijama pokazuje:

- **Ponderi su ispravni, opis tabela je pogrešan.** U [E2](/Users/danijel/Desktop/gadapt/research/ITERATION64_E2_REPORT_SR.md:20) i [E3](/Users/danijel/Desktop/gadapt/research/ITERATION64_E3_REPORT_SR.md:20) piše „ćelije jednako ponderisane“. Brojke koriste propisane pondere po funkciji/dimenziji. Na primer, orig A za GAdapt je 0.702169; jednak ponder ćelija dao bi 0.629490.
- **Podela ćelija je ispravna:** rot su indeksi `2,5,…,62` — svih 21 ćelija označenih `rot`, uključujući 2D i Sphere. Nonrot su svih 42 `orig+shift` ćelije.
- **„Medijana jaza“ je skraćen naziv:** računa se ponderisani aritmetički prosek ćelijskih medijana, saglasno [protokolu](/Users/danijel/Desktop/gadapt/research/ITERATION64_PROTOCOL.md:32). Ukupna E3 kolona je prosek te mere preko tri varijante.
- [Zaključak E2](/Users/danijel/Desktop/gadapt/research/ITERATION64_E2_REPORT_SR.md:56) tvrdi intervalno potvrđen pad „na svim varijantama“. Zamrznuta porodica daje intervale za **rot** i zajednički **nonrot**; zasebni orig/shift intervali nisu prikazani.
- [Naslov E3](/Users/danijel/Desktop/gadapt/research/ITERATION64_E3_REPORT_SR.md:1) pogrešno glasi „ITERATION64-E2“.