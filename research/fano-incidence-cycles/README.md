# The Fano incidence graph has 28 six-cycles

**Partial. No new exponent.**

The seven Fano lines are the cyclic shifts of `{0, 1, 3}`. Every pair of the
seven points lies on exactly one line, and every pair of lines meets in
exactly one point. The point-line graph therefore has 14 vertices, each of
degree 3, and it contains no 4-cycle.

That graph has 28 six-cycles. Each of the 14 vertices lies on 12 of them.
The same per-vertex count is `3(3 - 1)^2 = 12`. A degree-3 braid cap of one
six-cycle per vertex excludes this graph, while a cap of 12 meets the count
at every vertex. The selected kappa is unchanged.

## What was executed

The checker builds the seven lines and enumerates the cycles. It does not
replay the centre window.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the Fano control in PR 3147,
head `5cbc48b18cb05327a8dacab3f626412d3bc5e924`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fano-incidence-cycles/verify.py
python3.12 -B research/fano-incidence-cycles/test_verify.py
python3.12 -B scripts/research_package.py --package research/fano-incidence-cycles
```

## Open next questions

This count is the Fano incidence graph. A centre-window replay would leave it.

## Credit

The braid note cites this Fano partition as the configuration admitted when
the degree-3 six-cycle cap is relaxed from 1 to 12.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
