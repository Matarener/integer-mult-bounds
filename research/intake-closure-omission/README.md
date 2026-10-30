# Twenty-four intake rows omit closure

**Partial. No new exponent.**

The published family order carries `closure`, `review_completion` and
`verification_evidence` when a later row omits them. In the committed intake,
every row still has `review_completion` and `verification_evidence`. Exactly
24 of the 564 intake rows omit `closure`.

Four of those rows inherit an explicit null from an earlier family decision.
The ledger keeps that null. They are 1365, 1494, 2361 and 2832. One new row,
2963, has no earlier closure and records null in the ledger. The other 19 new
rows omit the field in both the intake row and the ledger: 2985, 3012, 3029,
3031, 3039, 3040, 3045, 3049, 3074, 3120, 3143, 3147, 3154, 3181, 3184, 3190,
3198, 3200 and 3251.

## What was executed

The checker walks the 47 family files in the published order and partitions
these rows. It does not rewrite the ledger or the family files.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the optional-field carry in PR
3686, head `932f3b1ef707733643b5e318c4bf134436ddd766`.

## Scope and evidence

Original card: `overlap-receipt`, priority revision 6, refined to this
partition. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the ledger and the
family files. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/intake-closure-omission/verify.py
python3.12 -B research/intake-closure-omission/test_verify.py
python3.12 -B scripts/research_package.py --package research/intake-closure-omission
```

## Open next questions

This partition is the count. A checker rewrite would leave it.

## Credit

roger-sato recorded the omitted-closure split and the family carry.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
