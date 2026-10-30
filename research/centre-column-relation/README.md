# The centre columns cancel

**Partial. No new exponent.**

The published ports `(0, 6, 85)` have columns

```text
(1, 1, 1, 1, 0, 0, 0, 0)
(0, 1, 1, 0, 1, 0, 0, 1)
(1, 0, 0, 1, -1, 0, 0, -1)
```

Their integer combination is zero:

```text
R_0 - R_6 - R_85 = 0
```

The ambient dimension is 112 and the observation rank is 8, so the per-owner
factor is `112 - 8 = 104`. The even subgroup has the order of `SL(2,16)`,

```text
16 · 15 · 17 = 4080
```

and the full subgroup has order `2 · 4080 = 8160`. The block therefore has

```text
104 · 4080 = 424320
```

coordinates, and the common kernel saves 1 of them. The published census
splits 896 dependent triples into 56 of order 4080 and 840 larger ones,
since `56 + 840 = 896`. With the published 15-owner floor, the support lies
in `[15, 4080]`.

## What was executed

The checker subtracts the three columns and multiplies these counts. It does
not enumerate the 4,080 owners.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the column list in PR 3656, head
`69e745992b966c647e10696b980cb4c96d7ebeed`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to these
columns. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/centre-column-relation/verify.py
python3.12 -B research/centre-column-relation/test_verify.py
python3.12 -B scripts/research_package.py --package research/centre-column-relation
```

## Open next questions

This column relation is the witness. Enumerating the coset would leave it.

## Credit

Matarener published the 4,080-owner coset certificate and these three columns.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
