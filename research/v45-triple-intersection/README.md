# The V45 frame is the intersection of three hyperplanes

**Partial. No new exponent.**

The normals `7`, `42` and `45` satisfy

```text
7 xor 42 = 45
```

so the third hyperplane is the sum of the first two. Their common intersection
in `F_2^9` therefore has dimension 7 and contains 128 vectors.

The seven generators

```text
256, 128, 64, 35, 16, 11, 5
```

all lie in that intersection, and they span every one of its 128 vectors. The
selected kappa is unchanged.

## What was executed

The checker builds the span and the intersection. It does not rerun the
fresh-extraction search.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the V45 frame in PR 2979, head
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
frame. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/v45-triple-intersection/verify.py
python3.12 -B research/v45-triple-intersection/test_verify.py
python3.12 -B scripts/research_package.py --package research/v45-triple-intersection
```

## Open next questions

The named frame and the normal relation are finite. A fresh-extraction search
would leave this package.

## Credit

mdumitrean named this frame in PR 2979. This package compares the generators
with the intersection.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
