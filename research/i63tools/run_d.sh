#!/bin/bash
# I63-D chain (descriptive extension; see research/i63tools/d_study.py). Restartable: finished stages are skipped, `run` resumes by cell.
cd "$(dirname "$0")/../.." || exit 1
unset I63_TESTING I63_TEMP D_OUT D_N
W=${1:-5}
OUT=research/results/iteration63d
for st in gate run check analyse; do
  case $st in analyse) a=analysis;; *) a=$st;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 .venv/bin/python research/i63tools/d_study.py $st $W || { echo "stage $st failed"; exit 2; }
done
echo "D ALL DONE $(date)"
