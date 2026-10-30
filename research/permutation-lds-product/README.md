# Permutation decreasing-subsequence products

## Question

For two permutations of the same order, written as sequences, is the longest decreasing subsequence of their composition at most the product of the two lengths?

## Result

Through order 7, every pair obeys the product bound. There are 25,935,017 pairs. Equality holds for 44,061 of them, including every pair of identity permutations. The selected κ is unchanged.

## Boundary

This checks compositions through order 7. It does not price a bit-free supplier, choose a tape count, or run a layout schedule. The stop rule is to record this product.

## Reproduce

```bash
python3.12 -B research/permutation-lds-product/verify.py
python3.12 -B research/permutation-lds-product/test_verify.py
```

## Open next questions

None. The permutations through order 7 are finite. A supplier pricing would leave this package.

## Credit

Matarener recorded submultiplicativity for sampled permutations in PR #3825. The checker compares every pair through order 7. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
