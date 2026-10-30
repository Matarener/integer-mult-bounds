#!/bin/sh
# usage: sh research/p104-priced-handoff/verify.sh   (from repository root; Python 3.12, stdlib only)
exec python3 -B "$(dirname "$0")/verify.py" "$@"
