# Neumann tail below one 16p unit

## Question

With `g = 1/(16p)` and `J = 512 p²`, is the Neumann tail `2(1-g)^J/g` below `2^(-16p)`?

## Result

For every precision from 101 through 200, `(1 - 1/(16p))^(16p)` is strictly below `1/2`. The length splits exactly as

```
512 p² = (16p) * (32p).
```

Raising the contraction to the `32p` power puts `(1-g)^J` strictly below `2^(-32p)`. Multiplying by `2/g = 32p` leaves a tail strictly below `32p * 2^(-32p)`. Since `32p < 2^(16p)`, that quantity is strictly below `2^(-16p)`. There are 100 such precisions. The selected κ is unchanged.

At precision 1 the same tail was compared in full integers: `32 * 15^512 * 2^16 < 16^512`.

## Boundary

This checks the contraction and these precisions. It does not run the Gaussian core. The stop rule is to record this tail.

## Reproduce

```bash
python3.12 -B research/neumann-tail-bound/verify.py
python3.12 -B research/neumann-tail-bound/test_verify.py
```

## Open next questions

None. The contraction settles the tail on this range. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the Neumann tail in PR #3851. The checker proves the contraction. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
