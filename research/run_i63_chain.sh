#!/bin/bash
# I63 chain (protocol research/ITERATION63_PROTOCOL.md). Restartable after a crash: stages with a published manifest are skipped;
# a protocol STOP (results/iteration63/STOP.json.gz) ends the chain and is final. Never set I63_TESTING / I63_TEMP here.
cd "$(dirname "$0")/.." || exit 1
unset I63_TESTING I63_TEMP
OUT=research/results/iteration63
W=${1:-9}
for st in gate normalizers fxt rehearsal power freeze test check analyse; do
  case $st in gate) m=manifest_gate;; analyse) m=manifest_analysis;; *) m=manifest_$st;; esac
  [ -f "$OUT/$m.json.gz" ] && { echo "skip $st"; continue; }
  [ -f "$OUT/STOP.json.gz" ] && { echo "STOP.json present: terminal"; exit 3; }
  echo "=== $st $(date)"
  .venv/bin/python research/iteration63_replication.py "$st" "$W" || { echo "stage $st exited non-zero $(date)"; exit 2; }
done
echo "I63 ALL DONE $(date)"
