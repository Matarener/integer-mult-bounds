# The 360-replica profile changes sign across one unit of 10^-24

**Partial. No new exponent.**

The published profile

`{1:7990332, 2:2349000, 3:748971, 4:330480, 5:69479, 8:25920, 32:1, 48:137911}`

is charged `73` with weight `-896 * 360`. At

`86522418010381773087/50000000000000000000000`

its upper enclosure is negative. One unit of `10^-24` later its lower
enclosure is positive. Subtracting `10^-46` and `10^-70` from the lower
endpoint exceeds the published PR 3682 comparator by

`1841277597768621/62500000000000000000000`.

That endpoint stays above the selected kappa.

## What was executed

The checker encloses the signed profile with a finite logarithm series and
alternating exponentials. It does not replay the words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the price in PR 3734, head
`fa041037a3374eaa08feeca0b26a5d6893194147`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
profile. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/helper544-root-sign/verify.py
python3.12 -B research/helper544-root-sign/test_verify.py
python3.12 -B scripts/research_package.py --package research/helper544-root-sign
```

## Open next questions

This straddle and this gain are the price. A word replay would leave them.

## Credit

dataisfire priced the staged profile and the gain over PR 3682.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
