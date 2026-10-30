# Every one-coset family has deficiency sum at most 9

**Partial. No new exponent.**

The 120 root lines are the 36 pair roots and the 84 triple roots in nine
coordinates. Their binary labels pair by the same rule as one plus the
integer root product. Coordinate permutation reduces the nonzero characters
to nine weights and the ordered character pairs to 220 four-count profiles.
Deleting the zero and equal profiles leaves 192. Exactly 100 of those are
forbidden: the overlap block has odd length, or both weights are even and
their half-weights have the same parity.

Each of the nine weight representatives meets the roots it marks in a set of
scalar rank 8. Each of the 100 forbidden profiles does the same on the
intersection. A compatible pair is one whose intersection has rank at most 7,
so none of these forbidden profiles is compatible. The contrapositive is the
pairing rule used by the budget: compatible characters are orthogonal, and
two compatible even-weight characters have different half-weight parities.
An odd-weight character is not isotropic, so it drops out of a linear
relation. At most two even-weight characters can then remain, and those two
are independent. Support annihilators of distinct normalized vectors in one
outside coset therefore form a direct sum in the nine-bit label space, and
the sum of their deficiencies is at most 9.

Nine explicit vectors attain the sum. On column `j`, the value is the integer
root row in that column, shifted by `-2` on every triple root. Its support
has label rank 8, so each deficiency is 1. The nine supports are distinct.
The selected kappa is unchanged.

## What was executed

The checker builds the roots, ranks the nine orbits and the 100 profiles, and
adds the nine deficiencies. It does not exhaust the 130,305 character pairs.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the one-coset budget in PR 3755,
head `9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
budget. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

Overlap search on 2026-10-18 covered 494 open pull requests and 2,509
discussions. The matches are earlier uses of this card. This package changes
the question to the orbit reduction of the one-coset sum.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/one-coset-orbit-budget/verify.py
python3.12 -B research/one-coset-orbit-budget/test_verify.py
python3.12 -B scripts/research_package.py --package research/one-coset-orbit-budget
```

## Open next questions

This budget is the one-coset sum. An unrestricted higher-rank factor would
leave it.

## Credit

conorholds stated the uniform deficiency budget and the orbit reduction.
CubeJerry certified an earlier full-rank premise, and mightyOil supplied the
compatible-edge independence argument.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
