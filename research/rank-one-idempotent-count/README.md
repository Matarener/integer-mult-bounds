# The three-bit ring has 28 rank-one idempotents

**Partial. No new exponent.**

A rank-one matrix in `M_3(F_2)` has the form `u v^T` with `u` nonzero. There
are 7 choices for `u` and 7 choices for `v`, so there are 49 such matrices.
The square is

`(u v^T)^2 = (v · u) u v^T`.

It equals the matrix exactly when `v · u = 1`. For each nonzero `u`, four of
the eight dual vectors have that trace. The resulting 28 matrices are
distinct, because the image vector determines `u` and the matrix then
determines `v`. Each has trace 1. The other 21 rank-one matrices have trace 0
and are not idempotent. The selected kappa is unchanged.

## What was executed

The checker builds all 49 products and separates them. It does not search
words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the idempotent count in
PR 3774, head `713c28c1b0ebbdf3f30d7887fcb173e7a786f245`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rank-one-idempotent-count/verify.py
python3.12 -B research/rank-one-idempotent-count/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank-one-idempotent-count
```

## Open next questions

This count is the three-bit projector set. A wider register would leave it.

## Credit

Wentao Li recorded this count of 28 trace-one idempotents. The rank-one call
model is credited there to eumemic and woklerx.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
