# Slot width for a nonnegative convolution

## Question

Two length-`n` sequences have nonnegative coefficients below `2^a` and `2^b`. Does every convolution coefficient fit in the low half of a slot of `a+b+ceil(log2 n)+1` bits?

## Result

The largest overlap is exactly `n(2^a-1)(2^b-1)`. Since `n <= 2^{ceil(log2 n)}` and `(2^a-1)(2^b-1) = 2^{a+b}-2^a-2^b+1`, that overlap is strictly below `2^{a+b+ceil(log2 n)}`. The inequality holds for every positive `a`, `b`, and `n`. It was evaluated on all 25,600 triples with bit lengths at most 20 and lengths at most 64.

Every sequence pair with bit lengths 1 or 2 and length at most 4 was convolved directly: 79,604 pairs. Each coefficient stays at or below the closed-form overlap and strictly below the slot half. The selected κ is unchanged.

## Boundary

This checks the slot inequality and these sequences. It does not run the word multiplier or the Gaussian core. The stop rule is to record this slot bound.

## Reproduce

```bash
python3.12 -B research/convolution-slot-bound/verify.py
python3.12 -B research/convolution-slot-bound/test_verify.py
```

## Open next questions

None. The inequality holds for every positive length. The word multiplier would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the convolution slot in PR #3851. The checker proves the overlap bound and enumerates the small sequences. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
