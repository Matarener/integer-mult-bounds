# One odd root pair has copy rank 7

**Partial. No new exponent.**

The two lines are the doubled roots `(2, 2, 0, 0, 0, 0, 0, 0)` and
`(1, 1, 1, 1, 1, 1, 1, 1)`. Their inner product is 1. On the other 118 lines,
the label pairing of this pair has rank 7. Putting either line back, or
pairing the first line with itself, raises that rank to 8.

Eight children of rank 7 have copy mass 56. Replacing the selected word's
eight rank-8 children by these eight, and lowering the centre charge from 64
to 56, gives the packing ceiling

```text
2069881607/1000000000000
```

The selected word's ceiling is `169005411/100000000000`. The ratio of those
high endpoints is `26201033/21393090`, which is above `21/20`.

This screen leaves out centre reads, phase frames and restoration. It is not
a supplied word, and it does not change the selected kappa.

## What was executed

The checker rebuilds the 120 lines, prices this one pair, and calls
`ceiling.ceiling` on the two profiles. It does not census the 1,260 frames.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the frame-pair note's cost-7
sentence.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this pair. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the frame-pair note and the ceiling
sources. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/odd-pair-block-rank/verify.py
python3.12 -B research/odd-pair-block-rank/test_verify.py
python3.12 -B scripts/research_package.py --package research/odd-pair-block-rank
```

## Open next questions

This pair's rank and the ideal eight-child screen are the identity. Building
the word would leave this rank.

## Credit

DreamingOfClouds supplied the B14 model in PR 717. The frame-pair note was
prepared with Claude Opus (Anthropic). Douglas Colkitt prepared the packing
ceiling with Claude (Anthropic).

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
