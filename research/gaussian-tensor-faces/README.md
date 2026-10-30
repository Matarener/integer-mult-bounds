# The face factor 2 spends one bit of slack

**Claim type:** an explicit absorption bound for one constant factor.
**No new κ.** The section ceiling `10 p^2` and the section error
`p^6 exp(-p^2)` stay hypotheses. The selected record remains `23/10000`.

## Question

#4486 absorbs

```text
g (10 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(-p^2)
```

under the gate `p ≥ max(64, 4K + 2C)` and `16 g ceil(log2 p) ≤ p`, with
exponent at most `-C p - 4`. HALO partitions boundary outputs into `2g`
rectangles, and a review note asks for a factor `2g` on the core error.
Does that extra factor of 2 stay below `2^{-C p}` under the same gate?

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
2 g (10 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
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

Thus `10 p^2 + p^6 exp(-p^2) < 10 p^2 + 1 < 16 p^2`, because `1 < 6 p^2`
for every integer `p ≥ 2`. At `g = 1` the power `g - 1` is zero. For
`g ≥ 2` the approximant base is strictly smaller than `16 p^2`, so

```text
2 g (10 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2)
  < 2 · g 2^{4g-4} p^{2g+4} 2^{2 K p - p^2}.
```

The gate forces `g ≤ p ≤ 2^L`, and `L ≥ 1`. Since `2 = 2^1`, the product is
strictly less than

```text
2^{1 + 2 g L + 4 g + 5 L - 4 + 2 K p - p^2}.
```

Clear the eighths. The four pieces scale as `8 · 2 g L = 16 g L ≤ p`,
`8 · 4 g = 2 · 16 g ≤ 2 p`, `8 · 5 L = 5 · 8 L ≤ 5 p`, and
`8 (2 K + C) p ≤ 4 p^2` once `p ≥ 4 K + 2 C`, because
`8 (2 K + C) = 4 (4 K + 2 C)`. The coefficients of `p` are `1 + 2 + 5 = 8`.
Doubling the exponent without the new bit, plus `C p`, leaves at most
`-(p^2 - 2 p + 8)`. That polynomial equals 8 at `p = 2` and increases by
`2 p - 1`, so the doubled quantity is at most `-8`. The exponent without
the face factor is at most `-C p - 4`. One bit lowers the remaining slack
from 4 to 3, and the exponent above is at most `-C p - 3`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so the gate holds eventually, and every fixed `K` and `C`
satisfy `p ≥ 4 K + 2 C` as well.

At `g = p^2` the product is twice a quantity larger than
`g (10 p^2)^{g-1} p^6 exp(-p^2)`. The smaller monomial equals
`g (10 p^2)^g exp(-p^2) · p^4 / 10`, and
`(10 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `10 p^2 ≥ 40 > 4` and `e < 4`,
while `p^6 / 10 > 1` because `p^6 ≥ 64 > 10`. That product is greater than 1,
so the face-factor monomial is greater than 1 as well.

## Not covered

- A proof that the tensor difference is at most this monomial.
- A proof that a section inverse is at most `10 p^2`, or that a section
  error is less than `p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-faces --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-faces
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T01:16:25Z, 340 records;
discussions fetched 2026-10-22T01:17:10Z, 3365 records) names this draft, #4486
(the approximant budget, which leaves the factor 2 open), #4484 and #4485,
discussion comment 19078965, and the locality audit. That audit already says a
factor 2 on `g p^{10 g} exp(-p^2)` is absorbed by `2^{-C p}`. It does not
give this gate or the slack 3 for the approximant base. A broad search for
`2g` also hits unrelated `D(2G)` claims. A search miss is not a novelty
certificate. #4486 is the predecessor budget. HALO is the error sentence.

## Open next questions

1. **Is the tensor difference at most this monomial?** Another constant in
   front of the same product is not the missing step. The first step is to
   expand one axis of the tensor product and bound that slice by one section
   error.

## Credit

- The tensor sentence, the `2g` rectangles, and the gate `g log p = o(p)` are #4100's.
- The ceiling `10 p^2` is Ryanson Jonathan's #4462, as carried through #4481.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The approximant budget is #4486. This package spends one bit of its slack.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
