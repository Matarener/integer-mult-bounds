# Three degree budgets stay positive

**Partial. No new exponent.**

The frozen assembler writes the selected degree gap as
`10^6 - (51/25) * 20161`. That value is `23971789/25`, and the stored
assembly field `outer.row_product_gap` is the same fraction. It is positive,
so degree `10^6` still clears the cap 20161 at coefficient `51/25`.

The three-stage note carries `58344 + 9909 + 252 = 68505` and prints
`160000 - (51/25) * 68505 = 20249.8`. That decimal is the fraction
`506245/25`. The paired-cube note carries `10284 + 9909 + 252 = 20445` and
prints `70000 - (51/25) * 20445 = 141461/5`. Both gaps are positive. The
selected kappa is unchanged.

## What was executed

The checker evaluates these three formulas. It does not recompute the
fourteen stage headrooms.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json` during this replay,
because the stored gap is read from that file. The orientation used here is
the degree-gap comparison in PR 3667, head
`ad7c0e10e5476136498b377a3a28b80640e55c08`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
these three gaps. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the assembly, the two notes and the frozen
assembler. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/degree-gap-clearance/verify.py
python3.12 -B research/degree-gap-clearance/test_verify.py
python3.12 -B scripts/research_package.py --package research/degree-gap-clearance
```

## Open next questions

These three gaps are the comparison. A stage-headroom replay would leave it.

## Credit

Mainzu compared the selected degree gap with these reserves.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
