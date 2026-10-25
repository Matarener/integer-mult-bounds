# Margin between two expansion axes and the chirp input cap

## Question

An expansion axis has norm below `3/4`, and the chirp input cap is `3/5`. Does one axis fit, and how much error can two axes absorb?

## Result

`3/4` is larger than `3/5`, so the one-axis bound does not meet the cap. The product of the two bounds is `9/16`. The difference is exact:

```
3/5 - 9/16 = 3/80.
```

Adding the gap back recovers `3/5`. Every pair of multiples of `1/400` that stay below `3/4`, together with every error `0`, `1/80`, or `2/80`, has a sum strictly below `3/5`. There are 270,000 such sums. The selected κ is unchanged.

## Boundary

This checks the rational margin and this grid. It does not run the Gaussian core or the chirp consumer. The stop rule is to record this margin.

## Reproduce

```bash
python3.12 -B research/expansion-axis-margin/verify.py
python3.12 -B research/expansion-axis-margin/test_verify.py
```

## Open next questions

None. The rational margin is exact. The Gaussian core and the chirp consumer would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the two-axis handoff in PR #3851. The chirp input cap of `.6` is the hypothesis in PR #3763. The checker compares the two rationals. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
