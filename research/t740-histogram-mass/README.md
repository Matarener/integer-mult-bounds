# The T740 histogram sits above the selected kappa

**Partial. No new exponent.**

The published histogram is

```text
{1:16417896, 2:4835160, 3:1540174, 4:679321, 5:143992, 6:3, 8:53280, 48:283185}
```

It has 23,953,011 children and rank mass 48,165,120. The stated schedule is
740 replicas, `740 · 9 = 6,660` calls, and `6,660 · 408 = 2,717,280` helper
roles.

The conditional root is

```text
0.001730006549538841847005 - 10^(-46) - 10^(-70)
```

That value is greater than `0.00173` and greater than the selected kappa
`836330098538459/500000000000000000`.

## What was executed

The checker adds the published counts and compares the two rationals. It does
not run the fresh-bootstrap wrapper.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the histogram in PR 3605, head
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/t740-histogram-mass/verify.py
python3.12 -B research/t740-histogram-mass/test_verify.py
python3.12 -B scripts/research_package.py --package research/t740-histogram-mass
```

## Open next questions

This histogram and this root comparison are the ledger. The wrapper replay
would leave them.

## Credit

Ross Richardson published the conditional T740 release and its histogram.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
