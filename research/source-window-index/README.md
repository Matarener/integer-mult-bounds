# Source indices of a rounded target window

## Question

The map `j -> floor(t*j/s + 1/2)` sends a source index to a target. For a ratio strictly between 1 and 2, which source indices land in a target window?

## Result

For every denominator `s` from 2 through 20, every numerator `t` with `s < t < 2s`, and every target window `[a, b)` with `0 <= a < b <= 13`, the landing indices are exactly the integers from `ceil(s*(2a-1)/(2t))` up to, but not including, `ceil(s*(2b-1)/(2t))`. There are 17,290 such windows. The rounding is nondecreasing, and the scanned range extends past both ends of each window. The selected κ is unchanged.

## Boundary

This checks this parameter box with integer arithmetic. It does not run the Gaussian core or the word multiplier. The stop rule is to record these windows.

## Reproduce

```bash
python3.12 -B research/source-window-index/verify.py
python3.12 -B research/source-window-index/test_verify.py
```

## Open next questions

None. The parameter box is finite. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the source-window ceilings in PR #3851. The checker compares them with the rounded preimage. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
