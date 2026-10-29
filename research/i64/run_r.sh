#!/bin/bash
# I64-R chain (spec research/ITERATION64_R_SPEC.md); restartable: finished stages are skipped, `run` resumes by pair after validation.
cd "$(dirname "$0")/../.." || exit 1
unset R_OUT E_OUT E_SEEDS E_DEV_SEEDS
export MBENCH=${MBENCH:?clone of gadapt_experiments at 0e388356} R_FREEZE_COMMIT=${R_FREEZE_COMMIT:?commit that froze the R spec and code}
PY=${E_PY:?python of the eenv}
W=${1:-4}
OUT=research/results/iteration64_r
mkdir -p $OUT
for st in check_repro run analyse; do
  case $st in analyse) a=analysis;; *) a=$st;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 $PY research/i64/r_study.py $st $W || { echo "stage $st failed"; exit 2; }
done
echo "R ALL DONE $(date)"
