#!/bin/bash
# I64-C chain (spec research/ITERATION64_C_SPEC.md); restartable: finished stages are skipped, `run` resumes by pair after validation.
cd "$(dirname "$0")/../.." || exit 1
unset C_OUT R_OUT E_OUT E_SEEDS
export MBENCH=${MBENCH:?clone of gadapt_experiments at 0e388356} C_FREEZE_COMMIT=${C_FREEZE_COMMIT:?commit that froze the C spec and code}
PY=${E_PY:?python of the eenv}
W=${1:-4}
OUT=research/results/iteration64_c
mkdir -p $OUT
for st in preflight run analyse; do
  case $st in analyse) a=analysis;; *) a=$st;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 $PY research/i64/c_study.py $st $W || { echo "stage $st failed"; exit 2; }
done
echo "C ALL DONE $(date)"
