# Normalized ranks at most nine have COPY floor 72

**Partial. No new exponent.**

On a nondegenerate nine-bit form, the pairing rank of two subspaces is at
least the sum of their dimensions minus 9. The nine-bit dot product has rank
9. The same comparison holds for every pair of subspaces of a three-bit
space.

A normalized exact factorization has factor ranks `8 + s` and `8 + t` with
`s, t` in `{0, 1}`. The one-coset budget limits the two deficiency sums by
`9s` and `9t`, so

```text
COPY >= 9(m - s - t).
```

Sylvester's inequality on a product of rank 8 gives `m >= 8 + s + t`. Every
one of the four rank pairs therefore has COPY at least `9 * 8 = 72`. The
one-sided counts `9(8 + s) - 9s` are the same number.

The orthogonal frame

```text
e_{2a} + e_{2a+1},   e_{2a} - e_{2a+1},   a = 0, 1, 2, 3
```

has eight vectors of squared length 2, and the sum of their outer products
is twice the identity. Eight terms of cost 9 add to 72. The selected kappa
is unchanged.

## What was executed

The checker ranks the form, tests the pairing inequality, evaluates the four
rank pairs and adds the frame. It does not exhaust the 130,305 character
pairs.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the COPY consequence in PR 3755,
head `9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this floor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/copy-floor-arithmetic/verify.py
python3.12 -B research/copy-floor-arithmetic/test_verify.py
python3.12 -B scripts/research_package.py --package research/copy-floor-arithmetic
```

## Open next questions

This floor is the normalized rank-at-most-nine consequence. An unrestricted
higher-rank factor would leave it.

## Credit

conorholds derived the COPY floor from the one-coset budget. The orthogonal
frame is the rank-eight sharpness example in that argument.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
