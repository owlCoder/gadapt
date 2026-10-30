Nije spremno za zamrzavanje. Algoritam i statistika su uglavnom ispravni, ali postoje četiri stvarna hardening problema i nekoliko specifikacionih nedostataka.

- **OK — faza 2 i budžet.** Blok CMA-ES je identičan: isti `x0`, `sigma0`, restart `sigma=0.3`, granice i tokovi `[seed,3,k]`/`[seed,4,k]` u [a_algo.py:17](/Users/danijel/Desktop/gadapt/research/i64/a_algo.py:17) i [e3_algo.py:97](/Users/danijel/Desktop/gadapt/research/i64/e3_algo.py:97). `_Recorder` proverava limit pre poziva `g`, pa je naplaćeno tačno 3.600 poziva; poziv koji baca `SubBudgetReached` nije naplaćen ([e3_algo.py:23](/Users/danijel/Desktop/gadapt/research/i64/e3_algo.py:23)). Spoljni budžet analogno naplaćuje pozive 1–12.000, a baca pre 12.001. ([e_common.py:74](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:74)). Nema off-by-one razlike.

- **OK — domen.** `gadapt_hyb` dobija native `lo,hi`, ali `_native` pretvara tačke u jediničnu kocku pre `_Recorder`, pa je sačuvani `best` u `[0,1]^d` ([e3_algo.py:77](/Users/danijel/Desktop/gadapt/research/i64/e3_algo.py:77), [e_algos.py:14](/Users/danijel/Desktop/gadapt/research/i64/e_algos.py:14)). Ablacija direktno uzorkuje `[0,1]^d` i pravilno nije u `NATIVE` ([a_study.py:68](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:68)).

- **MISMATCH — `frac` nije tvrdo zaključan na 0,3.** Kod prihvata bilo koju vrednost iz trenutnog E3 `freeze` ([a_study.py:68](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:68)), iako specifikacija zahteva 0,3. Dodati `if frac != 0.3: STOP`, pre manifesta i izvršavanja.

- **OK — statistika.** Težine se pravilno renormalizuju unutar `rot` i `orig+shift` ([a_study.py:233](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:233)); po ćeliji se koristi jedan bootstrap indeks zajednički za H i R ([a_study.py:244](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:244)); pragovi i nazivi ishoda odgovaraju specifikaciji ([a_study.py:263](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:263)). c3/c4 mogu ostati u simultanoj porodici: to je konzervativno, ali validno i daje simultane opisne intervale. Ako se izbace, njihovi intervali više ne smeju biti predstavljeni kao deo iste simultane porodice.

- **BUG — beskonačni terminalni jaz ne blokira.** `g=inf` se pretvara u konačno `1.0`, a `finite` proverava samo A i kompresovani CVaR ([a_study.py:210](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:210), [a_study.py:244](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:244)). Time je prekršeno „beskonačne vrednosti blokiraju“. Pre bootstrap-a proveriti `np.isfinite(arr[..., 2])` za sve H/R zapise i uključiti rezultat u `blocked`.

- **MISMATCH — blokirani izlaz je nepotpun.** Trenutno sadrži samo `blocked` i procene ([a_study.py:255](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:255)). Dodati `names`, `se`, bootstrap postavke, `inputs`, `freeze_commit`, te `H64a1="blocked"`, `H64a2="blocked"` i `contribution_supported=None`. Neblokirani `contributes=False` je takođe previše deklarativan; preimenovati u `contribution_supported`.

- **BUG — nepotpuna freeze-commit veza.** `e3_algo.py` je heširan, ali nije proveravan prema freeze komitu; `e3_study.py`, koji izvršava repro gate, nije ni u manifestu ([a_study.py:78](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:78), [a_study.py:86](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:86)). Freeze-bindovati najmanje `a_study.py`, `a_algo.py`, `e3_algo.py`, `e3_study.py`, `e_study.py`, `e_common.py`, `e_algos.py` i specifikaciju.

- **MISMATCH — `check_repro` je potreban, ali nije dovoljan.** Ponovno izvršavanje H pravilno potvrđuje kompatibilnost arhive ([a_study.py:114](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:114)), ali uopšte ne izvršava novi `rand_cma_runner`. Dodati sintetički, ne-potvrdni preflight koji proverava determinističko ponavljanje, handoff posle tačno 3.600 poziva, najbolju tačku i početne CMA parametre. Ne koristiti A potvrdne ćelije za taj test.

- **BUG — `run` nije race-free create-once.** Rezervacija se koristi samo za `check_repro` i `analysis`; `run` i `run_part_*` imaju check-then-write trku, dok `os.replace` može prepisati izlaz ([a_study.py:44](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:44), [a_study.py:158](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:158)). Uvesti ekskluzivnu rezervaciju svakog dela i završnog `run`, a `reserve` mora odbiti i već postojeći `.json.gz`, ne samo `.lock`.

- **MISMATCH — validacija arhiviranog H je preslaba.** Analiza za H proverava samo `ok` i broj poziva, a zatim ignoriše originalni `config`, `purpose` i `params` ([a_study.py:223](/Users/danijel/Desktop/gadapt/research/i64/a_study.py:223)). Dodati semantičku validaciju tačno 6.300 jedinstvenih `gadapt_hyb` zadataka, očekivanih ćelija/semena i validnih događaja. Isto pozvati `valid_records` nad sastavljenim R `run` pre analize.

Pre freeze-a specifikacija treba još da:

- definiše A, normalizovani/kompresovani jaz i CVaR90;
- kaže da bootstrap obuhvata samo varijaciju algoritamskih semena, ne funkcije, dimenzije ili transformacije;
- zameni „izoluje doprinos GAdapt faze“ preciznijim „procenjuje efekat zamene GAdapt prve faze uniformnim uzorkovanjem u ovom fiksiranom hibridu“ ([ITERATION64_A_SPEC.md:3](/Users/danijel/Desktop/gadapt/research/ITERATION64_A_SPEC.md:3));
- zabrani tvrdnju da GAdapt samostalno nadmašuje random, da je efekat mehanistički, ili da važi za druge udele, budžete, `sigma0` ili CMA varijante;
- obelodani da su E3 ishodi bili poznati, a prag 0,02 fiksiran pre A ishoda;
- ili dodati obećane `a_report.py` i `run_a.sh`, ili ih ukloniti iz realizacije — trenutno ne postoje, iako ih specifikacija navodi ([ITERATION64_A_SPEC.md:15](/Users/danijel/Desktop/gadapt/research/ITERATION64_A_SPEC.md:15)).

Fajlovi nisu menjani.