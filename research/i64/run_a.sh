#!/bin/bash
# I64-A chain (spec research/ITERATION64_A_SPEC.md); restartable: finished stages are skipped, `run` resumes by cell after validation.
cd "$(dirname "$0")/../.." || exit 1
unset A_OUT A_E3_OUT E_OUT E_SEEDS E3_OUT
export MBENCH=${MBENCH:?clone of gadapt_experiments at 0e388356} A_FREEZE_COMMIT=${A_FREEZE_COMMIT:?commit that froze the A spec and code}
PY=${E_PY:?python of the eenv}
W=${1:-4}
OUT=research/results/iteration64_a
mkdir -p $OUT
for st in check_repro run analyse; do
  case $st in analyse) a=analysis;; *) a=$st;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 $PY research/i64/a_study.py $st $W || { echo "stage $st failed"; exit 2; }
done
echo "A ALL DONE $(date)"
