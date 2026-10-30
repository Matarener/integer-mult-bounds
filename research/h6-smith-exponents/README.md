# The H6 repair rank is 560

**Partial. No new exponent.**

The published localized Smith factors of the 30,960-port complement are

```text
1 repeated 30400 times,
11 repeated 336 times,
209 = 11·19 repeated 208 times,
4807 = 11·19·23 repeated 16 times.
```

The checker confirms `11·19 = 209` and `11·19·23 = 4807`. The non-unit
factors number

```text
336 + 208 + 16 = 560
```

and the port count is `30400 + 560 = 30960`. Their product is

```text
11^560 · 19^224 · 23^16
```

because the exponent of 19 is `208 + 16 = 224` and the exponent of 23 is 16.
A dyadic repair therefore has rank at least 560.

## What was executed

The checker multiplies these factors. It does not rebuild the 30,960-square
matrix and it does not list the 560 physical rows.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the factor list in PR 3655, head
`7bf23e128e58a33c019268f57129629f603547f7`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to these
exponents. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/h6-smith-exponents/verify.py
python3.12 -B research/h6-smith-exponents/test_verify.py
python3.12 -B scripts/research_package.py --package research/h6-smith-exponents
```

## Open next questions

These exponents are the identity. Rebuilding the matrix would leave them.

## Credit

Ross Richardson published the H6 Smith factors and the 560-row repair.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
