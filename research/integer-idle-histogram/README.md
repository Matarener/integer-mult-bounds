# The integer idle optimum is 32 children of rank 51 and one of rank 14

**Partial. No new exponent.**

The selected complex profile pays `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`
on each call. The coverage law leaves an idle mass of 1646. Under the halving
guard the largest idle rank is 51. The minimum-cost integer histogram of that
mass, at both ends of the bracket

`1688603446526/10^15` and `1688603446527/10^15`,

is 32 children of rank 51 and one child of rank 14. The lower endpoint has
certified moment strictly below 1, and the upper endpoint has certified moment
strictly above 1. The selected saving sits strictly below the lower endpoint.

## What was executed

The checker reads the pinned profile and runs the mass recurrence at those
two endpoints. It does not search another rank cap.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the integer histogram in PR 3729,
head `c7c68f89e020f9e62f38514afdfc99dda01430d4`.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this
histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the assembly, and the
independent profile. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/integer-idle-histogram/verify.py
python3.12 -B research/integer-idle-histogram/test_verify.py
python3.12 -B scripts/research_package.py --package research/integer-idle-histogram
```

## Open next questions

This histogram and these two endpoints are the integer ceiling. A finer grid
would leave them.

## Credit

Douglas Colkitt wrote the outward-rounded child-cost enclosures. petalas
recovered the integer histogram.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
