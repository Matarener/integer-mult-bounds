#!/usr/bin/env bash
# Kernel-check both files: Lean v4.21.0 (elan) + the pinned Mathlib cache; reject sorry, errors and non-standard axioms.
set -euo pipefail
cd "$(dirname "$0")"
command -v lake >/dev/null || { curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none >/dev/null; export PATH="$HOME/.elan/bin:$PATH"; }
lake exe cache get > cache.log 2>&1 || { tail -20 cache.log; exit 1; }
for f in V4Duality.lean V4Rank.lean; do
  echo "=== $f"
  lake env lean -DwarningAsError=true "$f" 2>&1 | tee "$f.out"
  if grep -q "sorry" "$f.out"; then echo "SORRY in $f"; exit 1; fi
  if grep -q "error" "$f.out"; then echo "ERROR in $f"; exit 1; fi
  if grep "depends on axioms" "$f.out" | grep -v -E "\[(propext|Classical.choice|Quot.sound)(, (propext|Classical.choice|Quot.sound))*\]$"; then echo "BAD AXIOMS"; exit 1; fi
done
rm -f cache.log ./*.out
echo "ALL LEAN CHECKS PASSED"
