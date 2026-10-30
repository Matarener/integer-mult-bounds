# Every orthogonal core has the same section histogram

**Partial. No new exponent.**

There are 3780 orthogonal pairs among the 120 canonical E8 lines. Each
common core has 24 roots and binary rank 7. Its 127 nonzero coordinate
masks meet that core in sections whose sizes are

`{0: 1, 8: 15, 12: 96, 16: 15}`.

Those four counts sum to 127. The same histogram occurs for every pair, so
the aggregate is

`{0: 3780, 8: 56700, 12: 362880, 16: 56700}`.

The selected kappa is unchanged.

## What was executed

The checker counts these sections. It does not infer an invoice floor.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the core-section histogram in
PR 3689, head `3193d1ea9a4fc5d178570a61e6019454b53c1db9`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the root geometry.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/core-section-capacity/verify.py
python3.12 -B research/core-section-capacity/test_verify.py
python3.12 -B scripts/research_package.py --package research/core-section-capacity
```

## Open next questions

This histogram is the capacity. An invoice floor would leave it.

## Credit

conorholds recorded this section histogram. The root geometry names Nick Petalas.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
