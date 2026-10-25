# Erasure of one unweighted tensor kernel

## Question

On the family `p = 2^(10a)`, `m = 2^(4a)`, `X = 2^(3a)`, does toward-zero rounding of the unweighted tensor coefficient on the `P = 32768p` grid return zero while the weighted entry stays larger than one `p` unit?

## Result

For every integer `a` from 26 through 64, set `d = u = m`, `D = d - 1`, `w = 4X + 2` and `k = X/2048`. Then `m^5 = p^2`, `u d <= p`, `u` meets `ceil(log2(8p))`, `(w-2)^2 u = 16p`, and `d - 2 > 2w + k + 3`.

The unweighted exponent `D(3mk - 1)` is strictly larger than `P`. Its ratio to `p` is at least `3·2^a/4096 - 1/(2X^2)`, and that lower bound more than doubles at each larger `a`. The weighted exponent `16Dk(2w+k+3) + D + 1` is strictly below both `p/8` and

```
(8 + 1/2048 + 7/128)/128 + 1/128^2,
```

which is itself below `1/8`. There are 39 such scales. The selected κ is unchanged.

## Boundary

This checks the rational comparison on this family. It does not build the tensor or run the Gaussian core. The stop rule is to record this erasure.

## Reproduce

```bash
python3.12 -B research/kernel-grid-erasure/verify.py
python3.12 -B research/kernel-grid-erasure/test_verify.py
```

## Open next questions

None. The rational comparison settles this family. Building the tensor would leave this package.

## Credit

Chafik Boukhalfa recorded the kernel-grid failure in PR #489. The checker recomputes the exponents. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
