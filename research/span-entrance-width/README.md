# The staged entrance has width 7

**Partial. No new exponent.**

Helpers 644 and 660 both start at the entrance `(429, 30)` and finish at the
dyadic frame

```text
(256, 128, 64, 32, 16, 8, 4, 2, 1).
```

That frame is `2^8` down to `2^0`, and its sum is `2^9 - 1 = 511`. Each climb
rank is the increase in the number of blocks. Helper 644 grows by
`(2, 1, 2, 1, 1)` and helper 660 grows by `(2, 2, 1, 1, 1)`. Both totals are
`9 - 2 = 7`.

The parent entrance is the one-block frame `(30)`. Its ranks are
`(3, 1, 2, 1, 1)` and `(3, 2, 1, 1, 1)`, each totaling `9 - 1 = 8`. Only the
first rank changes, from 3 to 2. The serialized recipe count moves from 56 to
57. The same two chains appear in both orientations and both providers.

## What was executed

The checker follows these frames. It does not replay the 512 Gaussian columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the entrance audit in PR 3713,
head `49bd08ec57d0d2345b0efa1a651fa862b9a41b15`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
width. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/span-entrance-width/verify.py
python3.12 -B research/span-entrance-width/test_verify.py
python3.12 -B scripts/research_package.py --package research/span-entrance-width
```

## Open next questions

This width is the comparison. Replaying the columns would leave it.

## Credit

Mainzu published the separate-kernel entrance audit. The staged words come from
Ross Richardson's PR 3605, and the kernel used for that audit is Sagar Thakrar's.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
