# Gap in the simultaneous production bounds

## Question

Can one integer precision `p >= 101`, one scale `u >= ceil(log2(8p))`, and one positive integer spacing `d` satisfy `u*d <= p` together with `d-2 > 4w`, where `w = ceil(sqrt(16p/u))+2`?

## Result

No precision from 101 through 4463 works. For each of those 4,363 values, every real scale at or above `ceil(log2(8p))` makes the smallest admissible integer spacing obey `u*d > p`. At precision 101 the least product is 630.

Precision 4464 is the first that works. The witness is `u = 16`, `d = 279` and `w = 69`: `16*279 = 4464`, `279-2 > 4*69`, and `ceil(sqrt(4464)) = 67`. The spacing also leaves a nonempty interval for `theta`. The selected κ is unchanged.

## Boundary

This checks these simultaneous inequalities. It does not run the Gaussian core. The stop rule is to record this domain gap.

## Reproduce

```bash
python3.12 -B research/production-domain-gap/verify.py
python3.12 -B research/production-domain-gap/test_verify.py
```

## Open next questions

None. The obstruction and the first witness settle these simultaneous inequalities. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) stated the production conditions in PR #3851. The checker compares them. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
