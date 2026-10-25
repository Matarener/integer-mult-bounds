# Prefix-mask basis

## Question

The prefix masks `M_t = 2^(t+1) - 1` are the masks with the lowest `t+1` bits set. Which subset of them XORs to a given mask, and how large is the smallest such subset?

## Result

For every mask in dimensions 1 through 20, exactly one subset works. It consists of the positions where a bit differs from the next bit, taking the bit past the top as zero. Its size equals `2 * (number of 1-runs) - 1` when the low bit is set, and `2 * (number of 1-runs)` otherwise. There are 2,097,150 masks.

A mask with only the low bit set has one boundary. Every other single-bit mask has two. The selected κ is unchanged.

## Boundary

This checks the basis and the boundary count. It does not price a bit-free supplier, choose a tape count, or run a layout schedule. The stop rule is to record this unique subset.

## Reproduce

```bash
python3.12 -B research/prefix-mask-basis/verify.py
python3.12 -B research/prefix-mask-basis/test_verify.py
```

## Open next questions

None. The masks are finite. A supplier pricing would leave this package.

## Credit

Matarener recorded the prefix-reversal count in PR #3825. The checker reimplements the subset and the run count. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
