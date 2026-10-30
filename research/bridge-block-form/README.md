# Four-wire bridge block form

## Question

A bridge `(target ← source, q)` adds `q` times `X_source` to `X_target` and subtracts `q` times `Y_target` from `Y_source`. Is its eight-wire matrix `diag(E, E^{-T})` for a determinant-one matrix `E`?

## Result

For all four wires and every coefficient from −12 through 12, the bridge matrix equals that block form. There are 300 bridges. Each `E` has determinant 1, and the bridge with the negated coefficient is the inverse. Every product of two bridges with coefficients from −3 through 3 stays in the same form. There are 7,056 products. The selected κ is unchanged.

## Boundary

This checks the bridge matrices. It does not census bridge schedules, insert free bridges, or price an idle alphabet. The stop rule is to record this block form.

## Reproduce

```bash
python3.12 -B research/bridge-block-form/verify.py
python3.12 -B research/bridge-block-form/test_verify.py
```

## Open next questions

None. The bridges and the products are finite. A schedule census would leave this package.

## Credit

Matarener recorded the block form in PR #3836. The checker rebuilds the matrices and multiplies them. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
