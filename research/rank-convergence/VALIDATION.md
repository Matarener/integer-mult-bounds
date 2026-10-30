# Validation and limits

Author-side validation on 2026-10-22, Python 3.12.8, macOS arm64.
Substantial OpenAI Codex assistance; separate Sol 6.1 medium agents reviewed
proof algebra, finite chronology and numerical/source bindings. This is not
formal or independent human acceptance.

## Scientific replay

- `python3.12 -B research/rank-convergence/verify.py --write`: passed;
  regenerates the exact receipt explicitly.
- `python3.12 -I -O -B research/rank-convergence/verify.py`: passed during
  development; the final exported-byte replay is recorded below.
- `python3.12 -B scripts/research_package.py --package research/rank-convergence`:
  passed before adding retained original license/notice inputs; the final
  registered replay and transport checks are recorded below.
- Thirteen test methods include 80 literal fixtures (43 above the old height),
  24 independent ordered-word flow comparisons, exact cancellation and mirror
  checks, empty-root and small-root examples, and invalid/corrupted inputs.
- Four exact compiler certificates across three raw profiles; eight invalid
  numerical witnesses rejected. The p7 local-exponent upper endpoint must be
  `.997481`; the earlier `.9974808` is rejected.

The checks use exact Fraction intervals with explicit logarithm and exponential
tails. Floating-point calculations appear only in regression tests, not in
accepted scientific gates. All native and outer producer receipts are inherited
and authenticated, not freshly replayed. No Lean, Docker, native heavy replay,
full physical/precision instantiation or winning-word materialization was run.
The selected frontier remains unchanged.

## Source and runtime transport

Live mathematical sources, consumer receipts and baseline comparisons are
SHA256/Git-blob authenticated. The predecessor flow authenticates before
execution. Original Sussman license and notice are retained in the explicit
export closure. All changed research is scoped to this package.

Scientific commit: `527dc558072f0336b3b0b8023fd972f0af398d15`.

- Final registered replay with the original Sussman license and notice inputs:
  `PASS_REGISTERED_RESEARCH_PACKAGE`, outcome completed.
- `python3.12 -B scripts/check_research_commit.py --package research/rank-convergence`:
  `PASS_RESEARCH_COMMIT_BYTES`, 26 files.
- `python3.12 -B scripts/export_research_package.py export --package research/rank-convergence --output /tmp/rank-convergence-science.tar`:
  `PASS_RESEARCH_EXPORT`, 26 files; archive checker passed.
- Extracted to a fresh directory with no `.git`. Direct replay with
  `python3.12 -I -O -B`, absolute interpreter path and `PATH=/nonexistent`:
  `PASS_PADDING_FREE_ADAPTIVE_COMPILER`, all four certificates, 13 tests and
  eight rejected witnesses. Neither Git nor an undeclared Python dependency
  was available through PATH.
- Altering the extracted predecessor flow bytes is rejected before execution.
  A first external test harness expected the wrong diagnostic substring;
  the verifier itself rejected correctly. The harness was corrected.
- Altering the extracted exact RESULT receipt is rejected after recomputation;
  both exported mutation controls passed. Original extracted bytes were restored.

Only documentation and validation metadata were edited after the scientific
commit. Full source-history ancestry checking requires an unshallow repository
and is not claimed here.
