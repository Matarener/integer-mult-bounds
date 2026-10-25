# Outer-product mask weights

## Question

When the second mask is written into each set bit of the first, with a fixed row stride, when is the weight of the result the product of the two weights?

## Result

For every pair of masks whose widths multiply to at most 20, a stride equal to the second width gives weight equal to the product. There are 8,408,068 pairs. For every shape with both widths at least 2, a stride one shorter makes the all-ones masks collide, so the weight is strictly smaller than the product. There are 27 such shapes. The selected κ is unchanged.

## Boundary

This checks the flattened weights. It does not price a bit-free supplier, choose a tape count, or run a layout schedule. The stop rule is to record this product.

## Reproduce

```bash
python3.12 -B research/kronecker-mask-weight/verify.py
python3.12 -B research/kronecker-mask-weight/test_verify.py
```

## Open next questions

None. The mask pairs are finite. A supplier pricing would leave this package.

## Credit

Matarener recorded the Kronecker weight in PR #3825. The checker compares the flattened weight with the product on every pair. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
