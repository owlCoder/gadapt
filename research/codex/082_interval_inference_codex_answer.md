**Presuda: NOT ESTABLISHED. Preporuka: NO-GO za dvonedeljni gate ove formulacije kao samostalnog teorijskog doprinosa.** Tražena garancija jeste dokaziva, ali osnovni rezultat sledi kratkom primenom poznatih uniformnih nejednakosti. Uža novina u metodologiji optimizacionog benchmarkinga ostaje moguća, ali nije ustanovljena.

Pročitani [I61 izveštaj](/Users/danijel/Desktop/gadapt/research/ITERATION61_REPORT_SR.md) i [077](/Users/danijel/Desktop/gadapt/research/codex/077_i63_design_codex_answer.md) opravdavaju problem: referenca nije bila sertifikovani optimum, a neki ciljevi nisu dostignuti do budžeta. To poslednje nije dokaz njihove globalne nedostižnosti. Ništa nije menjano niti pokretano.

Ciljana pretraga obuhvatila je literaturu 2018–28.10.2026, uz neophodne starije temelje. Nepostojanje pronađenog identičnog rada nije dokaz prvenstva.

| Prior art | Šta daje | Šta ne daje |
|---|---|---|
| **Hansen i sar. (2022), *Anytime Performance Assessment…*** DOI potvrđen: [10.1109/TEVC.2022.3210897](https://ieeexplore.ieee.org/abstract/document/9905722). | Sistematski tretira vreme dostizanja, izbor ciljeva, budžetske ciljeve, restarte i ECDF agregaciju. | Ne ustanovljava traženu simultanu garanciju za nepoznati optimum u intervalu. |
| **López-Ibáñez i sar. (2024 online; 2025 sveska), *Using the Empirical Attainment Function…*** DOI potvrđen: [10.1109/TEVC.2024.3462758](https://arxiv.org/html/2404.02031v3). | ECDF povezuje sa EAF-om, pokazuje osetljivost rangiranja na ciljeve; §V izričito pominje bootstrap pojaseve oko EAF-a. | Ne dokazuje baš traženi pojas za kontrast ograničenih očekivanih vremena, simultano preko reference. Sam prikaz bootstrap pojasa ne dokazuje simultano pokriće. |
| **Hall–Wellner (1980); Nair (1984); Sachs–Brand–Gabriel (2022).** DOI: [10.1093/biomet/67.1.133](https://academic.oup.com/biomet/article-abstract/67/1/133/276365), [10.1080/00401706.1984.10487964](https://www.tandfonline.com/doi/abs/10.1080/00401706.1984.10487964), [10.1038/s41416-022-01920-5](https://www.nature.com/articles/s41416-022-01920-5). | Asimptotske simultane pojaseve za funkciju preživljavanja preko **vremena**; Nair pristup daje pojaseve jednake preciznosti. | Pojas za \(S_r(t)\) pri jednom cilju \(r\) ne pokriva automatski sve ciljeve \(r\). Potreban je zajednički proces. |
| **Teng–Jiang–Chen (2023), RMST preko biomarkera.** DOI potvrđen: [10.1002/sim.9618](https://pubmed.ncbi.nlm.nih.gov/36444774/). | Neparametarsku inferenciju i simultane pojaseve za RMST preko kontinuiranog indeksa, uključujući poređenje grupa. | Biomarker menja uslovnu populaciju; ovde prag menja vreme događaja za isto pokretanje. Nije neposredno ista konstrukcija. |
| **Maksimalno izabrane log-rank statistike**, Lausen–Schumacher/Hothorn–Lausen; [tačna raspodela, DOI 10.1016/S0167-9473(02)00225-6](https://www.sciencedirect.com/science/article/pii/S0167947302002256). | Kalibraciju pretraživanja pragova koji dele ispitanike u grupe; obuhvata veze i cenzuru. | Ovde algoritamske grupe ostaju iste, a menjaju se vremena dostizanja. Njihova kritična vrednost nije automatski prenosiva; log-rank takođe nije estimand razlike RMST. |
| **Parcijalna identifikacija i osetljivost:** Zhao–Small–Bhattacharya (2019), [10.1111/rssb.12327](https://academic.oup.com/jrsssb/article/81/4/735/7048357); Masten–Poirier–Zhang (2024), [10.1080/07350015.2023.2183212](https://scholars.duke.edu/publication/1573437). | Prvi razvija Rosenbaum-srodan model i inferenciju pod ograničenim skrivenim konfaundiranjem; drugi daje pojaseve uniformne preko parametra osetljivosti. | Ne daju teoremu za neizvestan optimizacioni optimum. Direktnu primenu Manski/Rosenbaum okvira na traženo poređenje nisam pronašao. |
| **Nepoznati optimum u benchmarkingu:** [Bartz-Beielstein i sar. (2020)](https://arxiv.org/abs/2007.03488); [QOBLIB (2026), DOI 10.1038/s43588-026-00991-1](https://www.nature.com/articles/s43588-026-00991-1). | Razlikuju poznati optimum, najbolje poznato rešenje i dokazive granice; QOBLIB eksplicitno dopušta referencu koja odstupa od optimuma. | Ne daju traženu kontrolu greške preko celog intervala referenci. |

Za preciznu formalizaciju neka su algoritmi \(A,C\), budžet \(B\in\mathbb N\), a \(\varepsilon\ge0\) unapred fiksirani. Za isti problem neka \(Q_{ki}(t)\) bude najbolje izvodljivo ostvarenje posle \(t\) evaluacija; bez izvodljivog rešenja postavlja se \(+\infty\), uključujući \(Q_{ki}(0)=+\infty\). Pretpostaviti potpune tragove do \(B\), nezavisna i identično raspodeljena pokretanja unutar algoritma; uparivanje algoritama je dopušteno.

Definisati
\[
T_{ki}(r)=\inf\{t\ge1:Q_{ki}(t)\le r+\varepsilon\},\qquad
X_{ki}(r)=\min\{T_{ki}(r),B\},
\]
sa \(\inf\varnothing=\infty\), i
\[
\Delta(r)=E[X_A(r)]-E[X_C(r)],\quad r\in[L,U].
\]

Negativno \(\Delta(r)\) znači kraće očekivano **ograničeno** vreme za \(A\). Pogodak tačno na \(B\) i nedostizanje daju isti \(X=B\); ne procenjuje se neograničeno očekivano vreme niti restartni ERT.

\(\Delta\) je deterministički funkcionalni parametar; slučajan je empirijski proces \(\widehat\Delta-\Delta\). Relevantni objekti su cela kriva, skup mogućih efekata \(\{\Delta(r):r\in[L,U]\}\) i najnepovoljniji efekat \(\sup_r\Delta(r)\). Pojedinačna očekivanja jesu monotona, ali njihova razlika ne mora biti: krajevi intervala nisu dovoljni.

**Jedna konačno-uzoračka garancija može se dokazati odmah.** Neka
\(F_{kt}(z)=P\{Q_k(t)\le z\}\). Identitet
\[
E[X_k(r)]=\sum_{t=0}^{B-1}[1-F_{kt}(r+\varepsilon)]
\]
svodi problem na konačnu sumu raspodela kvaliteta.

Za \(n_k\) pokretanja postaviti
\[
\eta_k=\sqrt{\frac{\log(4B/\alpha)}{2n_k}},\qquad
w=B(\eta_A+\eta_C).
\]
[DKW–Massart nejednakost](https://doi.org/10.1214/aop/1176990746), uniformna preko svih \(z\), i union bound preko algoritama i vremena daju
\[
P\!\left\{\forall r\in[L,U]:
|\widehat\Delta(r)-\Delta(r)|\le w\right\}\ge1-\alpha.
\]
Nezavisnost između vremena nije potrebna. Veze i potpuna administrativna cenzura ne narušavaju dokaz.

Prema tome, pravilo
\[
\sup_{r\in[L,U]}\{\widehat\Delta(r)+w\}<0
\]
potvrđuje prednost za **svaki** dopušteni optimum, uz verovatnoću lažne potvrde najviše \(\alpha\). Pojas je konzervativan, ali ostvaruje osnovni zahtev.

Hall–Wellner zato nije neposredna posledica „u jednom redu”, ali **postojanje tražene garancije praktično jeste kratka posledica DKW-a i sabiranja**. Za fiksno \(B\), funkcionalni CLT takođe sledi iz konačne zajednice klasa indikatora pragova i linearnog preslikavanja. Uži bootstrap pojas zahteva kalibraciju supremuma i resamplovanje celih pokretanja/parova.

Empirijska kriva ima konačno mnogo prelomnih tačaka \(Q_{ki}(t)-\varepsilon\), pa se njen supremum može tačno izračunati, uz pravilno tretiranje jednakosti. Međutim, Bonferroni nad prelomima iz istog uzorka **sam nije dokaz**: populaciona kriva ne mora biti konstantna između njih.

Interval mora stvarno sadržati optimum: lokalni kontinualni OPF nije automatski donja granica; provereno izvodljivo rešenje istog problema daje gornju. Ako pokriće reference iznosi \(1-\beta\), ukupna garancija je najmanje \(1-\alpha-\beta\). Manski-slična projekcija ovde daje analizu osetljivosti; oštrina identifikacionog skupa zahtevala bi dodatni model kompatibilnih problema.

**Više od alatne napomene** zahtevalo bi nov rezultat o oštrini, snazi ili optimalnoj širini pojasa, uz dokaz prednosti prema standardnoj empirijskoj-procesnoj konstrukciji. Trenutno toga nema. Osnovna formulacija zato ne opravdava dvonedeljni istraživački gate za originalnost, iako predstavlja korisnu korekciju benchmark protokola.