#!/bin/bash
# I64-I chain (spec research/ITERATION64_I_SPEC.md); restartable (parts + manifest check). Needs MBENCH and I_PY (the ienv python).
cd "$(dirname "$0")/../.." || exit 1
unset I_OUT I_B I_SEEDS I_BOOT
export MBENCH=${MBENCH:?mentor clone} PYTHONPATH="$PWD"
PY=${I_PY:?ienv python}
W=${1:-4}
OUT=research/results/iteration64_i
[ -f "$OUT/run.json.gz" ] || { echo "=== run $(date)"; nice -n 10 $PY research/i64/i_study.py run $W || { echo "run failed"; exit 2; }; }
[ -f "$OUT/analysis.json.gz" ] || { echo "=== analyse $(date)"; nice -n 10 $PY research/i64/i_study.py analyse || { echo "analyse failed"; exit 2; }; }
echo "I ALL DONE $(date)"
