# Scalar instructions of the selected word lift at every column multiplicity

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No new κ. Assumption ID: `native_all_columns`. This is one implication, not that assumption and not the other four.

## 1. Proposition

Let the selected word be `research/p104-helper-subspace-splits/WORD.json.gz` on canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a` (PR #5599, κ = 62009/20000000). Evaluate it by the convention in the selected review and in #5442: a register at chart `C` stores logical coordinates `u`, the physical vector at column multiplicity `f ≥ 1` is `C^{(⊗)f} u`, and a scalar coefficient stays outside the tensor power.

**Proposition.** Every `SCALE`, `ADD` and `COPY` in that word acts on those logical coordinates by the same rational matrix at every integer `f ≥ 1`. The 342 events added to the pinned PR5565 word are 300 `ADD`s and 42 `SCALE`s, so they are included. The 3,447 `MOVE`s are not.

The selected author proof states the corresponding sentence for the three basis changes. The maintainer review still lists universal native implementation at every positive column multiplicity as assumption `native_all_columns`. The argument below discharges only the scalar-instruction part of that sentence. It does not rerun the finite endpoint replay and does not treat a finite width as the proof.

## 2. Lemmas

Let `C` be an invertible linear operator on a finite-dimensional space `V`. Write `C^{(⊗)f}` for its `f`-fold tensor power on `V^{(⊗)f}`, and write `(C^{(⊗)f})^{-1} = (C^{-1})^{(⊗)f}`.

**Lemma A (scale).** For every scalar `q` and every `f ≥ 1`,

```text
C^{(⊗)f}(q u) = q C^{(⊗)f} u.
```

*Proof.* A scalar factors through every linear map, hence through each tensor factor and through their product. ∎

**Lemma B (common chart).** If both operands are logical coordinates of the same chart `C`, physical addition and return to that chart are

```text
(C^{(⊗)f})^{-1}(C^{(⊗)f} u + q C^{(⊗)f} v) = u + q v.
```

`COPY` of `q v` into a zero logical register is the same identity with `u = 0`.

*Proof.* `(C^{-1})^{(⊗)1} C^{(⊗)1} = I`. If it holds at `f`, the mixed-product identity `(A⊗B)(C⊗D) = (AC)⊗(BD)` gives

```text
(C^{-1})^{(⊗)(f+1)} C^{(⊗)(f+1)}
  = ((C^{-1})^{(⊗)f} C^{(⊗)f}) ⊗ (C^{-1} C) = I.
```

The scalar `q` then passes through that inverse. ∎

**Lemma C (distinct charts).** If the destination chart is `C_R` and the source chart is `C_S`, the same reading is

```text
u + q (C_R^{-1} C_S)^{(⊗)f} v.
```

This equals `u + q v` for every `f ≥ 1` and all vectors if and only if `C_R^{-1} C_S = I`. The "only if" is the case `f = 1`. The "if" is Lemma B.

*Phase trap.* If `C_R^{-1} C_S = -I`, the correction is `(-1)^f`. The width-free update `u + q v` is therefore right for every even `f` and wrong for every odd `f`. Agreement at width 2 does not imply agreement at width 1 or width 3. A finite-width sample cannot replace the common-chart hypothesis.

`verify.py` checks Lemma A and Lemma B on three invertible charts (Pauli `X`, the shear `[[1,1],[0,1]]`, and `[[2,3],[5,7]]`) at widths 1, 2 and 3, and checks the mixed-product step on each chart. It checks the phase trap for `q = -1/2` and `v = e_0`: widths 1 and 3 miss the width-free replay, and width 2 hits it. Pauli `X` misses the replay at all three widths, and `X⊗X` is distinct from `X⊗I`. These specimens support the tensor implementation. The all-`f` statement is the induction above.

## 3. Binding to the selected caller

`local.py` in the selected package accepts a scalar event only when its frame tag equals the current chart of every operand. `MOVE` replaces that current chart; `INIT` and `CLEAR` set or drop it. `verify.py` reimplements that chart rule and no other acceptance test.

On the selected word the walk accepts every event and counts 21,247 `ADD`, 757 `SCALE`, 8 `COPY` and 3,447 `MOVE`. The chart list is identical to `inputs/PR5565-WORD.json.gz`. Relative to that word the opcode delta is `+300 ADD`, `+42 SCALE`, and zero `MOVE`, `INIT`, `COPY` or `CLEAR` (25,133 events to 25,475; 735 public fields to 748). The thirteen helper splits therefore added only instructions covered by Lemmas A and B. The same chart indices denote the same operators before and after those splits.

A synthetic `ADD` whose operands are at charts 4 and 5 is rejected. An `ADD` that still carries the pre-`MOVE` frame is rejected. Adding one to the frame tag of the first selected `ADD` is rejected. Those controls are finite rejection tests of the walker. They are not the all-width proof.

## 4. What remains

This does not prove that a `MOVE` from chart `A` to chart `B` equals `(chart_B^{-1} chart_A)^{(⊗)f}` on the tape, with the signed Pauli image and absolute phase. The selected `native` checker compares width-1 recipes. #5442 (Matarener) proves the group-algebra half of `native_all_columns` for the older #5413 caller, which does not contain these scalar bases and is not this word.

Spectators, whole-job adapters and fixed-tape tariffs stay open. `owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery` are untouched. Dyadic denominator bounds are a precision obligation and are not re-audited here. No outer row, admitted BIT budget or selected κ changes. #5625 (CRT row reentry) and #5707 (root-prefix lowering) are partial interfaces of other callers; neither is this implication.

## 5. Downstream effect

The width-free rational rows already used for this word's scalar program remain the logical coordinates at every positive column multiplicity, for `SCALE`, `ADD` and `COPY` only. Any later all-width claim for a `MOVE`, a native adapter or a different word still has to be proved on its own hypothesis.
