# The non-Fano assignment costs at least 32

**Partial. No new exponent.**

Each reader tariff is at least its dimension minus the source codimension. The
displayed assignment has one reader of dimension at least 8, four of dimension
6, and one more of dimension 6, with codimension at most 1. The invoice is
therefore at least

```text
(8 - 1) + 4 · (6 - 1) + (6 - 1) = 32.
```

Five ordinary targets cost 30, and the residual-bearing baseline is 31. Both
are below 32. When five distinct roles make every source the full 9-dimensional
space, the same readers give `9 + 4 · 6 + 6 = 39`.

If `k` of the four middle targets are J axes, with `1 <= k <= 3`, the baseline
before a residual line is `B0 = 30 - 3k`. One shared ordinary role costs at
least `B0 + 6`. Two or more ordinary roles cost at least `B0 + k`. A residual
raises the baseline by at most 1. The one-role floor stays strictly above that,
and the two-role floor meets it only at `k = 1`, which is a tie rather than a
saving.

The published annihilator counts `395 + 107 + 8 + 1` equal `2^9 - 1`. The
18 role dimensions and the 612 ordered triad choices add as stated.

## What was executed

The checker adds these floors. It does not sweep coefficients and it does not
reclassify the annihilators.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the invoice in PR 3685, head
`7b55935a33b50d05858095dee93c669eadd122e8`.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to this
floor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/nonfano-invoice-floor/verify.py
python3.12 -B research/nonfano-invoice-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/nonfano-invoice-floor
```

## Open next questions

This floor is the comparison. A coefficient sweep would leave it.

## Credit

flyingviper published the non-Fano invoice exclusion.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
