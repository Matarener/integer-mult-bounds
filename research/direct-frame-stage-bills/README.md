# The direct frame schedule exceeds capacity by 3552

**Partial. No new exponent.**

The retained odd-stage recipe uses width `m = 1 + 7L` and live width
`W = 2 K v T`, where `L = 2K + 1`. Its idle advances charge `2 v T` at the
ranks written in the recipe. On the direct profile, each live port contributes
one rank-7 move and one rank-8 move at every stage.

With the pinned counts `v = 111` and `T = 32`, the paid mass is

`v L T (14 K + 1)`.

Capacity is smaller by exactly `v T = 3552` at every odd stage count. The
5, 9 and 11 stage bills are therefore

`145/144`, `513/512` and `781/780`.

The same excess appears in the histograms. At 9 stages the counts are
`{7: 53280, 8: 31968, 14: 14208, 28: 14208, 42: 14208}`. At 5 and 11 stages
the checker records the corresponding counts. The selected kappa is unchanged.

## What was executed

The checker reads the pinned recipe and applies those idle rules. It does
not replay bridge columns or repair address junctions.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the direct-frame bill in
PR 3772, head `5b1d4c2ade90dfa0d8b837148cc5b9cc4be1cdab`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to these
three bills. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the odd-stage recipe,
the replica count and the live port count. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/direct-frame-stage-bills/verify.py
python3.12 -B research/direct-frame-stage-bills/test_verify.py
python3.12 -B scripts/research_package.py --package research/direct-frame-stage-bills
```

## Open next questions

These bills are the schedule. A matched-endpoint word would leave them.

## Credit

DreamingOfClouds wrote the odd-stage recipe. Gonzalo Mier recorded these
direct-frame bills. The recipe file also names Zhihao Chen, eumemic and
chafreaky.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
