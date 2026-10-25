# Nonframe roots have three covers and frame roots have 945

**Partial. No new exponent.**

The 120 canonical E8 lines split into 112 nonframe roots and 8 frame roots.
Across the 3780 orthogonal pairs, every common core has 24 roots and binary
rank 7. Each accepted cover splits the live support into parts of ranks 7, 6
and 4. A nonframe root meets the five-site floor, and a frame root meets the
eight-site floor.

Every one of the 112 nonframe roots has exactly 3 such covers, so there are
336 five-site covers. Every one of the 8 frame roots has exactly 945, so
there are 7560 eight-site covers. The selected kappa is unchanged.

## What was executed

The checker enumerates these pairs. It does not infer an invoice floor.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the uniform cover count in
PR 3689, head `3193d1ea9a4fc5d178570a61e6019454b53c1db9`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
these counts. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the root geometry.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/uniform-cover-counts/verify.py
python3.12 -B research/uniform-cover-counts/test_verify.py
python3.12 -B scripts/research_package.py --package research/uniform-cover-counts
```

## Open next questions

These counts are the census. An invoice floor would leave it.

## Credit

conorholds counted these covers. The root geometry names Nick Petalas.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
