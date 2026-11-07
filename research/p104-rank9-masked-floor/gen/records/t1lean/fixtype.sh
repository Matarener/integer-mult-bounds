#!/bin/bash
# For a type whose T3 record failed (no frame inside zm, or a line not pinned in one step): try other closure
# variants (gauge tree without diagonals / with rule (b)); keep the first whose T3 record passes, then redo the zero
# step and the records.  usage: bash t1lean/fixtype.sh k
k=$1; cd "$(dirname "$0")/.."; S=t1lean/zero/out; R=t1lean/records
for cfg in "DTREE= RULES=ac" "DTREE=1 RULES=abc" "DTREE= RULES=abc"; do
  env $cfg T1K=$k python3 t1lean/t1case.py >> t1lean/logs/fix.txt 2>&1
  if python3 t1lean/t3data.py $k $PWD/t1lean/cert/T1_$k.json $PWD/$R/T3_$k.txt >> t1lean/logs/fix.txt 2>&1; then
    python3 t1lean/zero/contag.py $k $S/chains-$k.json t1lean/cert/T1_$k.json > $S/contag-$k.txt 2>&1
    python3 t1lean/zero/lrat8.py $k t1lean/cert/T1_$k.json $S/chains-$k.json $S/origin-$k.json $S/proof-$k.lrat > /dev/null 2>&1 || { echo "FIX $k [$cfg] LRAT FAIL"; exit 1; }
    ZJSON=$S/zj-$k.json python3 kaggle-t2zero/emit_t2zero.py t1lean/cert/T1_$k.json $S/origin-$k.json $S/proof-$k.lrat T1_$k $S/Z_T1_$k.lean > /dev/null 2>&1 || { echo "FIX $k [$cfg] ZERO FAIL"; exit 1; }
    python3 t1lean/wdata.py t1lean/cert/T1_$k.json $S/zj-$k.json $R/T1_$k.txt > /dev/null
    echo "FIX $k OK [$cfg]"; exit 0
  fi
done
rm -f $R/T3_$k.txt; echo "FIX $k NONE"; exit 1
