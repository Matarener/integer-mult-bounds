# The telescoping tensor factor is absorbed by the same gate

**Claim type:** an explicit absorption bound for one telescoping monomial.
**No new κ.** The section ceiling `10 p^2` and the section error
`p^6 exp(-p^2)` stay hypotheses. The selected record remains `23/10000`.

## Question

#4484 absorbs `g (10 p^2)^g exp(-p^2)` under the gate
`p ≥ max(64, 4K + 2C)` and `16 g ceil(log2 p) ≤ p`. A `g`-fold triangle
inequality carries `g - 1` inverse ceilings and one section error, which is
`g (10 p^2)^{g-1} p^6 exp(-p^2)`. Does that monomial stay below `2^{-C p}`
under the same gate?

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (10 p^2)^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. A global factor `exp(K p)`
does not change the conclusion. Whenever `g log p = o(p)`, every fixed pair
`K, C` satisfies the gate for all large `p`.

The extra factor against #4484 is `p^4 / 10`, because

```text
g (10 p^2)^{g-1} p^6 = g (10 p^2)^g (p^4 / 10).
```

The gate still does not cover every `g`. At `g = p^2` the telescoping error
is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`: the values at 2, 3 and 4 are `2`, `6` and `24`,
and the step uses `k + 1 ≥ 2`. The tail of `e` is then at most the geometric
series of ratio `1/2`, so `e < 3 < 4` and `exp(K p) ≤ 2^{2 K p}`, with
equality only at `K = 0`.

Since `10 < 16`, `(10 p^2)^{g-1} ≤ (16 p^2)^{g-1} = 2^{4(g-1)} p^{2(g-1)}`.
At `g = 1` both sides are 1. Therefore

```text
g (10 p^2)^{g-1} p^6 exp(K p - p^2)
  < g 2^{4g-4} p^{2g+4} 2^{2 K p - p^2}.
```

The hypothesis `16 g L ≤ p` forces `g ≤ p ≤ 2^L`, and `p ≤ 2^L` gives
`p^{2g+4} ≤ 2^{(2g+4) L}`. The product is strictly less than

```text
2^{2 g L + 4 g + 5 L - 4 + 2 K p - p^2}.
```

It remains to show that this exponent is at most `-C p - 1`. For every
integer `p ≥ 64`, `8 L ≤ p`. The base is `8 · 7 = 56 ≤ 64` at `p = 2^6`, and
`8 ≤ 64`. If `8(m + 1) ≤ 2^m`, then `8(m + 2) ≤ 2^m + 8 ≤ 2^{m+1}`. On each
dyadic interval the largest ratio of `L` to `p` is at the left endpoint.
Also `L ≥ 1` for `p ≥ 2`, so the gate gives `16 g ≤ p`.

Clear the eighths. The four pieces scale as `8 · 2 g L = 16 g L ≤ p`,
`8 · 4 g = 2 · 16 g ≤ 2 p`, `8 · 5 L = 5 · 8 L ≤ 5 p`, and
`8 (2 K + C) p ≤ 4 p^2` once `p ≥ 4 K + 2 C`, because
`8 (2 K + C) = 4 (4 K + 2 C)`. Their sum is at most `4 p^2 + 8 p`, and the
coefficients of `p` are `1 + 2 + 5 = 8`. Doubling the exponent plus `C p`
therefore leaves at most

```text
-(p^2 - 2 p + 8).
```

At `p = 2` the polynomial equals 8, and the step to the next integer is
`2 p - 1`. In particular it is at least 8 for every integer `p ≥ 2`, so the
doubled quantity is at most `-8` and the exponent is at most `-C p - 4`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so `p/(32 log2 p) ≤ p/(16 L)` and the gate holds eventually.
Every fixed `K` and `C` then satisfy `p ≥ 4 K + 2 C` as well.

At `g = p^2` the monomial equals `g (10 p^2)^g exp(-p^2) · p^4 / 10`. Here
`(10 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `10 p^2 ≥ 40 > 4` and `e < 4`,
while `p^6 / 10 > 1` because `p^6 ≥ 64 > 10`. The product is greater than 1,
which is not below `2^{-C p}`.

## Not covered

- A proof that each section inverse is at most `10 p^2`, or that each section
  error is less than `p^6 exp(-p^2)`. This comparison starts from both.
- Replacing any inverse ceiling by the approximant norm
  `10 p^2 + p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-fold --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-fold
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T01:04:20Z, 338 records;
discussions fetched 2026-10-22T01:05:06Z, 3363 records) names this draft, #4484
(the `(10 p^2)^g` absorption, which leaves this monomial open), the
section-error packages #4439, #4442 and #4452, discussion comment 19078965
(a factor 2 on `g p^{10 g}`, not this fold), the locality audit that keeps
`g p^{10 g} exp(-p^2)`, and `research/gaussian-expansion-headroom`. No other
package assigns the `(10 p^2)^{g-1} p^6` absorption. A search miss is not a
novelty certificate. #4484 is the predecessor monomial. HALO is the error
sentence.

## Open next questions

1. **Can an approximant norm replace the inverse ceiling?** The product above
   uses `g - 1` copies of `10 p^2`. If those factors are approximants, the
   ceiling becomes `10 p^2 + p^6 exp(-p^2)`. The first step is to expand that
   binomial and test each extra term in the same power-of-two budget.

## Credit

- The tensor sentence and the gate `g log p = o(p)` are #4100's.
- The ceiling `10 p^2` is Ryanson Jonathan's #4462, as carried through #4481.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The `(10 p^2)^g` absorption is #4484. This package is the next monomial.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
