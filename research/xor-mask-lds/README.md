# XOR-mask decreasing subsequences

## Question

For a mask of Hamming weight W, the sequence of values `x xor mask` has longest decreasing subsequence exactly `2^W`. Composing two such maps replaces the masks by their XOR, and that weight is at most the sum of the weights.

## Result

Every mask in dimensions 1 through 12 meets the length. There are 8,190 masks. Every pair of masks in dimensions 1 through 10 satisfies

```text
wt(a xor b) + 2 wt(a and b) = wt(a) + wt(b)
```

so the composed length `2^wt(a xor b)` is at most the product of the two lengths. There are 1,398,100 pairs. The selected κ is unchanged.

## Boundary

This checks the subsequence length and the weight identity. It does not price a bit-free supplier, choose a tape count, or run a layout schedule. The stop rule is to record this length.

## Reproduce

```bash
python3.12 -B research/xor-mask-lds/verify.py
python3.12 -B research/xor-mask-lds/test_verify.py
```

## Open next questions

None. The masks and the pairs are finite. A supplier pricing would leave this package.

## Credit

Matarener recorded the weight-W length in PR #3825. The checker reimplements the subsequence and the weight identity. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
