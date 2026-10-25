# Four rank-7 frames are lines in one 3-dimensional space

**Partial. No new exponent.**

Each of these generator lists spans 128 vectors in `F_2^9`:

```text
A    256, 128, 64, 38, 20, 10, 1
B    256, 128, 64, 34, 17, 11, 4
C    256, 128, 64, 32, 19, 11, 6
D    256, 128, 64, 37, 21,  8, 3
```

Their annihilators are the lines

```text
A    30 xor 42 = 52
B    25 xor 42 = 51
C     7 xor 25 = 30
D     7 xor 52 = 51
```

The V45 line `7 xor 42 = 45` is the fifth. These five lines are five of the
seven lines in the 8-point space

```text
{0, 7, 25, 30, 42, 45, 51, 52}
```

Any two of the five frames meet in 64 vectors. The selected kappa is
unchanged.

## What was executed

The checker builds each span and its annihilator. It does not rerun the
fresh-extraction search.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the frame table in PR 2979, head
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to these
lines. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rank7-frame-lines/verify.py
python3.12 -B research/rank7-frame-lines/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-frame-lines
```

## Open next questions

The four frames and the seven lines are finite. A fresh-extraction search
would leave this package.

## Credit

mdumitrean named these frames in PR 2979. This package computes their
annihilators.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
