# Spare bits in the online storage budget

## Question

The published online magnitudes are bounded by terms such as `2^(8p+18) p^2` and `2^18 p^4`. Does the budget

```
G = 8p + 8 ceil(log2(p+2)) + 32
```

leave twelve spare magnitude bits?

## Result

For every precision `p >= 101`, write `c = ceil(log2(p+2))`. Then `c >= 7` and `p < 2^c`, so `p^2` has at most `2c` bits. The prefix bound `2^(8p+18) p^2` therefore has bit length at most `8p+18+2c`, and

```
G - (8p+18+2c) = 6c+14 >= 56.
```

The spare is at least 56, which covers the claimed twelve bits. On precisions 101 through 300 the prefix bound is the widest of the 13 published magnitudes, and each of those 2,600 bit lengths fits in `G-56`. The minimum spare on that range is 56, at precision 101. The selected κ is unchanged.

## Boundary

This checks the bit-length comparison. It does not run the Gaussian core. The stop rule is to record this spare.

## Reproduce

```bash
python3.12 -B research/storage-spare-bits/verify.py
python3.12 -B research/storage-spare-bits/test_verify.py
```

## Open next questions

None. The bit-length comparison settles the twelve-bit claim. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the storage budget in PR #3851. The checker compares it with the stated magnitudes. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
