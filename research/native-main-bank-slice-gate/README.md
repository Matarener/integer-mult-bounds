# Exact price gates for eight native main-bank slices

This scoped negative result checks eight declared slices of the frozen
PR #4610 native word. Set one main bank, or both main banks, to owned zero.
Keep all 408 independent helper outputs and the stated main output bank.
Remove paid calls on proved zero rows and events outside the exact backward
dependency slice. Every resulting paid invoice is strictly worse than its
complete target list for each tariff H_r = r^t with 0 < t < 1.

The complete kappa calculation does not improve. The result rules out these
eight optimistic invoices and two specified prefix variants. It is not a
lower bound for other pruning methods, new identities, changed words, or
coupled callers. No selected record is changed.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), and
[SOURCES.json](SOURCES.json). The publication base is
`32890bc5de034ab8fc93ac88ead7279a6a416d04`.

## Exact scope

The forward logical endpoint is `(x, y+x, h)`. The backward endpoint is
`(x-y, y, h)`. Here each main bank has 112 fields and h has 408 arbitrary
independent fields. The owned center starts and ends at zero. Source native
maps and frame tags are not removed by a claim of physical equivalence.
Instead, the price test grants any needed physical repair for free. This
makes the declared candidate invoice more favorable.

In both orientations the same-bank cases are X to X and Y to Y. The nonzero
cross-bank case is X to Y forward and Y to X backward. The eighth case has
both main banks zero and retains only h. The formal replay checks every
original endpoint and then replays each retained event slice separately.
It also checks two forward variants which omit the 6,037-record zero-frame
prefix before `entry_adapters`.

All cases credit the helper census `{4:28,7:7,8:47,9:326}`. A retained
same-bank output adds 112 H8 targets; a cross-bank output adds 112 H9 targets.
The following rank surplus is target rank minus paid rank. It does not by
itself prove the power-cost result; the nine exact hinge values do that.

| Direction | Input | Output | Rank surplus |
| --- | --- | --- | ---: |
| Forward | X | X | 0 |
| Forward | X | Y | -842 |
| Forward | Y | Y | -195 |
| Forward | None | Helpers only | -131 |
| Backward | X | X | 0 |
| Backward | Y | X | -848 |
| Backward | Y | Y | -881 |
| Backward | None | Helpers only | -704 |

The zero-surplus X-to-X invoice is
`1951 H1 + 267 H2 + 470 H3 + 103 H4 + 12 H5`. Its hinge certificate at
ranks 1 through 9 is
`[2283,2615,2680,2275,1795,1303,811,326,0]`.
Thus even the two zero-surplus cases have a strict deficit at every
strictly concave power tariff. All other cases have positive hinges at all
nine ranks. The two prefix variants have the same paid histograms as the
corresponding full-prefix slices.

## Replay

Use Python 3.12 with the standard library:

```sh
python3 -B research/native-main-bank-slice-gate/verify.py
python3 -O -B research/native-main-bank-slice-gate/verify.py
python3 -B scripts/research_package.py --package research/native-main-bank-slice-gate
```

Expected direct marker:

```text
PASS_NATIVE_MAIN_BANK_SLICE_GATE_NO_NEW_KAPPA
```

The verifier binds both live inputs by SHA256. It binds the decompressed
native payload separately, rebuilds all formal rows with exact rational
coefficients and free-group warp words, derives each slice and invoice,
and compares the full result with the frozen receipt. It computes the
hinges itself and cross-checks their sign with the shared invoice tool.
Controls reject changed source bytes, a wrong sign in the last helper ADD,
a missing independent helper output, and unearned target credit. A
separate positive concavity case checks the direction of the comparison.

The author-only `--write-result` option writes a new receipt. It does not
perform a frozen-receipt check and is not in the registered replay.

No physical payload, absolute phase, frame repair, full GL cover, compiler,
ordinary precision, tape, or outer multiplication replay is supplied. Those
costs cannot make a failing optimistic invoice profitable. This statement
does not show that every cheaper implementation has been found.

## Open next questions

Can a changed scalar word or a physical identity give a cheaper restricted
source? First supply that word, replay its exact endpoint, and reconstruct
all paid and target counts. The present slice does not bound this work.
[TASK.json](TASK.json) records the blocker and first experiment.

## Credit

Cao Yifan supplies [PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
and the [frozen native word](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz).
Its [source notice](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/kappa-round3-warp-20261022/README.md)
credits Cinna Davis, Dugongue, zxv, Jacob Alan Sussman, Pierre-Loic Doulcet,
and the retained native, controller, and compiler lineage.

[PR #5397](https://github.com/CrocSwap/integer-mult-bounds/pull/5397) supplies
the [signed invoice interface](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/scripts/compare_recursive_invoices.py).
Its classical concave-order test and credited predecessors are reused, not
claimed as a new theorem. This package changes the main-bank input domain;
it does not repeat that PR's fixed eight helper-relation census.

New slice analysis, exact proof, and checks: Ali Romman, with substantial
OpenAI Codex assistance. Apache-2.0. No predecessor source is changed.
