# Diagonal weights in a Schur correction

## Question

If an interior block is a diagonal similarity of an unweighted matrix, do the interior weights cancel in the Schur correction between two boundary indices?

## Result

For every invertible 2×2 interior with entries in `{−1, 0, 1}`, every boundary coupling with those entries, and every scale in `{1, 2, 3}`, the weighted correction equals `(a_b / a_c)` times the unweighted correction. The two interior scales cancel. There are 314,928 such checks. The selected κ is unchanged.

## Boundary

This checks this matrix box with exact rational arithmetic. It does not run the Gaussian core or the word multiplier. The stop rule is to record this cancellation.

## Reproduce

```bash
python3.12 -B research/schur-weight-cancellation/verify.py
python3.12 -B research/schur-weight-cancellation/test_verify.py
```

## Open next questions

None. The matrix box is finite. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the Schur weight cancellation in PR #3851. The checker recomputes the correction on this box. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
