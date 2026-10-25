# The selected saving lies below the ceiling bracket

**Partial. No new exponent.**

The published search bracket is

```text
52814190909/31250000000000 < a < 1690054109089/1000000000000000.
```

Its width is exactly `1/10^15`. The selected saving is `kappa / (1 - kappa)`,
which equals

```text
836330098538459/499163669901461541.
```

That rational is strictly smaller than the lower endpoint, so it lies outside
the bracket.

## What was executed

The checker subtracts the endpoints. It does not evaluate the exponential and
it does not time the search.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the bracket in PR 3662, head
`aa6f513720ad8de12d678f24f90ea17576e31d52`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
bracket. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/ceiling-bracket-gap/verify.py
python3.12 -B research/ceiling-bracket-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/ceiling-bracket-gap
```

## Open next questions

This comparison is the bracket. Evaluating the exponential would leave it.

## Credit

hevlyo published the ceiling bracket.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
