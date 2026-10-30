#!/bin/sh
# Exhaustive hand-off screens on PR5561's headline word (python3.12, stdlib). Writes tools/*.txt.
# usage: sh research/p104-priced-handoff/tools/run_screens.sh   (from repository root; ~5 min)
D="$(dirname "$0")"; W="$D/../inputs/pr5561-WORD.json.gz"; O="${TMPDIR:-/tmp}"
python3 -B "$D/screen.py"   "$W" "$O/r21-screen.json"  > "$D/screen.txt"
python3 -B "$D/screen2.py"  "$W" "$O/r21-screen2.json" > "$D/screen2.txt"
python3 -B "$D/windows.py"  "$W"                       > "$D/windows.txt"
python3 -B "$D/partner.py"  "$W" "$O/r21-partner.json" > "$D/partner.txt"
python3 -B "$D/lift21.py"   "$W" "$O/r21-lift.json" | grep -v '^ev ' > "$D/lift21.txt"
