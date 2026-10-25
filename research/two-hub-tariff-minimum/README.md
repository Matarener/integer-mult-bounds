# The two-hub literal actual-reader minimum is 54

**Partial. No new exponent.**

The retained model has nine queries, two marks, and 21 premises: four source
rows on the first mark, three on the second, and seven reader rows on each.
Every source row pays one unit, because the default readers `ghx` and `ghy`
carry their own mark and miss the other. Each reader row pays the smallest
number of mark-bearing queries in a support that still spans its mark. Six
reader premises, `dxy`, `dzw`, and `gtxy` on each mark, pay two. The other
eight reader rows pay one. The row-unit total is `7 + 20 = 27`, so the charge
is `2 * 27 = 54`.

The retained witness has the nine plane charges `4, 8, 12, 4, 10, 8, 0, 4, 4`,
which also sum to 54. The baseline of 42 is one unit on each of the 21 rows,
doubled. The excess is 12.

## What was executed

The checker enumerates the admissible supports of these 21 premises and prices
the retained witness. It does not search another reader model. The model files
are the retained `CONFIG.json` and `WITNESS.json` from PR 3583, commit
`f9db162a408ba978c10b00be265f5ffca321957c`. They are not on canonical main, so
this package carries those bytes and checks their hashes.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the two-hub tariff in PR 3698,
head `f8893fdfcb41a236ac085a92bca68ec6e5139cdc`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
model. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/two-hub-tariff-minimum/verify.py
python3.12 -B research/two-hub-tariff-minimum/test_verify.py
python3.12 -B scripts/research_package.py --package research/two-hub-tariff-minimum
```

## Open next questions

This minimum is the tariff in the stated model. Another reader model would leave it.

## Credit

Nick Petalas stated the minimum in PR 3698. The retained model is from PR 3583,
which credits Philippe Van Velzen and ctoth.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
