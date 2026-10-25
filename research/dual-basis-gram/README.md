# The stated rank-(9,9) dual basis has Gram matrix I

**Partial. No new exponent.**

The equality example for a normalized rank-(9,9) factorization names two
frames in the eight root coordinates. With the standard basis `e_0, …, e_7`,

```text
v = e_0 + e_1,   w = e_0 + e_2,
(h_1, …, h_8) = (v, e_1, e_0 − e_2, e_3, …, e_7),
(d_1, …, d_8) = (w, −e_0 + e_1 − e_2, −e_2, e_3, …, e_7).
```

Every one of the 64 products `h_i · d_j` equals 1 on the diagonal and 0 off
it, so `v · w = 1` and each frame is a basis. The example's stated term costs

```text
(1, 7, 9, 9, 9, 9, 9, 9, 9, 1)
```

add to 72. The selected kappa is unchanged.

## What was executed

The checker builds both frames and multiplies them. A second script repeats
the same products from the coordinate lists. Neither script enumerates the
120 roots or the 130,305 character pairs, and neither evaluates a support
weight.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the dual basis written in PR
3755, head `9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this Gram identity. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/dual-basis-gram/verify.py
python3.12 -B research/dual-basis-gram/test_verify.py
python3.12 -B scripts/research_package.py --package research/dual-basis-gram
```

## Open next questions

The dual basis is an 8 by 8 integer matrix and is fully checked. Support
weights of the ten terms would recount the root set.

## Credit

conorholds stated this dual basis in the rank-(9,9) equality example of PR
3755. This package checks the products that note left to inspection.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
