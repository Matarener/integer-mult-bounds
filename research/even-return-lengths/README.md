# Every even length from 4 through 18 meets the positive splits

**Partial. No new exponent.**

A one-bit step flips Hamming-weight parity, so every return has even length.
The ten admitted length-22 splits with a positive revisit count are
`(11,10)`, `(11,9)`, `(10,10)`, `(11,8)`, `(10,9)`, `(11,7)`, `(10,8)`,
`(9,9)`, `(11,6)` and `(10,7)`.

For each of those splits, explicit restored words of length 22 have return
lengths covering 4, 6, 8, 10, 12, 14, 16 and 18. Together with the length-2
witnesses, every even length from 2 through 22 occurs. The witnesses are not
universal words.

## What was executed

The checker replays the thirty-one words and the eleven-split domain filter.
It does not enumerate seven-label words and it does not claim `f(7)`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the intermediate-length question
in PR 3726, head `4d31b64628d3488baf70e73a8478648f5a16ab3f`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
cover. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/even-return-lengths/verify.py
python3.12 -B research/even-return-lengths/test_verify.py
python3.12 -B scripts/research_package.py --package research/even-return-lengths
```

## Open next questions

These eight lengths meet every positive count. A word census would leave them.

## Credit

petalas asked which return lengths can realize the forced revisit counts.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
