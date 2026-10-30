# Odd kernels exceed the dyadic coefficient-bit bill

**Partial. No new exponent.**

The address word for a nonzero integer power `k` has six affine events. Ten of
its coefficients are `±1` and contribute 20 bits. The other six are
`k/4`, `1 + k/4`, two copies of `-k/4`, `-4/k`, and `4/k - 1`. The word cost
is the sum of `bit_length(|numerator|) + bit_length(denominator)` over those
coefficients in lowest terms.

The fused bill at kernel `q` and index `j` is two copies of the cost at
`q * 2^j` plus the cost at `q * 2^{j+1}`. The baseline bill is four copies of
the cost at `q * 2^j`. On kernels `{3, 5, 7, 9, 15}` and every `j` from 0
through 32, both bills strictly exceed the same bills at kernel 1. That is
165 fused comparisons and 165 baseline comparisons. The smallest fused margin
is 14, at kernel 3 and `j = 0`.

The word cost is not monotone in the absolute power: the costs of 4, 2, and 1
are 32, 38, and 45. Fusion saves bits on every row of this grid, and the odd
kernels stay above the dyadic fused bill after that saving. The selected kappa
is unchanged.

## What was executed

The checker prices these 165 rows from the six affine events. It does not
extend `j` past 32.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the coefficient-bit tariff in
PR 3702, head `89288f824e44051d5a032ad6c28bc41f81746c28`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
grid. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/odd-kernel-bit-tariff/verify.py
python3.12 -B research/odd-kernel-bit-tariff/test_verify.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-bit-tariff
```

## Open next questions

This grid is the tariff comparison. A larger exponent range would leave it.

## Credit

Wentao Li (VictorLiwentao) compared these kernels on this tariff.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
