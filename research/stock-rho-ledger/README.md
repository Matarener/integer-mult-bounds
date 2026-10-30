# The row-ledger terms do not settle rho

**Partial. No new exponent.**

The published family charges are

```text
9909 = 367 · 27
252 = 9 · 28
1024 = 2 · 512
```

With the published bit length `B = 2642`, the selected ledger is

```text
2 · 2642 + 9909 + 252 + 1024 = 16469
```

The three external terms sum to `9909 + 252 + 1024 = 11185`. The retained
degree gap is

```text
10^6 - (51/25) · 20161 = 23971789/25
```

The BIT row stacks the same charges on its own factor:

```text
2 · (64² + 1) = 8194
8194 + 9909 + 252 = 18355
```

The two displayed stage-1 caps are `4362.14` and `12556.14`. They differ by
exactly 8194. Their guards are `ceil(log2(8 · sigma))`, equal to 16 and 17,
and both caps sit below the stage-1 guard `6,562,783`.

## What was executed

The checker multiplies these terms. It does not choose between `rho = 0` and
`rho = 8194`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ledger in PR 3667, head
`671757dfe548948e5a69e63058b98233b6a8f283`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
these products. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/stock-rho-ledger/verify.py
python3.12 -B research/stock-rho-ledger/test_verify.py
python3.12 -B scripts/research_package.py --package research/stock-rho-ledger
```

## Open next questions

These products are the ledger. Choosing a reading would leave them.

## Credit

Mainzu published the row-ledger comparison. Aaron Wang stated the unbound
`rho` term, and Wentao Li proved `A = 0`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
