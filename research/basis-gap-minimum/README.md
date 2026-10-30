# One changed basis lifts the five-cell minimum from 15 to 17

**Partial. No new exponent.**

The query has five cells and four blocks, of dimensions 1, 1, 1, and 4. The
first three blocks have one basis and the fourth has three. The VVV floor is
`1 + 1 + 1 + 4 * 3 = 15`. The MMM floor is `2 + 2 + 2 + 4 * 3 = 18`.

The two fixtures use the same cells. Only the bases of the four-dimensional
block differ. Over the 243 sign assignments, the coordinate basis attains 15
once. The changed basis never attains 15, and its minimum is 17. Both bases
attain the MMM floor 18. The selected kappa is unchanged.

## What was executed

The checker prices these two bases. It does not enumerate the other fixtures.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the basis gap in PR 3596, head
`d92d37b6b875cc2c4d73606a3df8298c44e7d54c`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
pair. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/basis-gap-minimum/verify.py
python3.12 -B research/basis-gap-minimum/test_verify.py
python3.12 -B scripts/research_package.py --package research/basis-gap-minimum
```

## Open next questions

This pair is the basis comparison. Another fixture would leave it.

## Credit

Nick Petalas separated these two bases.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
