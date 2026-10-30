# The rank floor removes three ten-call split families

**Partial. No new exponent.**

The inherited pair and parity conditions at ten calls and four targets admit
splits that the block rank floor `n_g >= t_g` removes. Shape `(4,0)` loses
`(0,10)` and `(2,8)`. Shape `(0,4)` loses `(8,2)` and `(10,0)`. Shape `(3,1)`
loses `(1,9)`, and shape `(1,3)` loses `(9,1)`. The balanced shape `(2,2)`
keeps `(2,8)`, `(4,6)`, `(6,4)` and `(8,2)`.

An explicit rank fixture realizes the balanced `(2,8)` boundary: both blocks
have rank 2, and each product has rank 2. The fixture is rank data. It is not
a word, and the floor does not remove that split.

## What was executed

The checker enumerates the five shapes at ten calls and ranks the fixture.
It does not search for a word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the rank floor in PR 3736, head
`6258d5e340e21594edec5a6672fdec8977a37608`.

## Scope and evidence

Original card: `bit-new-register-model`, priority revision 6, refined to these
splits. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/q8-rank-floor/verify.py
python3.12 -B research/q8-rank-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/q8-rank-floor
```

## Open next questions

These removals are the floor at ten calls. A word search would leave them.

## Credit

petalas derived the block rank floor and the balanced fixture.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
