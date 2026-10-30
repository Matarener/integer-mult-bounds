# Scalar half of `native_all_columns` for the selected #5599 word

**Scoped proof; no new κ.** Every `SCALE`, `ADD` and `COPY` in the selected helper-subspace word acts by the same rational matrix at every column multiplicity `f ≥ 1`. The 342 events added to the pinned PR5565 word are 300 `ADD`s and 42 `SCALE`s, so the thirteen helper splits sit inside that class. The 3,447 `MOVE`s stay inside assumption `native_all_columns`.

The proof is [PROOF.md](PROOF.md). The width-free cancellation

```text
(C^{(⊗)f})^{-1}(C^{(⊗)f} u + q C^{(⊗)f} v) = u + q v
```

is an induction on `f` for one common chart `C`. If the charts differ by `-I`, the correction is `(-1)^f`: width 2 matches the width-free replay and widths 1 and 3 do not. A finite width does not discharge the statement.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to assumption ID `native_all_columns` and this scalar implication. The actual question, the reason for the refinement and the stop rule are in [TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json). Base commit `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. Selected κ remains `62009/20000000`.

The chart walk on the selected word reports zero common-chart violations: 21,247 `ADD`, 757 `SCALE`, 8 `COPY`, 3,447 `MOVE`. The chart list matches the PR5565 word. Opcode delta `+300 ADD +42 SCALE +0 MOVE`.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/native-scalar-chart-lift/verify.py
python3 -O -B research/native-scalar-chart-lift/verify.py
python3 -B scripts/research_package.py --package research/native-scalar-chart-lift --check-only
python3 -B scripts/research_package.py --package research/native-scalar-chart-lift
```

Expected direct marker:

```text
PASS_NATIVE_SCALAR_CHART_LIFT adds=21247 scales=757 copies=8 moves=3447 common_chart_violations=0 split_delta_add=300 split_delta_scale=42 split_delta_move=0
```

The checker also rejects a cross-chart synthetic `ADD`, a stale frame tag after `MOVE`, and a one-step retag of the first selected `ADD`. It checks Pauli `X`, a shear and `[[2,3],[5,7]]` at widths 1, 2 and 3. Those widths are controls on the tensor code. The all-`f` argument is the induction in [PROOF.md](PROOF.md).

Not run: `make frontier5599-verify`, native Clifford replay, Lean, and any proof of `MOVE` operators.

## Open next questions

Can the 3,447 retained `MOVE` chart changes of this same word be lifted by `g ↦ g^{(⊗)f}` with absolute phase, as group identities rather than width-1 recipe checks?

That is the remaining algebraic content of `native_all_columns` for the selected caller. Scalar instructions no longer carry it. The smallest step is to census one distinct `(source frame, destination frame)` pair through the pinned `clifford_exact` canonical frames and apply the #5442 lifting lemma, including the action on `|0>`. The selected `native` checker only compares width-1 signed Pauli recipes. A passing census would still leave spectators, whole-job adapters and the fixed-tape tariff open.

## Credit

The selected word and the common-chart sentence are Ali Romman's PR #5599, using Pierre-Loic Doulcet / hexapode's PR #5565 word and the caller lineage credited in `research/p104-helper-subspace-splits/README.md`. The selected review is `docs/research/pr-intake-evidence/pr5599-completion/PROOF-REVIEW.md`. The convention that a scalar coefficient stays outside the tensor power is the one used by #5442 and stated for the older #4610 admission in `research/final4610-independent-admission`. #5442 (Mark / Matarener) proves the group-algebra half of `native_all_columns` for the older #5413 caller; it does not contain these scalar bases. #5625 and #5707 are different partial interfaces and are not reused as a proof of this implication.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
