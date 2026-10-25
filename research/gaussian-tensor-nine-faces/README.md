# The face factor 2 spends one bit of the coefficient-9 slack

**Claim type:** an explicit absorption bound for one constant factor.
**No new κ.** The section ceiling `9 p^2` and the section error
`p^6 exp(-p^2)` stay hypotheses. The selected record remains `23/10000`.

## Question

#4497 absorbs

```text
g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2)
```

under the gate `p ≥ max(64, 4K + 2C)` and `16 g ceil(log2 p) ≤ p`, with
exponent at most `-C p - 4`. Does the extra factor of 2 still leave the
monomial below `2^{-C p}`?

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
2 g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. The factor 2 contributes
one bit. The exponent is at most `-C p - 3`. Whenever `g log p = o(p)`,
every fixed pair `K, C` satisfies the gate for all large `p`.

This comparison does not identify HALO's `2g` rectangles with the tensor
error. It charges the constant 2 against slack that is already present.
At `g = p^2` the same error is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`: the values at 2, 3 and 4 are `2`, `6` and `24`,
and the step uses `k + 1 ≥ 2`. The tail of `e` is then at most the geometric
series of ratio `1/2`, so `e < 3 < 4` and `exp(K p) ≤ 2^{2 K p}`, with
equality only at `K = 0`.

For every integer `p ≥ 64`, `8 L ≤ p`. The base is `8 · 7 = 56 ≤ 64` at
`p = 2^6`, and `8 ≤ 64`. If `8(m + 1) ≤ 2^m`, then
`8(m + 2) ≤ 2^m + 8 ≤ 2^{m+1}`. On each dyadic interval the largest ratio of
`L` to `p` is at the left endpoint. From `8 L ≤ p`, `48 L = 6 · 8 L ≤ 6 p`.
The quadratic `4 p^2 - 3 p - 4` equals 6 at `p = 2` and increases by `8 p + 1`
at the next integer, so `6 p ≤ 8(p^2 - 1)`. Hence `6 L ≤ p^2 - 1`. Since
`p ≤ 2^L`, `p^6 ≤ 2^{6 L} ≤ 2^{p^2 - 1}`, and

```text
p^6 exp(-p^2) < p^6 2^{-p^2} ≤ 1/2.
```

Thus `9 p^2 + p^6 exp(-p^2) < 9 p^2 + 1 < 16 p^2`, because `1 < 7 p^2`
for every integer `p ≥ 2`. At `g = 1` the power `g - 1` is zero. For
`g ≥ 2` the approximant base is strictly smaller than `16 p^2`, so

```text
2 g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2)
  < 2 · g 2^{4g-4} p^{2g+4} 2^{2 K p - p^2}.
```

The gate forces `g < 2^L`, because `L ≥ 1` and `g ≤ p/(16 L) ≤ p/16`.
Since `2 = 2^1`, the product is strictly less than

```text
2^{1 + 2 g L + 4 g + 5 L - 4 + 2 K p - p^2}.
```

Clear the eighths of the exponent without the new bit. The four pieces
scale as `8 · 2 g L = 16 g L ≤ p`, `8 · 4 g = 2 · 16 g ≤ 2 p`,
`8 · 5 L = 5 · 8 L ≤ 5 p`, and `8 (2 K + C) p ≤ 4 p^2` once
`p ≥ 4 K + 2 C`, because `8(2 K + C) = 4(4 K + 2 C)`. The constant `-4`
contributes `-32`. The sum is at most `-4(p^2 - 2 p + 8)`. The coefficients
of `p` are `1 + 2 + 5 = 8`. At `p = 2` the polynomial equals 8, and the step
to the next integer is `2 p - 1`. It is therefore at least 8, so eight times
the shifted exponent is at most `-32`. The exponent without the face factor
is at most `-C p - 4`. One bit lowers the remaining slack from 4 to 3, and
the exponent above is at most `-C p - 3`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so the gate holds eventually, and every fixed `K` and `C`
satisfy `p ≥ 4 K + 2 C` as well.

At `g = p^2` the product is twice a quantity larger than
`g (9 p^2)^{g-1} p^6 exp(-p^2)`. The smaller monomial equals
`g (9 p^2)^g exp(-p^2) · p^4 / 9`, and
`(9 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `9 p^2 ≥ 36 > 4` and `e < 4`,
while `p^4 / 9 > 1` because `p^4 ≥ 16 > 9`. That product is greater than 1,
so the face-factor monomial is greater than 1 as well.

## Not covered

- A proof that the tensor difference is at most this monomial.
- A proof that a section inverse is at most `9 p^2`, or that a section
  error is less than `p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-faces --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-faces
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T02:42:08Z and was
still that commit.

Overlap snapshot: open PRs fetched 2026-10-22T02:42:49Z (356 records) and
discussions fetched 2026-10-22T02:43:31Z (3381 records). A search for
`face factor 2`, `slack of 4` and `9 p^2 + p^6` returned this draft, #4497,
which leaves the factor open, #4487, which spends the same bit on the
coefficient 10, and the predecessor fold #4496. A search miss is not a
novelty certificate. #4497 is the predecessor budget. HALO is the written
error.

## Open next questions

1. **Is one axis of the tensor difference at most two section errors?** The
   scalar factor 2 is not that identification. The first step is to expand
   one axis under the hypotheses `||B_i|| ≤ 9 p^2`,
   `||C_i|| ≤ 9 p^2 + ε` and `||B_i - C_i|| < 2 ε`, with
   `ε = p^6 exp(-p^2)`.

## Credit

- The one-bit charge against slack 4 is the route of #4487.
- The approximant budget with coefficient 9 is #4497.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- HALO's sentence `These 2g sets are disjoint rectangles.` is a volume
  partition. The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
