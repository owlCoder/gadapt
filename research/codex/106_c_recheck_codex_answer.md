Nije spremno za zamrzavanje.

- **OK** — updater hook poziva originalni `_update_decision_variables` pre snimanja, radi jednom po završenoj generaciji, context manager vraća original čak i posle izuzetka, a `run_H()` izostavlja prvi, t=0 zapis ([c_study.py:111](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:111), [c_study.py:242](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:242)).

- **BUG** — recorder tiho preskače nevalidan vektor, čime više ne snima tačno jednom po generaciji ([c_study.py:124](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:124)). Umesto uslovnog `_LOG.append`, odmah prekinuti run ako dimenzija, konačnost ili opseg nisu validni.

- **BUG** — `valid()` ne proverava `calls == 1200`, konačnost ni opseg koeficijenata ([c_study.py:192](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:192)). Mock je pokazao da prihvata `calls=1199` i vektore `[2,-1]`. Dodati proveru poziva, strogo rastućih call-markera i svih `finite, 0≤d≤1`. Pozivanje `valid()` pri resume-u i analizi jeste pravilno postavljeno.

- **BUG** — preflight koristi `Budget.events`, koji sadrži samo best-so-far poboljšanja, pa ne dokazuje identičan kompletan niz evaluiranih tačaka ([c_study.py:185](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:185), [e_common.py:79](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:79)). U preflight-u heširati sve ulazne vektore i rezultate svih 1.200 poziva. Tri para i create-once rezervacija jesu ispravni.

- **OK** — bootstrap je po devet funkcijskih klastera; arhivirane veličine su seed-level, a isti `iA`/`iB` indeksi dele se između ΔA i E unutar varijante ([c_study.py:259](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:259), [c_study.py:320](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:320)).

- **BUG — metodološki** — kod pravilno računa 16/21, nenulti denominator i Bonferroni (`16/21 p=0,01330`), ali „egzaktni” binomni test i dalje tretira dimenzije iste funkcije kao nezavisne ([c_study.py:343](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:343)). Zadržati 16/21 samo kao opisni kriterijum bez formalnog p-gate-a ili definisati jedan znak po funkcijskom klasteru.

- **OK** — `inputs()` vezuje svih 21 E-shift delova, E freeze/normalizers/manifest i sva tri R fajla. `same_gadapt_build_as_R()` radi; trenutni `r_study.py` heš odgovara R arhivi. Flock, tačno 1.260 jedinstvenih taskova i nazivi verdicta su ispravni.

- **BUG** — `c_report.py` i `run_c.sh` postoje, praćeni su Gitom i sintaksno su validni, ali nisu uključeni u C freeze manifest ([c_study.py:67](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:67)). Dodati ih u `names` i freeze-commit proveru.

- **BUG — nova provenance rupa** — C ne odbija prljav MBENCH checkout, iako iz njega učitava benchmark funkcije; R to proverava. Dodati `git status --porcelain` proveru u `c_manifest()`.

In-memory `stage_analyse` mock sa svih **1.260** fabrikovanih zapisa uspešno je prošao bez pisanja fajlova i proizveo očekivane verdict grane.