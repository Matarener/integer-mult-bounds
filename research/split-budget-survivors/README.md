# Five length-20 weight splits survive the budget tests

**Partial. No new exponent.**

At length 20 each weight class has size at most 10. There are 66 unordered
pairs of those sizes. A universal set in dimension 7 needs at least 64 cross
pairs and a nonnegative even budget

```text
B0 = C(s, 2) + C(t, 2) - 63
```

The pair identity also needs `B0 + a*b >= ceil((s*t - 64) / 2)` for some
nonnegative `a, b` with `a + b <= B0`. The largest such product is
`floor(B0 / 2) * ceil(B0 / 2)`.

Six splits pass the count tests: `(10,10)`, `(10,9)`, `(10,8)`, `(9,9)`,
`(10,7)` and `(9,8)`. The last has `B0 = 1` and need 4. Every admissible
product `a*b` is 0, so `B0 + a*b <= 1`. It drops out. The other five survive.
At length 18 the same tests leave only `(9,9)`, among 55 splits with parts at
most 9.

The selected kappa is unchanged. This check does not decide `f(7)`.

## What was executed

The checker classifies every split. It does not run a seven-label census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the split list in PR 2973, head
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
list. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/split-budget-survivors/verify.py
python3.12 -B research/split-budget-survivors/test_verify.py
python3.12 -B scripts/research_package.py --package research/split-budget-survivors
```

## Open next questions

The 66 and 55 splits are finite. A seven-label census would leave this package.

## Credit

Nicholas Stone listed these representatives in the collision-budget note of PR
2973. This package classifies the splits.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
