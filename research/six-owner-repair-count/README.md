# A repair block of six owners still needs 104 coordinates each

**Partial. No new exponent.**

The selected centre matrix has 112 ports and rank 8, so each owner has an
old-query kernel of dimension `112 - 8 = 104`. The eight pivot columns are
`0, 1, 2, 3, 4, 5, 6, 12`. Their complement has 104 ports.

The published column and route premises say that every pair of columns is
independent and that every ordered product of two distinct routes is unique.
Under those premises one active owner reaches at least three outputs. Each
of those outputs needs two further owners, and one pair of owners meets in
at most one output. The six further owners are therefore distinct, and the
whole support has size at least 7. No joint old and later kernel vector fits
in a block of size 1 through 6.

A repair of such a block must separate a kernel of dimension `104 * b`. The
104 complement reads attain that count. The six block totals are

```text
104, 208, 312, 416, 520, 624.
```

Seven is only the counting threshold. The selected kappa is unchanged.

## What was executed

The checker counts the complement and the owners. It does not enumerate the
12,432 route products.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the counting proof in merged PR
3071, package `research/centre-block-repair-information`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/six-owner-repair-count/verify.py
python3.12 -B research/six-owner-repair-count/test_verify.py
python3.12 -B scripts/research_package.py --package research/six-owner-repair-count
```

## Open next questions

This count is the six-owner bound. A route-product census would leave it.

## Credit

Ross Richardson proved the six-owner information bound. The rank and route
premises are the finite checks recorded with that proof.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
