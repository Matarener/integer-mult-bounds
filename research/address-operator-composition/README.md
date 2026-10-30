# Full exchange then the normal equals the complement

**Partial. No new exponent.**

The pinned bit operator exchanges the two address halves on a projector.
For the canonical root `q = (2, 2, 0, 0, 0, 0, 0, 0)`, the normal projector
is `P = q q^T / 8`. It fixes `q`, squares to itself, and has trace 1. Its
complement `K = I - P` kills `q`.

On each of the 16 basis pairs, exchanging every coordinate and then the
normal line equals exchanging the complement. On the root itself the two
frames disagree about the bank:

`D_I(q, 0) = (0, q)` and `D_K(q, 0) = (q, 0)`.

The selected kappa is unchanged.

## What was executed

The checker compares these operators on the basis and on this root. It does
not rerun the port boundary charts.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the address witness in
PR 3772, head `5b1d4c2ade90dfa0d8b837148cc5b9cc4be1cdab`.

## Scope and evidence

Original card: `bit-helper-contract`, priority revision 6, refined to this
identity. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the bit-operator
clause. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/address-operator-composition/verify.py
python3.12 -B research/address-operator-composition/test_verify.py
python3.12 -B scripts/research_package.py --package research/address-operator-composition
```

## Open next questions

This identity is the operator. A matched endpoint word would leave it.

## Credit

The pinned recipe states this composition. Gonzalo Mier recorded the
full-frame and complement images as an address witness. The recipe file
names DreamingOfClouds, Zhihao Chen, eumemic and chafreaky.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
