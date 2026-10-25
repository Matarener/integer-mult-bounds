# Independent review of the explicit-width synchronized CRT caller

Verdict: **pass within its logical caller scope**. No unresolved correctness
issue was found. The exact primary proof, code, source pins and result hashes
are recorded in `PRIMARY-REVIEW.json`. Separate-agent review is not independent
human review or proof-assistant verification.

## Findings

- The constructor takes ell explicitly and preserves declared widths. In
  particular, the wider-padding fixture uses ell=4 with both heights3 and
  retains both all-idle global rows instead of normalizing ell down.
- The row decoder correctly maps all local rows once in order. The short
  network idles at globals ell-1 and ell. IDLE is represented by None and
  branches before both target selection and table lookup; no phantom bit
  with a zero coefficient is introduced.
- Per-axis networks use exactly 2^h_i wires. Offsets depend only on the
  unchanged left child and fixed moduli. Those offsets are frozen for the
  level, while each later table is queried at the current axis value.
  The predecessor all-active-target omission argument therefore applies.
  This argument and placement coverage are credited to PR4169/PR4174.
- Different target axes commute throughout a level. Removing idle rows
  preserves each axis's complete local word, so interleaving realizes the
  same endpoint as the retained serial arithmetic caller on every padded
  tuple. The globally valid restriction gives the direct CRT map.
- Reversing levels and global rows uses the same positive-offset tables
  in reverse order. This is the literal inverse. It agrees in endpoint
  with the source's separately compiled negative-offset construction.
- Whole-network valid-set preservation is distinguished from transient
  target validity and from pointwise fixation of globally invalid tuples.
  The mutation with path (1,1,3,2) detects incorrect per-switch validity
  gating. The wider-input compiled-helper failure is correctly described
  as an API-domain boundary, not a predecessor theorem defect.
- Coordinates are canonical logical axes. No executed reservoir placement,
  compact macro/repair, tape/E tariff or full physical CRT theorem is claimed.

## Evidence

Before primary inspection, the independent oracle used an earlier separate
FIFO network compiler and brute-force scaled-CRT reconstruction. Normal and
strict optimized runs covered all16,384 main dirty tuples and all64 wider
padding tuples, whole literal inverses, commutation/omission comparisons and
the direct globally valid formula. It remains byte-pinned and unchanged.

The primary was replayed normally and under strict optimization from a
separate git-free copy with its three authenticated source inputs, without
source-root overrides. Both reproduced16,480 padded states and229,984
forward row checks. The stored receipt was compared without rewriting it.

The source-pinned `cross_check.py` was written after primary inspection to
apply the earlier oracle primitives. Both modes passed166 states,3,064
forward/inverse rows,510 decoder comparisons and648 literal idle specs.
It includes supplied-ell/all-short fixtures and singleton axes. It validates
the hashes of primary code, preimplementation oracle and retained source;
the preimplementation oracle also authenticates its earlier FIFO helper.
All referenced helpers are retained beside the receipts.

The independent full main and wider-padding endpoint digests agree with the
primary results. These are semantic checks, not machine timing evidence.

## Remaining obligations and credit

The complete uniform control evaluator, transported descriptors, production
reservoir and exception-set binding, ordinary callee, compact repair tariff,
precision/native/outer multiplication theorem and frontier certification
remain separate. Cinna Davis supplies the original CRT/network construction;
Hiroki KUMAZAKI's PR4169/PR4174 supplies existing omission/repair/placement
coverage. The unchanged earlier FIFO oracle supplies independent numerical
network semantics. No new kappa or selected-frontier change is asserted.
