# Four sparse E8 cosets stay within deficiency nine

**Partial. No new exponent.**

The standard construction gives 120 root lines of squared length 8. Their
pairwise scalar products lie in `{-4, 0, 4}`. After transport to the identity
bilinear form, the labels are exactly the 9-bit vectors of weights 3 and 7:
84 of weight 3 and 36 of weight 7. Label parity agrees with geometric
orthogonality.

The scalar code is evaluation of these lines over `F3`. It has `3^8 = 6561`
words, and each of the 6560 nonzero words has binary support rank 9. Four
sparse outside cosets were exhausted. Their deficiency sums are 9 for a single
coordinate, 9 for each of the two nonorthogonal pairs, and 7 for the orthogonal
pair. Each sum is at most 9. The selected kappa is unchanged.

## What was executed

The checker builds the root lines and exhausts these four cosets. It does not
exhaust the 130305 pairs.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the one-coset budget in PR 3755,
head `9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to these
four cosets. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/e8-sparse-coset-budget/verify.py
python3.12 -B research/e8-sparse-coset-budget/test_verify.py
python3.12 -B scripts/research_package.py --package research/e8-sparse-coset-budget
```

## Open next questions

These four sums are the coset comparison. The pair exhaustion would leave them.

## Credit

conorholds proved the one-coset budget containing these four sums.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
