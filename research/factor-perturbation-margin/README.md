# Margins for one rounded LU perturbation

## Question

Do the published product, inverse, growth and residual margins follow from the stated factor caps?

## Result

Take `eta = 2^(-32768 p)`. The lower factor moves by at most `2 p eta` and the upper factor by at most `3 p eta`. The caps are `||L|| <= 65 p^2`, `||L^{-1}|| <= 32 p` and `||U|| < 2`.

The product perturbation is then strictly below `200 p^3 eta`. The Neumann denominator stays at least one half, so the perturbed inverse stays at most `64 p`. Adding the lower perturbation keeps the factor at most `66 p^2`. Amplifying the `8 eta` residual by that factor and adding the `2 eta` residual gives `(528 p^2 + 2) eta`, which is at most `530 p^2 eta`. That quantity is strictly below one.

Each comparison reduces to a polynomial against `2^(32768 p)`. All three hold at precision 1. Raising the precision by one at most quadruples the polynomial and multiplies the exponential by `2^32768`. The same comparisons were evaluated directly for every precision from 1 through 200. The selected κ is unchanged.

## Boundary

This checks these four margins. It does not derive the published product-inverse cap of `32 p`, and it does not run the Gaussian core or the word multiplier. The stop rule is to record these margins.

## Reproduce

```bash
python3.12 -B research/factor-perturbation-margin/verify.py
python3.12 -B research/factor-perturbation-margin/test_verify.py
```

## Open next questions

None. The comparisons hold for every positive precision. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the factor caps and the four margins in PR #3851. The checker derives the margins from those caps. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
