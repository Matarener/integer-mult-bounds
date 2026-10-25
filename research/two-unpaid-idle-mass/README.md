# Two unpaid coordinates leave a fractional idle mass on one call

**Partial. No new exponent.**

The selected local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. Its
paid mass is 5586. With `m = 73`, width `896/9`, and centre 64, the covered
mass of one call with `unpaid` coordinates is `(73 - unpaid) * 896/9 + 64`.

One unpaid coordinate leaves idle mass 1646. Two unpaid coordinates leave
`13918/9`, which is not an integer, so one call has no integer idle histogram.
Nine calls, one replica, leave idle mass 13918. Under the rank cap 51, which
satisfies `2 * 51^2 < 73^2`, that mass is `272 * 51 + 46`. One hundred forty-four
calls leave `222688 = 4366 * 51 + 22`.

The selected kappa is unchanged. This is the coverage identity for a stated
coordinate count, not a realised packing.

## What was executed

The checker computes these three masses from the selected invoices. It does
not search a packing.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the two-unpaid accounting contrast
in PR 3754, head `4bde35c0200e83fe27a08ec408a2ae59b490a03f`.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this mass.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the two invoices.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/two-unpaid-idle-mass/verify.py
python3.12 -B research/two-unpaid-idle-mass/test_verify.py
python3.12 -B scripts/research_package.py --package research/two-unpaid-idle-mass
```

## Open next questions

This mass is the accounting contrast. A realised two-unpaid word would leave it.

## Credit

Nick Petalas priced this two-unpaid mass.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
