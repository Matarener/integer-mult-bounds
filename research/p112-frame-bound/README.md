# The lost-free P112 bound is 56

**Partial. No new exponent.**

An orthonormal list in `F2^9` has length at most 9. The planes of a lost-free
set that meet one eight-frame supply two orthonormal vectors per port, so

```text
2 · 4 = 8 ≤ 9  and  2 · 5 = 10 > 9
```

Each frame therefore meets at most 4 ports of the set. The published weights
are positive and sum to 14, and every selected label has weighted coverage
one, so

```text
|S| ≤ 4 · 14 = 56
```

The fixed block tariff is `72 + 2 · (112 - s)`. It costs 232 at size 32, then
230, 228, 226 and 224 at sizes 33 through 36. Size 37 costs 222, so a cost
strictly below 224 starts at 37. For every size at most 56 the tariff is at
least its value at 56:

```text
72 + 2 · (112 - 56) = 184
```

## What was executed

The checker multiplies these counts. It does not rerun the 4,032-frame census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the frame argument in PR 3674,
head `efe1d72e4dcd14c2c48693b8f3a8c66f23d539b0`.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to this
bound. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/p112-frame-bound/verify.py
python3.12 -B research/p112-frame-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/p112-frame-bound
```

## Open next questions

This bound is the certificate. The frame census would leave it.

## Credit

ToikY published the compact certificate. Matarener published the lost-free
P112 bound it checks.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
