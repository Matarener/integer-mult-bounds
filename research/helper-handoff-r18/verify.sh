#!/bin/sh
# Reproduce every output of research/helper-handoff-r18 and compare with the stored expected outputs.
# Run from the repository root: sh research/helper-handoff-r18/verify.sh   (python3.12, stdlib only; ~45 s)
set -e
PY=${PY:-python3.12}
D=research/helper-handoff-r18
T=$(mktemp -d)
cd $D
OPENBLAS_NUM_THREADS=1 $PY -B control_4610.py   > $T/control_4610.txt
OPENBLAS_NUM_THREADS=1 $PY -B gadget.py         > $T/gadget.txt
OPENBLAS_NUM_THREADS=1 $PY -B price_handoff.py  > $T/price_handoff.txt
cd screens
for f in relay relay2 spanb presub; do OPENBLAS_NUM_THREADS=1 $PY -B $f.py > $T/$f.txt; done
OPENBLAS_NUM_THREADS=1 $PY -B relay_def.py forward backward > $T/relay_def.txt
cd ..
for f in control_4610 gadget price_handoff; do cmp $T/$f.txt $f.txt; done
for f in relay relay2 spanb presub relay_def; do cmp $T/$f.txt screens/$f.txt; done
grep -q PASS_NREPLAY_CONTROL_4610 control_4610.txt && grep -q PASS_HANDOFF_GADGET gadget.txt && grep -q PASS_PRICE_HANDOFF price_handoff.txt
echo PASS_HELPER_HANDOFF_R18
