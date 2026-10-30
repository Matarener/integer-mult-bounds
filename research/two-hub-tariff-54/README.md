# The two-hub tariff is 54

**Partial. No new exponent.**

There are 7 source rows and 14 reader rows, 21 in all. Each row has cost at
least 1, because the mark evaluates to 1 and therefore meets some query where
both factors are nonzero. Six reader premises force a second query. Their
query sets are `{d,x,y}`, `{d,z,w}` and `{g,t,x,y}`, once for each mark `E`
and `F`. Each mark lies in the span of its set, and in none of the individual
queries.

The row total is therefore at least

```text
15 · 1 + 6 · 2 = 27
```

and the measured charge, twice that total, is at least `2 · 27 = 54`. The
21-row baseline is `2 · 21 = 42`, so the excess is 12. The published nine
plane charges `4, 8, 12, 4, 10, 8, 0, 4, 4` sum to 54, so the bound is attained.

## What was executed

The checker solves the six premises over the rationals and adds the charges.
It does not enumerate factorizations.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the row model in PR 3698, head
`f8893fdfcb41a236ac085a92bca68ec6e5139cdc`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
tariff. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/two-hub-tariff-54/verify.py
python3.12 -B research/two-hub-tariff-54/test_verify.py
python3.12 -B scripts/research_package.py --package research/two-hub-tariff-54
```

## Open next questions

This tariff is the minimum. Enumerating factorizations would leave it.

## Credit

Nick Petalas published the two-hub tariff minimum and the witness charges.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
