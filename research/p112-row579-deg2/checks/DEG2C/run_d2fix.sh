#!/usr/bin/env bash
# DEG2 impl C driver (d2fix.c = the FIXED oracle; see NOTES.md "Oracle bug").  usage: run_d2fix.sh WORKDIR [ctl|deg2]
#   ctl  : controls (all-root MODE 1: a root-only triple (K=3) and quad (K=4) configuration are FOUND), ~minutes; default mode of verify.sh
#   deg2 : FULL rerun of the 64 leaf jobs `d2fix 6 0 TYPE 1 SHARD NS` (list = `coverage.py --leaves`: NS=8, 32 or 128, see coverage.py), 3 at a time,
#          each under timeout $DEG2C_TMO (default 10800 s; the recorded run used 1150 s for NS=8, longer for the split shards; HOURS in total).
#          Writes WORKDIR/out/{fix,fix2,fix4}/NAME.out in the recorded format, then checks (a) coverage.py on the rerun and (b) every TYPE line equals the recorded one.
set -u; H=$(cd "$(dirname "$0")" && pwd); W=${1:-$(mktemp -d)}; M=${2:-ctl}; mkdir -p "$W"; W=$(cd "$W" && pwd); cd "$W" || exit 2
PY="${PYTHON:-python3}"
cp "$H/d2fix.c" .; cc -O2 -o d2fix d2fix.c 2>/dev/null || cc -O2 -o d2fix d2fix.c || { echo "FAIL build d2fix"; exit 1; }
if [ "$M" = ctl ]; then
  r3=$(FIRST=1 timeout 1100 ./d2fix 3 1 0 1 2>&1 | grep -E '^FOUND' | head -n 1); r4=$(FIRST=1 timeout 1100 ./d2fix 4 1 0 1 2>&1 | grep -E '^FOUND' | head -n 1)
  echo "ctl K=3 MODE1: $r3"; echo "ctl K=4 MODE1: $r4"
  [ -n "$r3" ] && [ -n "$r4" ] && echo "PASS DEG2C controls: root-only configurations FOUND at K=3 and K=4" || echo "FAIL DEG2C controls: K=3 '${r3:-none}' K=4 '${r4:-none}'"
else
  mkdir -p out/fix out/fix2 out/fix4; cp "$H"/out/fix2/jobs.txt out/fix2/; cp "$H"/out/fix4/jobs.txt out/fix4/
  FIRST=1 timeout 1100 ./d2fix 3 1 0 1 >/dev/null 2>&1   # builds LM.bin once (maximal 7-flat masks), shared by all jobs
  cat > worker.sh <<'WEOF'
#!/bin/sh
# args: TYPE SHARD NS DIR NAME
mkdir -p "j_$5"; cp LM.bin "j_$5/" 2>/dev/null; cd "j_$5" || exit 2
timeout "${DEG2C_TMO:-10800}" ../d2fix 6 0 "$1" 1 "$2" "$3" > out 2>/dev/null; echo "rc=$?" >> out; cp out "../out/$4/$5.out"
WEOF
  "$PY" -B "$H/coverage.py" --leaves | xargs -P3 -L1 sh worker.sh
  "$PY" -B "$H/coverage.py" "$W/out" | tail -n 3
  bad=0; for f in "$H"/out/fix*/t*.out; do n=${f#"$H"/out/}; grep -q '^rc=0' "$f" || continue; [ "$(grep '^TYPE' "$f")" = "$(grep '^TYPE' "$W/out/$n" 2>/dev/null)" ] || { echo "MISMATCH $n"; bad=1; }; done
  [ $bad = 0 ] && echo "PASS DEG2C full rerun: all recorded TYPE lines reproduced" || echo "FAIL DEG2C full rerun"
fi
