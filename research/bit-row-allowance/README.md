# The nine-stage BIT row is 18355

**Partial. No new exponent.**

The nine-stage assembler asserts

`row = DEPTH * (m * m + 1) + 9909 + 252`

and `row == 18355`, with `row < 20161`. The parent note records the allowance
`2 * (64^2 + 1) = 8194`. The gauge pairs `(367, 27)` and `(9, 28)` give
`9909` and `252`. Their sum is

`8194 + 9909 + 252 = 18355`,

which is below the cap 20161. The selected kappa is unchanged.

## What was executed

The checker adds these published terms. It does not recompute the fourteen
stage headrooms.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the BIT-row comparison in PR 3667,
head `ad7c0e10e5476136498b377a3a28b80640e55c08`.

## Scope and evidence

Original card: `bit-new-register-model`, priority revision 6, refined to this
row. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the nine-stage assembler, the parent note
and the gauge pairs. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/bit-row-allowance/verify.py
python3.12 -B research/bit-row-allowance/test_verify.py
python3.12 -B scripts/research_package.py --package research/bit-row-allowance
```

## Open next questions

This row is the allowance. A stage-headroom replay would leave it.

## Credit

Mainzu compared this BIT row with the cap. The nine-stage assembler names
DreamingOfClouds.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
