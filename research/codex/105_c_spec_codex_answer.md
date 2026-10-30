Није спремно за замрзавање. Постоје четири блокирајућа проблема: recorder не мери по генерацији, `preflight` није три пута recorder-off/on, bootstrap не обухвата неизвесност архивираних величина, а freeze/validation веза је непотпуна.

### Recorder и метрика

- **BUG** — `H` није медијана CV-а по генерацијама. Recorder је закачен за `_get_mutation_rate` и пише при појединачним мутацијама ([c_study.py:96](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:96)), док број таквих позива зависи од броја мутираних кандидата и случајног избора determinatora. Зато су генерације неједнако пондерисане, а неке могу бити изостављене; [run_H:202](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:202) ипак третира сваки запис као засебно \(t\).

  **Тачна исправка:** monkeypatch-овати `ColumnarDiversityDecisionVariableUpdater._update_decision_variables`, позвати оригинал па снимити вектор тачно једном. То место се извршава после евалуације популације ([ga_executor.py:103](/Users/danijel/Desktop/gadapt/gadapt/execution/ga_executor.py:103)). Унапред дефинисати да ли се почетна популација рачуна као \(t=0\); снимати и број позива/генерацију и захтевати `len(d)==D`, коначност и \(0\le d_j\le1\).

- **BUG** — тренутни `preflight` заиста има recorder-off/on само за први `k`. После првог `_install_recorder`, monkeypatch остаје трајно означен са `_c_recorded` ([c_study.py:99](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:99)), па су „off” покретања за `k=6,10` и даље instrumentisana ([c_study.py:149](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:149)).

  **Исправка:** привремени context manager са обавезним враћањем оригиналне методе у `finally`, или одвојени свежи процеси за сваки off/on пар. Такође, ово нису „синтетички задаци” како пише у спецификацији, већ три benchmark ћелије ([SPEC:14](/Users/danijel/Desktop/gadapt/research/ITERATION64_C_SPEC.md:14)).

- **OK уз ограничење тврдње** — када садашњи hook заиста буде позван, коефицијенти су већ прошли `None/NaN` проверу ([determinator.py:35](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/candidate_solution_mutation/variable_columnar_diversity_decision_variable_mutation_rate_determinator.py:35)). Проблем је што неуспели/прескочени позиви остају невидљиви, што решава hook на updater-у.

- **MISMATCH** — E конфигурација користи подразумевани `log_relative`, јер га runner не задаје ([e_algos.py:102](/Users/danijel/Desktop/gadapt/research/i64/e_algos.py:102)), а default је log метрика ([ga.py:132](/Users/danijel/Desktop/gadapt/gadapt/ga.py:132)). Теорија о дијагонали коваријансе непосредно се односи на линеарни spread, док стварни коефицијент користи `std(log(x-min+1))`, нормализацију почетним spread-ом и clipping ([updater.py:45](/Users/danijel/Desktop/gadapt/gadapt/operations/decision_variable_update/variable_columnar_diversity_decision_variable_updater.py:45)).

  **Исправка:** не мењати примарни run на `linear`, јер то више не би био механизам резултата R. Експлицитно фиксирати `columnar_diversity_metric="log_relative"` и сузити тврдњу на „хомогенизацију стварних log-relative коефицијената”. Ако се жели тврдња о коваријанси, пасивно снимити и `diag(cov)`/линеарни spread као засебну, унапред означену секундарну меру.

### Статистика

- **BUG** — Bonferroni није доследно примењен: bootstrap користи \(\alpha/3\), али sign test користи `p<0.05` ([c_study.py:285](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:285), [c_study.py:291](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:291)). За \(n=21\), 15 позитивних даје \(p=0.03918\), али не пролази \(\alpha/3\); потребно је најмање 16, \(p=0.01330\).

  **Исправка:** `p_binom < ALPHA/3` и „најмање 16/21”, или sign test прогласити искључиво описним критеријумом и избацити га из формалне H64c1 одлуке.

- **BUG/MISMATCH** — „bootstrap преко семена” тренутно resample-ује само 30 C семена. `ΔA_k` је учитан као готов просек, а `E_k` као фиксна архивска вредност ([c_study.py:224](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:224), [c_study.py:247](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:247)). Неизвесност њихових 100 семена, нарочито рангирање бројних `ΔA` близу нуле, потпуно је занемарена.

  **Исправка:** из сирових E/R events израчунати seed-level `A` и рани gap; у сваком bootstrap-у resample-овати њихових 100 семена. Исти resample индекси унутар варијанте морају се користити за `ΔA` и `E`, јер потичу из истих записа.

- **MISMATCH** — 21 пар нису 21 независна benchmark-а: више димензија је угнежђено у истој функцији. Pair bootstrap и sign test третирају их као независне ([c_study.py:271](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:271)). Spearman није доминиран величином ефекта, али крајњи рангови неколико функција имају велики утицај.

  **Исправка:** bootstrap-овати девет функција као cluster-е, задржавајући њихове димензије, и унапред додати leave-one-function-out анализу утицаја. Ако се задржи pair bootstrap, закључак мора бити ограничен на ових 21 фиксних ћелија, без популационе генерализације.

- **MISMATCH** — нуле/везани рангови нису дефинисани. Код `D0>0` третира тачну нулу као неуспех и задржава denominator 21 ([c_study.py:267](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:267)); то није стандардни exact sign test, који одбацује ties.

  **Исправка:** унапред задати толеранцију за нулу и користити број ненултих парова као denominator, или изричито назвати поступак конзервативним success-count тестом. Архивирани `ΔA_k` и `E_k` тренутно имају 21 јединствену вредност и немају ties; будући `Δ_k` још није познат.

- **MISMATCH** — H64c3 није „додатна информација”; разлика две маргиналне Spearman корелације ([SPEC:11](/Users/danijel/Desktop/gadapt/research/ITERATION64_C_SPEC.md:11)) показује само да је једна маргинална rank асоцијација јача.

  **Исправка:** преименовати исход у „јача маргинална rank асоцијација од baseline-а”. За стварну инкременталну вредност потребан је partial-rank тест или унапред дефинисан out-of-sample модел `E` наспрам `E+Δ`.

- **MISMATCH** — прагови `0.60` и `0.30` су изводљиви, али морају бити описани као различити критеријуми: `0.60` циљна point величина, `0.30` најмањи прихватљив ефекат. Иначе „opposite” користи други праг од point одлуке ([c_study.py:292](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:292)).

### Baseline, freeze и репродуктивност

- **OK** — знак у коду је исправно усаглашен: `ΔA=A_shift-A_rotm`, а `E=gap_rotm-gap_shift`, па позитивно у оба случаја значи да је `rotm` тежи ([c_study.py:248](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:248), [c_study.py:260](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:260)). Спецификација треба експлицитно да наведе овај редослед и формулу „просек log-gap-ова”, а не двосмислено „разлика”.

- **OK за постојеће архиве** — проверено је свих 100 E-shift и 100 R-rotm записа по пару: `calls=12000`, events су потпуни и строго растући, а сваки има запис пре 1.200; нема gap-ова једнаких нули на 1.200. Дакле прозор baseline-а заиста одговара првих 10%.

- **BUG** — `inputs()` не хешира 21 E shift part фајл који анализа чита ([c_study.py:87](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:87), [c_study.py:243](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:243)). Додати њихове SHA-256, као и E `manifest_run/freeze` ако су део provenance-а.

- **BUG** — `analyse` не проверава `run["manifest"]` нити `valid()` за учитане C записе ([c_study.py:218](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:218)). Измењен `run.json.gz` са истим `inputs` може проћи.

  **Исправка:** захтевати `same_build(run["manifest"], pre["manifest"])`, тачно 1.260 јединствених task-ова и `valid` за сваки `k`, уз проверу log димензије и коначности.

- **BUG** — C не захтева да текући GAdapt build буде исти као build који је произвео R. `rs.env_check()` проверава само Python/pip ([r_study.py:139](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:139)). Упоредити C manifest са manifest-ом у R `run/check_repro` за `gadapt_tree`, E код/settings, Python, dependency freeze и mentor commit.

- **BUG** — `stage_run` нема race-safe reservation; два процеса могу истовремено писати исте part фајлове и финални `run` ([c_study.py:167](/Users/danijel/Desktop/gadapt/research/i64/c_study.py:167)). Потребан је процесни `flock` или атомска ексклузивна резервација.

- **MISMATCH** — `c_report.py` и `run_c.sh`, наведени у [SPEC:15](/Users/danijel/Desktop/gadapt/research/ITERATION64_C_SPEC.md:15), тренутно не постоје. Додати их и укључити у freeze manifest, или их уклонити из замрзнуте реализације.

### Overclaim

У забрањене тврдње додати:

- да је хомогенизација дијагонале коваријансе измерена — није, ако се снима само log-relative \(d\);
- да је доказано да губитак dispersion-а узрокује погоршање регулатора — нема интервенције/медијационог теста;
- да H64c3 доказује инкременталну предиктивну вредност;
- генерализацију изван ове GAdapt-M конфигурације, native домена, буџета 1.200 и 21 фиксне ћелије;
- израз „механизам потврђен”; прикладније је „предвиђени коефицијентни потпис подржан”.

Семена су исправна и непоклапајућа са E/R, `rotm` непосредно користи замрзнуту `r_study.rotm_transform`, а ponderi у коду одговарају E. У спецификацији само заменити нејасно `(1/9)/dim` са \(w_{f,d}=(1/9)/m_f\), где је \(m_f\) број испитиваних димензија функције.