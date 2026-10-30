## Zaključak

Najbolji pravac nije još jedan rotaciono-invarijantan operator: adaptive encoding, CMA-ES, UNDX/PCX i slični operatori već zauzimaju taj prostor. Odbranjiva su dva uža doprinosa:

1. **GO — teorema i dijagnostički sertifikat rotacione osetljivosti baš za GAdapt.**
2. **GO za jeftin pilot — graf-ekvivarijantna mutacija za diskretne ORPD kontrole.**
3. **NO-GO kao naučna novina — selektor GAdapt/IPOP iz ranog dela putanje.**

DOI-jevi ispod provereni su prema izdavačkim ili indeksnim metapodacima.

---

## 1. GAdapt Rotation-Sensitivity Certificate — teorema + dijagnostički protokol

**Istraživačko pitanje.** Može li se pad od 0,081 ECDF površine predvideti iz unutrašnjeg stanja GAdapt-a pre završetka optimizacije, i matematički pripisati kolonskim koeficijentima raznovrsnosti?

### Matematička definicija

Za `columnar_diversity_metric="linear"` neka je \(C_t\) kovarijansa populacije posle normalizacije opsega. GAdapt koristi

\[
d_{t,j}=\operatorname{clip}_{[0,1]}
 \sqrt{\frac{(C_t)_{jj}}{(C_0)_{jj}}},
\qquad
\sigma_{t,j}=\sigma_{\min}+(\sigma_{\max}-\sigma_{\min})d_{t,j}.
\]

Vektor \(d_t\) dalje određuje:

- broj mutiranih jedinki preko \(1-\bar d_t\);
- broj mutiranih koordinata preko \(n\bar d_t\);
- rang-verovatnoću izbora koordinata;
- varijansu Gausovog koraka \(\sigma_{t,j}^2\).

Za rotaciju \(Q\),

\[
d^Q_{t,j}=
\operatorname{clip}_{[0,1]}
\sqrt{\frac{(QC_tQ^\top)_{jj}}{(QC_0Q^\top)_{jj}}}.
\]

Predloženi sertifikat je razlika drugog momenta predloga:

\[
R_t(Q)=
\frac{\left\|
Q^\top\operatorname{diag}(q^Q_{t,j}\sigma^{Q\,2}_{t,j})Q
-\operatorname{diag}(q_{t,j}\sigma^2_{t,j})
\right\|_F}
{\left\|\operatorname{diag}(q_{t,j}\sigma^2_{t,j})\right\|_F},
\]

gde je \(q_{t,j}\) tačna ili Monte-Karlo verovatnoća da koordinata \(j\) bude mutirana.

**Teorema za dokazivanje.**

- Za linearni režim, generička grupa ortogonalnih simetrija regulatora nije \(O(n)\), već najviše grupa potpisanih permutacija koordinata; podrazumevani logaritamski režim nema veću grupu.
- Ako je \(C_0=cI\), onda za Haar-rotaciju  
  \(\mathbb E_Q[(QC_tQ^\top)_{jj}]=\operatorname{tr}(C_t)/n\): rotacija u proseku homogenizuje upravo dijagonalu iz koje GAdapt izvodi signal, dok sopstvene vrednosti pune kovarijanse ostaju očuvane.

### Tačna razlika prema prior artu

Ovo **nije** novi lek za rotaciju:

- Hansenov adaptive encoding uči linearnu transformaciju postojećeg optimizatora — [DOI 10.1007/978-3-540-87700-4_21](https://doi.org/10.1007/978-3-540-87700-4_21).
- CMA-ES adaptira punu \(C_t\) — [DOI 10.1162/106365601750190398](https://doi.org/10.1162/106365601750190398); sep-CMA zadržava samo dijagonalu i napušta učenje zavisnosti — [DOI 10.1007/978-3-540-87700-4_30](https://doi.org/10.1007/978-3-540-87700-4_30).
- PCX/UNDX već generišu potomke iz geometrije vektora roditelja, a ne koordinatu po koordinatu: [PCX DOI 10.1109/CEC.2002.1006210](https://doi.org/10.1109/CEC.2002.1006210), [UNDX DOI 10.11517/jjsai.14.6_1146](https://doi.org/10.11517/jjsai.14.6_1146).
- Grupna invarijantnost genetskih operatora već je formalizovana kao komutiranje sa grupnom akcijom — [Rowe–Vose–Wright, DOI 10.1162/EVCO_a_00007](https://doi.org/10.1162/EVCO_a_00007).

**Uska novost:** eksplicitna karakterizacija prelaznog jezgra GAdapt-ovog višestepenog regulatora i koeficijentni sertifikat koji predviđa upareni gubitak performansi. Nije tvrdnja da su invarijantnost ili rotacioni benchmark novi.

### Baseline i falsifikacija

Baselines:

- \(\kappa\), ELA osobine, rani nagib poboljšanja;
- spektralna kondicija \(C_t\);
- sep-CMA, puna CMA, IPOP/BIPOP;
- PCX/UNDX kao geometrijske GA kontrole.

Eksperiment:

- koristiti postojeće pune ishode 21 para `shift/rotm`;
- novi kratki tragovi: \(21\times20\times2\times1.200=1.008.000\) jeftinih sintetičkih poziva;
- primarno: Spearman korelacija ranog \(\operatorname{median}_{t\le0.1B}R_t\) sa postojećim ćelijskim padom \(\Delta A\);
- uspeh: \(\rho\ge0,60\) i donja 95% granica \(>0,30\), uz bolju predikciju od \(\kappa\), ELA i ranog nagiba u leave-one-function-out postupku.

**Falsifikacija:** pogrešan dokaz za stvarni kod, ili interval korelacije koji uključuje 0,30. ORPD ne treba „rotirati”: takva transformacija nema fizičko značenje za diskretne kontrole.

**Odluka: GO.** Najjeftiniji i najuverljiviji pravac; doprinos ostaje vredan čak i bez novog optimizatora.

---

## 2. Graph-GAdapt — graf-ekvivarijantna adaptivna mutacija diskretnih kontrola

**Istraživačko pitanje.** Može li se GAdapt-ova filozofija „više jedinki, manje promenljivih i manji koraci pri konvergenciji” preneti na diskretne ORPD promenljive bez proizvoljne numeričke oznake alela?

### Metod

Za diskretnu promenljivu \(i\), neka je \(G_i=(V_i,E_i)\) graf dozvoljenih fizičkih prelaza:

- putanja za uređene tap/shunt nivoe;
- kompletan graf za nominalne kategorije;
- domen-specifičan graf ako neke promene nisu dozvoljene.

Iz populacione marginale \(p_i\) računati

\[
d_i=\frac{-\sum_{v\in V_i}p_i(v)\log p_i(v)}{\log |V_i|}.
\]

Promenljiva se bira sa težinom približno \(1-d_i\), dok se novi alel uzorkuje iz toplotnog jezgra

\[
K_i(\tau_i)=\exp(-\tau_iL_i),\qquad
\tau_i=\tau_{\min}+(\tau_{\max}-\tau_{\min})d_i,
\]

gde je \(L_i\) graf-Laplasijan. Niska raznovrsnost daje lokalni korak, ali se mutira više jedinki; visoka raznovrsnost dopušta širi prelaz.

**Teoremom garantovana osobina.** Za svaku permutacionu matricu \(P\) koja samo preimenuje čvorove grafa,

\[
L'_i=PL_iP^\top,\qquad
K'_i=PK_iP^\top,
\]

a entropija je nepromenjena. Diskretno mutaciono jezgro zato komutira sa izomorfizmom reprezentacije.

### Tačna razlika prema prior artu

- Rowe–Vose–Wright daju opštu karakterizaciju reprezentaciono-invarijantnih operatora, ali ne ovo GAdapt-ovo entropijski kontrolisano toplotno jezgro.
- Entropijska adaptacija mutacije sama nije nova; zato ona nije tvrdnja doprinosa.
- CMA-ES with Margin koristi latentni Gausov model, pragovno diskretizovanje i donju granicu marginalne verovatnoće promene — [DOI 10.1145/3512290.3528827](https://doi.org/10.1145/3512290.3528827). Graph-GAdapt nema latentno euklidsko kodiranje i može razlikovati ordinalne i nominalne domene.
- Hansenov adaptive encoding je kontinualna linearna transformacija, ne diskretni graf domena.

**Uska novost:** kombinacija GAdapt-ovog višestepenog diversity feedbacka sa per-variable grafovskim toplotnim jezgrom i dokazom ekvivarijantnosti prema izomorfizmu domena. U pregledanoj literaturi nisam našao tu tačnu konstrukciju; ne treba tvrditi da su entropija, grafovski random walk ili reprezentaciona invarijantnost pojedinačno novi.

### Baseline i falsifikacija

Baselines:

- GAdapt-M;
- fiksni \(K_i(\tau)\), bez adaptacije;
- entropijski regulator + nezavisno uniformno ponovno uzorkovanje;
- CMAwM, IPOP/BIPOP;
- postojeći PyGAD/DE rezultati kao slabe kontrole.

Jeftini gate:

- sintetički test: 100 nasumičnih preimenovanja alela mora uz upareni RNG dati identičan dekodirani trag;
- ORPD: osam postojećih ćelija, 12 semena, \(B=3.000\);
- ako se postojeći prefiksi GAdapt/IPOP/BIPOP ponovo koriste, četiri nova režima zahtevaju oko \(8\times12\times4\times3.000=1,152\) miliona PF poziva.

Preregistrovani prolaz:

1. Graph-GAdapt bolji od obe ablacije u agregatnoj izvodljivosti, sa simultanom donjom granicom iznad nule;
2. nije lošiji od boljeg od GAdapt-M/CMAwM za više od 5 p.p.;
3. CVaR nije veći više od 10%.

**Falsifikacija:** bilo koji neuspeh tačne ekvivarijantnosti ili izostanak koristi prema obe ablacije.

**Odluka: GO samo za ovaj pilot.** Ako padne ablacioni gate, trajni NO-GO; ne pokretati odmah potvrdu sa 30 semena i 12.000 PF.

---

## 3. Rani selektor GAdapt ↔ IPOP iz putanje — nije nova tema

**Istraživačko pitanje.** Da li prvih 5% budžeta GAdapt-a — \(\bar d_t\), rasipanje \(d_{t,j}\), nagib napretka i hazard izvodljivosti — može odlučiti da li nastaviti GAdapt ili preći na IPOP?

To bi bilo bolje od \(\kappa\), jer meri stvarni odziv algoritma na problem, a ne statičnu spregu.

Ipak, matematički je to već poznata forma:

\[
z(\mathcal T_{0:b})\longmapsto
\arg\min_{a\in\{\mathrm{GAdapt,IPOP}\}}\widehat L(a\mid z).
\]

ELA selekcija postoji od Mersmanna i saradnika — [DOI 10.1145/2001576.2001690](https://doi.org/10.1145/2001576.2001690). Per-run selekcija iz rane putanje sa warm-startom već je objavljena — [DOI 10.1109/CEC55065.2022.9870222](https://doi.org/10.1109/CEC55065.2022.9870222). Nevergrad/ABBO već gradi portfolio-wizard iz velikog benchmarka — [Nevergrad DOI 10.1145/3460310.3460312](https://doi.org/10.1145/3460310.3460312), [ABBO DOI 10.1109/TEVC.2021.3108185](https://doi.org/10.1109/TEVC.2021.3108185).

Nove GAdapt osobine bile bi samo novi feature set, ne nova klasa metoda.

Hipotetički test bi koristio \(b=600\), leave-one-function-out sintetiku i potpuno zaključane ORPD ćelije, naspram single-best, NGOpt/ABBO, ELA-RF, slučajnog izbora, \(\kappa\) i oracle selektora. Selektor bi pao ako ne nadmaši single-best uz uračunatih 600 poziva.

**Odluka: NO-GO kao doktorska novina.** Može ostati praktična preporuka ili sekundarna analiza, ali ne glavni doprinos.

---

COCO/BBOB već standardizuje funkcijske instance, ciljeve, broj poziva i ECDF — [COCO DOI 10.1080/10556788.2020.1808977](https://doi.org/10.1080/10556788.2020.1808977). Zato bi konačna preporuka bila: **prvo pravac 1; pravac 2 samo kroz jeftin gate; ne trošiti novu seriju na selektor ili na još jednu CMA/adaptive-encoding varijantu.**