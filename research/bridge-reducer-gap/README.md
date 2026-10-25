# Row reduction of elementary transvections

## Question

The bridge closure procedure clears a determinant-one matrix by integer row operations `row_i += q row_j`. Which products of two plus-or-minus-one transvections on four wires does that procedure finish?

## Result

There are 24 transvections, one for each ordered pair of distinct wires and each coefficient ±1. Each reduces to the identity. Their 576 products all have determinant 1. The procedure reduces 564 of them to the identity, returns no operation list for 6, and stops for 6 when a column has no remaining pivot. Replaying the returned operations reproduces the identity. The selected κ is unchanged.

## Boundary

This runs the row operations on these products. It does not census bridge schedules or replace the procedure. The stop rule is to record these outcomes.

## Reproduce

```bash
python3.12 -B research/bridge-reducer-gap/verify.py
python3.12 -B research/bridge-reducer-gap/test_verify.py
```

## Open next questions

None. The transvection products are finite. A schedule census would leave this package.

## Credit

Matarener recorded the row reducer in PR #3836. The checker runs it on every product of two plus-or-minus-one transvections. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
