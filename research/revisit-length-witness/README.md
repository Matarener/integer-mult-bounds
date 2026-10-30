# Length 2 meets every positive length-22 split

**Partial. No new exponent.**

A one-bit step flips Hamming-weight parity, so a return to an earlier prefix
state has even length. The ten admitted length-22 splits with a positive
revisit count are `(11,10)`, `(11,9)`, `(10,10)`, `(11,8)`, `(10,9)`,
`(11,7)`, `(10,8)`, `(9,9)`, `(11,6)` and `(10,7)`. Their revisit counts are
`22 - (s+t)`, from 1 through 5.

Each split has an explicit restored word of length 22. The word is a Gray
cycle, expanded by disjoint detours, with repeated-label spikes. Its prefix
set has the split's two class sizes, and the distances between equal prefix
states are exactly 2, 20 and 22. The witnesses are not universal words, and
they are not a census.

## What was executed

The checker rebuilds the ten words and the eleven-split domain filter. It
does not enumerate seven-label words and it does not claim `f(7)`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the revisit question in PR 3708,
head `44334c60341e4354378666838c7921e6cabd6c03`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to these
witnesses. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/revisit-length-witness/verify.py
python3.12 -B research/revisit-length-witness/test_verify.py
python3.12 -B scripts/research_package.py --package research/revisit-length-witness
```

## Open next questions

Which even lengths from 4 through 18 also occur as returns for every positive
length-22 split?

## Credit

petalas asked which return lengths can realize the forced revisit counts.
Ross Richardson recorded the prefix-walk model used by those counts.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
