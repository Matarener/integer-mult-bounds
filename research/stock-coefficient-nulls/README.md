# All fourteen recorded stock coefficients are null

**Partial. No new exponent.**

The selected bootstrap stock audit records seven stages on the native branch
and seven on the conservative branch. Every `actual_stock_coefficient` is
null, and the boundary field `actual_stage_stock_coefficients` is null. The
historical candidate `57604` remains in the candidate record and is not
written into any stage. Both recorded stage-1 headrooms are `6562783`.

## What was executed

The checker reads the receipt. It does not recompute the fourteen stages and
it does not adopt `57604`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the null-coefficient record
identified after PR 3742, head `89f6af270c550dd02bdb05d7a69987159aa110f2`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
these fields. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the stock audit.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/stock-coefficient-nulls/verify.py
python3.12 -B research/stock-coefficient-nulls/test_verify.py
python3.12 -B scripts/research_package.py --package research/stock-coefficient-nulls
```

## Open next questions

These fourteen fields are null. Adopting 57604 would leave that record.

## Credit

The selected stock audit records the null fields. petalas identified that
record as the remaining stock obligation.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
