# Rank-1 steps uniquely maximize the power-sum drop

**Partial. No new exponent.**

At the test saving `a = 1/596`, the power is `b = 595/596`. A rank-1 step
changes the sum by `1^b = 1`. For every rank `r` from 2 through 73, with
`x = r - 1` and `z = (x+1)/x`,

```text
z^595 < z^596
```

so one step at that rank changes the sum by strictly less than 1. Among
integer deletions of a fixed number of rank units, the rank-1 deletion is
the unique maximum of this drop.

When the forward power sum `V` is positive and the combined sum `U` is
strictly larger, the second-derivative bracket in the pair count `p` is
bounded below by

```text
U (16p + 16 a p + 2 + 16 a)
```

That quantity is positive for every integer `p ≥ 1`, both at `a = 1/596` and
at the selected kappa. The same bound holds at the neighboring pair counts
6, 7 and 8.

## What was executed

The checker proves those comparisons. It does not recompute the signed excess
enclosure.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the 425/426 comparison in
PR 3620, head `5a4354c669dc05a9368f58321b1951ebac36d80d`.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
order. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rank-unit-deletion-order/verify.py
python3.12 -B research/rank-unit-deletion-order/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank-unit-deletion-order
```

## Open next questions

This order and this bracket are the comparison. The signed excess enclosure
would leave them.

## Credit

Jose Manuel supplied the deletion comparison. Clear1nsight stated the
pair-count convexity in the caller-feasibility note. Nick Petalas supplied
the earlier all-pair budgets.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
