# Coefficient-width bounds

## Question

The Gaussian interval routine sets `X = 4F`, `k = ceil(log2(8(X+1)))`, `H0 = P+X+k+16`, `c = ceil(log2(H0))`, and `R = P+4X+4k+2c+64`. Which inequalities do these integers satisfy for every positive precision `P` and frequency bound `F`?

## Result

The minimum is at `P = F = 1`: `k = 6`, `c = 5`, `H0 = 27`, and `R = 115`. For every larger positive pair, `H0 >= 27`, `R >= 115`, and `R < 5 H0`. The block count `ceil(R/3)+8` is at most `R/2`, and `R^2+2 <= 32 H0^2`. The series comparison gives `e < 3 < 4`, so `exp(X+1) < 2^(2X+2)`. The resulting width exponent is `-P-2X-3k-57`, which is at most `-P-83`. All 1,600 pairs with both arguments at most 40 meet the same bounds. The selected κ is unchanged.

## Boundary

This proves these integer comparisons. It does not run the Gaussian core or the word multiplier. The stop rule is to record these bounds.

## Reproduce

```bash
python3.12 -B research/coefficient-width-bound/verify.py
python3.12 -B research/coefficient-width-bound/test_verify.py
```

## Open next questions

None. The inequalities are settled for every positive pair. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the coefficient widths in PR #3851. The checker proves the integer comparisons. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
