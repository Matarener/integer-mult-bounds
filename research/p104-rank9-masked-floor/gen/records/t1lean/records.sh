#!/bin/bash
# Records T1_<k>.txt, T3_<k>.txt (Lean data) for every type whose zero certificate passed.  usage: bash t1lean/records.sh
cd "$(dirname "$0")/.."; S=t1lean/zero/out; R=t1lean/records; mkdir -p $R
for f in $S/Z_T1_*.lean; do
  k=$(basename $f .lean | sed "s/Z_T1_//"); [ -f $R/T1_$k.txt ] && [ -f $R/T3_$k.txt ] && [ $R/T3_$k.txt -nt t1lean/t3data.py ] && continue
  ZJSON=$S/zj-$k.json python3 kaggle-t2zero/emit_t2zero.py t1lean/cert/T1_$k.json $S/origin-$k.json $S/proof-$k.lrat T1_$k /dev/null > /dev/null 2>&1 || { echo "ZJ FAIL $k"; continue; }
  python3 t1lean/wdata.py t1lean/cert/T1_$k.json $S/zj-$k.json $R/T1_$k.txt > /dev/null || echo "W1 FAIL $k"
  python3 t1lean/t3data.py $k $PWD/t1lean/cert/T1_$k.json $PWD/$R/T3_$k.txt || echo "T3 FAIL $k"
done
