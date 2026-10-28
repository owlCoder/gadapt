#!/bin/bash
# I64-E chain (spec research/ITERATION64_E_SPEC.md); restartable: finished stages are skipped, `run` resumes by cell.
cd "$(dirname "$0")/../.." || exit 1
unset E_OUT E_B E_SEEDS E_DEV_SEEDS E_BOOT
export MBENCH=${MBENCH:?clone of gadapt_experiments at 0e388356}
PY=${E_PY:?python of the eenv}
W=${1:-1}
OUT=research/results/iteration64_e
for st in normalizers dev freeze run analyse; do
  case $st in analyse) a=analysis;; *) a=$st;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 $PY research/i64/e_study.py $st $W || { echo "stage $st failed"; exit 2; }
done
echo "E ALL DONE $(date)"
