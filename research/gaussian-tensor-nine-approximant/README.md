# The approximant base 9 p^2 + p^6 exp(-p^2) stays inside the budget

**Claim type:** an explicit absorption bound for one approximant monomial.
**No new κ.** The section ceiling `9 p^2` and the section error
`p^6 exp(-p^2)` stay hypotheses. The selected record remains `23/10000`.

## Question

#4496 absorbs `g (9 p^2)^{g-1} p^6 exp(K p - p^2)` under the gate
`p ≥ max(64, 4K + 2C)` and `16 g ceil(log2 p) ≤ p`. If each of the `g - 1`
factors is an approximant, the base becomes `9 p^2 + p^6 exp(-p^2)`. Does

```text
g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2)
```

stay below `2^{-C p}` under that same gate?

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. A global factor `exp(K p)`
does not change the conclusion. Whenever `g log p = o(p)`, every fixed pair
`K, C` satisfies the gate for all large `p`.

For every integer `p ≥ 64`, the section error is strictly below `1/2`, so

```text
9 p^2 + p^6 exp(-p^2) < 9 p^2 + 1 < 16 p^2.
```

The base therefore remains strictly below the power of two already used for
`(16 p^2)^{g-1}`. No extra bit is spent. The exponent is at most `-C p - 4`.
At `g = p^2` the same error is greater than 1 for every integer `p ≥ 2`,
because it is larger than the inverse-ceiling monomial, which is already
greater than 1.

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
at the next integer, so it stays positive. Equivalently
`6 p ≤ 8(p^2 - 1)`. Combining these estimates gives `6 L ≤ p^2 - 1`. Since
`p ≤ 2^L`, `p^6 ≤ 2^{6 L} ≤ 2^{p^2 - 1}`, and therefore

```text
p^6 exp(-p^2) < p^6 2^{-p^2} ≤ 1/2.
```

Hence `9 p^2 + p^6 exp(-p^2) < 9 p^2 + 1`. Also `1 < 7 p^2` for every
integer `p ≥ 2`, so `9 p^2 + 1 < 16 p^2`. The approximant base is strictly
smaller than `16 p^2`.

At `g = 1` the power `g - 1` is zero. For `g ≥ 2`,

```text
(9 p^2 + p^6 exp(-p^2))^{g-1} < (16 p^2)^{g-1}
  = 2^{4(g-1)} p^{2(g-1)}.
```

In both cases

```text
g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2)
  < g 2^{4g-4} p^{2g+4} 2^{2 K p - p^2}.
```

The gate forces `g < 2^L`, because `L ≥ 1` and `g ≤ p/(16 L) ≤ p/16`.
Together with `p ≤ 2^L`, the product is strictly less than

```text
2^{2 g L + 4 g + 5 L - 4 + 2 K p - p^2}.
```

Clear the eighths. The four pieces scale as `8 · 2 g L = 16 g L ≤ p`,
`8 · 4 g = 2 · 16 g ≤ 2 p`, `8 · 5 L = 5 · 8 L ≤ 5 p`, and
`8 (2 K + C) p ≤ 4 p^2` once `p ≥ 4 K + 2 C`, because
`8(2 K + C) = 4(4 K + 2 C)`. The constant `-4` contributes `-32`. The sum
is at most `-4(p^2 - 2 p + 8)`. The coefficients of `p` are `1 + 2 + 5 = 8`.
At `p = 2` the polynomial equals 8, and the step to the next integer is
`2 p - 1`. It is therefore at least 8, so eight times the shifted exponent
is at most `-32`. The exponent is at most `-C p - 4`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so the gate holds eventually, and every fixed `K` and `C`
satisfy `p ≥ 4 K + 2 C` as well.

At `g = p^2` the approximant monomial is larger than
`g (9 p^2)^{g-1} p^6 exp(-p^2)`, since the added section error is positive
and `g ≥ 2`. The smaller monomial equals
`g (9 p^2)^g exp(-p^2) · p^4 / 9`. Here
`(9 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `9 p^2 ≥ 36 > 4` and `e < 4`,
while `p^4 / 9 > 1` because `p^4 ≥ 16 > 9`. That product is greater than 1,
and so is the approximant monomial.

## Not covered

- A proof that a section inverse is at most `9 p^2`, or that a section
  error is less than `p^6 exp(-p^2)`. The approximant ceiling is their sum.
- The factor `2` in front of `g`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-approximant --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-approximant
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T01:56:48Z and was
still that commit.

Overlap snapshot: open PRs fetched 2026-10-22T01:57:24Z (350 records) and
discussions fetched 2026-10-22T01:58:13Z (3374 records). A search for
`9 p^2 + 1`, `9 p^2 + p^6` and `approximant base` returned this draft, #4496,
which leaves the base open, and the coefficient-10 packages #4486 and #4487.
A search miss is not a novelty certificate. #4496 is the predecessor fold.
HALO is the written error.

## Open next questions

1. **Does the face factor 2 still fit?** The exponent above is at most
   `-C p - 4`. The first step is to charge that extra factor of 2 against
   this slack of 4.

## Credit

- The section-error comparison `p^6 2^{-p^2} ≤ 1/2` is the route of #4486.
- The predecessor fold with coefficient 9 is #4496.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
