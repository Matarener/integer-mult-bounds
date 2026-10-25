# A 7-dimensional subspace of `F_2^9` lies in exactly 3 hyperplanes

**Partial. No new exponent.**

A 7-dimensional subspace of a 9-dimensional space over `F_2` has a
2-dimensional annihilator. That annihilator has four vectors, so the subspace
lies in three hyperplanes, one for each nonzero normal.

There are 43,435 such subspaces. The Gaussian count is

```text
(2^9 - 1)(2^9 - 2) / ((2^2 - 1)(2^2 - 2)) = 43435
```

Every one of them has a 128-point orthogonal and an annihilator of size 4.
Each of the 511 hyperplanes contains 255 of the subspaces, and

```text
43435 * 3 = 511 * 255
```

The selected kappa is unchanged.

## What was executed

The checker enumerates the subspaces and their annihilators. It does not rerun
the fresh-extraction search.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the three-hyperplane sentence of
PR 2979, head `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rank7-hyperplane-count/verify.py
python3.12 -B research/rank7-hyperplane-count/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-hyperplane-count
```

## Open next questions

The subspace count and the three-hyperplane incidence are exhaustive. A
fresh-extraction search would leave this package.

## Credit

mdumitrean used this count for the fresh rank-7 route in PR 2979. This package
enumerates the subspaces and the hyperplanes.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
