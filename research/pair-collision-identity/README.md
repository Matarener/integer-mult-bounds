# Cross-pair collisions equal twice the within-class products

**Partial. No new exponent.**

Split a set `P` in `F_2^4` by a nonzero linear functional. Let `A_x` be the
number of unordered pairs inside the zero class with XOR `x`, and let `B_x`
be the same count inside the other class. Let `r_y` be the number of pairs
with one point from each class and XOR `y`. Then

```text
sum_y C(r_y, 2) = 2 * sum_x A_x B_x
```

Each within-class pair of pairs that share a sum produces two cross-pair
collisions. The identity holds for every one of the 65,536 subsets and every
one of the 15 nonzero functionals: 983,040 checks. The selected kappa is
unchanged. This check does not decide `f(7)`.

## What was executed

The checker evaluates the two sides on every subset and functional. It does
not run a seven-label census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the pair identity in PR 2973,
head `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
identity. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/pair-collision-identity/verify.py
python3.12 -B research/pair-collision-identity/test_verify.py
python3.12 -B scripts/research_package.py --package research/pair-collision-identity
```

## Open next questions

The 983,040 checks are finite. A seven-label census would leave this package.

## Credit

Nicholas Stone stated this identity in the collision-budget note of PR 2973.
This package checks it on every subset of `F_2^4`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
