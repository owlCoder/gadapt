#!/bin/bash
# I64-S0 chain; restartable (stages with a published artifact are skipped). Interpreter: the mentor's pinned environment.
cd "$(dirname "$0")/../.." || exit 1
unset S0_OUT S0_SEEDS S0_FULL_BOOT
export MBENCH=${MBENCH:?set MBENCH to the gadapt_experiments clone at 0e388356}
PY=${S0_PY:?set S0_PY to the python of the mentor environment}
OUT=research/results/iteration64_s0
for st in gate run analyse; do
  case $st in gate) a=gate;; run) a=runs;; analyse) a=analysis;; esac
  [ -f "$OUT/$a.json.gz" ] && { echo "skip $st"; continue; }
  echo "=== $st $(date)"; nice -n 10 $PY research/i64/s0_replication.py $st || { echo "stage $st failed"; exit 2; }
done
echo "S0 ALL DONE $(date)"
