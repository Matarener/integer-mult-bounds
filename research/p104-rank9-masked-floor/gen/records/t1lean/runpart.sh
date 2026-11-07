#!/bin/bash
# T1 tables for types k = P, P+4, ...: closure cert (diag gauge tree), pinning, contagion, LRAT, T2Zero mirror.
# usage: bash t1lean/runpart.sh P   (logs t1lean/logs/*-pP.txt)
P=$1; cd "$(dirname "$0")/.."; mkdir -p t1lean/logs t1lean/zero/out
S=t1lean/zero/out
for k in $(seq $P 4 386); do
  [ -f t1lean/zero/out/Z_T1_$k.lean ] && continue
  DTREE=1 T1K=$k python3 t1lean/t1case.py >> t1lean/logs/case-p$P.txt 2>&1
  python3 t1lean/pincheck.py $k >> t1lean/logs/pin-p$P.txt 2>&1
  python3 t1lean/zero/contag.py $k $S/chains-$k.json t1lean/cert/T1_$k.json > $S/contag-$k.txt 2>&1; tail -1 $S/contag-$k.txt >> t1lean/logs/contag-p$P.txt
  python3 t1lean/zero/lrat8.py $k t1lean/cert/T1_$k.json $S/chains-$k.json $S/origin-$k.json $S/proof-$k.lrat >> t1lean/logs/lrat-p$P.txt 2>&1 || echo "LRAT FAIL $k" >> t1lean/logs/lrat-p$P.txt
  python3 kaggle-t2zero/emit_t2zero.py t1lean/cert/T1_$k.json $S/origin-$k.json $S/proof-$k.lrat T1_$k $S/Z_T1_$k.lean >> t1lean/logs/zero-p$P.txt 2>&1 || echo "ZERO FAIL $k" >> t1lean/logs/zero-p$P.txt
done
echo DONE >> t1lean/logs/case-p$P.txt
