# The T488 composition moment changes sign across one unit of 10^-24

**Partial. No new exponent.**

The published paid profile

`{1:10817496, 2:3179808, 3:1024434, 4:447984, 5:94794, 8:35136, 48:186782}`

has rank mass `31762944 = 65088 * 488`. It uses `4392 = 488 * 9` calls,
`437248 = 896 * 488` live families and `1791936 = 4392 * 408` roles. Its
moment is the paid power sum minus `437248 * 73^(1-a)`.

At `a = 0.001730418899766071163804` the moment is negative. One unit of
`10^-24` later it is positive. The sign agrees at 80 digits and at 160
digits. Subtracting `10^-46` and `10^-70` from the lower endpoint produces
the 70-digit released string. That released value stays strictly above the
selected kappa.

## What was executed

The checker evaluates the two endpoints and formats the released fraction.
It does not replay the word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the composition arithmetic in
PR 3740, head `535b3fc6a4100199ef4d8c96bede421a8d79efee`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
straddle. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/t488-moment-straddle/verify.py
python3.12 -B research/t488-moment-straddle/test_verify.py
python3.12 -B scripts/research_package.py --package research/t488-moment-straddle
```

## Open next questions

This straddle and this released string are the arithmetic. A word replay
would leave them.

## Credit

petalas audited the composition moment and the released string.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
