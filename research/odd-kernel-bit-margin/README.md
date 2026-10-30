# Odd kernels exceed the dyadic coefficient-bit bill

**Partial. No new exponent.**

The ADDRESS word for power `k` has ten unit coefficients and six variable
coefficients in the slope `k/4`: the slope, one plus the slope, the negated
slope twice, the negated reciprocal, and the reciprocal minus one. Each
rational is charged the bit length of its absolute numerator plus the bit
length of its denominator. The ten units contribute 20, and the word tariff
is that 20 plus the six variable charges.

A fused program uses powers `(-q 2^j, q 2^{j+1}, -q 2^j)`. A baseline program
uses `(-q 2^j, q 2^j, q 2^j, -q 2^j)`. For every kernel in `{3, 5, 7, 9, 15}`
and every `j` from 0 through 32, both programs cost strictly more than the
same program at kernel 1. That is 165 fused comparisons and 165 baseline
comparisons. The least fused margin is 14, at kernel 3 and `j = 0`. The least
baseline margin is 16. The word tariff itself falls from `T(1) = 45` to
`T(2) = 38` to `T(4) = 32`.

## What was executed

The checker rebuilds every affine coefficient and adds the bit lengths. It
does not try another tariff.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ADDRESS word in PR 3702, head
`89288f824e44051d5a032ad6c28bc41f81746c28`.

## Scope and evidence

Original card: `connector-alphabet-change`, priority revision 6, refined to
this bill. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/odd-kernel-bit-margin/verify.py
python3.12 -B research/odd-kernel-bit-margin/test_verify.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-bit-margin
```

## Open next questions

This margin is the comparison. Another tariff would leave it.

## Credit

Wentao Li published the coefficient-bit tariff and the 165-point exceedance.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
