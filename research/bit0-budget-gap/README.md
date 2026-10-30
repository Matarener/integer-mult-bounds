# An unbalanced 20-point split has even budget `27 + d^2`

**Partial. No new exponent.**

In dimension 7 a universal 20-point set needs 64 odd masks. Split the points
into classes of sizes `10 + d` and `10 - d`, with `d` from 0 through 10. The
two classes determine

```text
C(10+d, 2) + C(10-d, 2) = 90 + d^2
```

within-class pairs, so the even collision budget is `27 + d^2` after removing
the 63 nonzero even masks. The balanced budget 27 is the case `d = 0`. Every
positive deviation has `d^2` more room.

The cross pairs number `100 - d^2`. Covering 64 odd masks requires
`100 - d^2 >= 64`, hence `d <= 6`. The four deviations `d = 7, 8, 9, 10` have
only 51, 36, 19 and 0 cross pairs, so none of those splits can be universal.
The selected kappa is unchanged. This check does not decide `f(7)`.

## What was executed

The checker evaluates the binomial identities for every deviation. It does not
run a seven-label census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the bit-0 budget paragraph of PR
2973, head `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
formula. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/bit0-budget-gap/verify.py
python3.12 -B research/bit0-budget-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/bit0-budget-gap
```

## Open next questions

The eleven deviations and the four odd-mask obstructions are finite. A
seven-label census would leave this package.

## Credit

Nicholas Stone stated the budget `27 + d^2` in the collision-budget note of PR
2973. This package checks that formula and the odd-mask cutoff.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
