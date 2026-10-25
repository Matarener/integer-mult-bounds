#!/bin/sh
# Re-verify the Gaussian-E8 c = 20 certificates from scratch.
# Usage: sh verify.sh OUTDIR        (needs python3 with numpy, scipy, highspy)
#        PY=/path/to/python sh verify.sh OUTDIR
# Rebuilds the type tables, unpacks the shipped certificates and checks each one with
# the pure-integer verifier ecert.py.  Exit 0 iff every shipped certificate is EXCLUDED.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?usage: sh verify.sh OUTDIR}"
PY="${PY:-python3}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$OUT"
cp "$HERE"/scripts/*.py "$HERE"/data/flats_Gauss.pkl "$OUT"/
cd "$OUT"
echo "[1/3] rebuilding tables"
"$PY" -B hits_table.py > hits_table.log 2>&1
"$PY" -B orbits.py > orbits.log 2>&1
"$PY" -B types_e.py 256 > types_e.log 2>&1
"$PY" -B dom.py > dom.log 2>&1
"$PY" -B lift_prep.py > lift_prep.log 2>&1
echo "[2/3] unpacking certificates"
mkdir -p certs
for f in "$HERE"/certs/*.pkl.gz; do gunzip -c "$f" > "certs/$(basename "$f" .gz)"; done
echo "[3/3] exact verification"
n=0; ok=0
for f in certs/*.pkl; do
  n=$((n+1))
  line=$("$PY" -B ecert.py "$f" 2>&1 | tail -1)
  echo "$line"
  case "$line" in *"EXCLUDED (exact"*) ok=$((ok+1));; esac
done
echo "verified $ok / $n certificates EXCLUDED (exact)"
[ "$ok" -eq "$n" ]
