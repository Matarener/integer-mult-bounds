# The telescoping factor with coefficient 9 is absorbed by the same gate

**Claim type:** an explicit absorption bound for one telescoping monomial.
**No new κ.** The section ceiling `9 p^2` and the section error
`p^6 exp(-p^2)` stay hypotheses. The selected record remains `23/10000`.

## Question

#4495 absorbs `g (9 p^2)^g exp(K p - p^2)` under the gate
`p ≥ max(64, 4K + 2C)` and `16 g ceil(log2 p) ≤ p`. The extra factor in

```text
g (9 p^2)^{g-1} p^6 exp(K p - p^2)
```

is `p^4 / 9`. Does that monomial stay below `2^{-C p}` under the same gate?

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (9 p^2)^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. A global factor `exp(K p)`
does not change the conclusion. Whenever `g log p = o(p)`, every fixed pair
`K, C` satisfies the gate for all large `p`.

The identity is

```text
g (9 p^2)^{g-1} p^6 = g (9 p^2)^g (p^4 / 9).
```

Placing `p^4 / 9` in the exponent contributes `4 L - 3`, because
`p^4 ≤ 2^{4 L}` and `9 > 8 = 2^3`. The resulting exponent is at most
`-C p - 3`.

The gate is not optional for every `g`. At `g = p^2` the telescoping error
is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`: the values at 2, 3 and 4 are `2`, `6` and `24`,
and the step uses `k + 1 ≥ 2`. The tail of `e` is then at most the geometric
series of ratio `1/2`, so `e < 3 < 4` and `exp(K p) < 4^{K p} = 2^{2 K p}`
whenever `K p > 0`. At `K = 0` the factor is 1.

Since `9 < 16`, `(9 p^2)^g < 2^{4 g} p^{2 g}`. Also `p ≤ 2^L`, so
`p^{2 g} ≤ 2^{2 g L}`. The hypothesis `16 g L ≤ p` and `L ≥ 1` force
`g ≤ p/(16 L) ≤ p/16 < 2^L`. Hence

```text
g (9 p^2)^g exp(K p - p^2) < 2^{L + 4 g + 2 g L + 2 K p - p^2}.
```

Call this exponent `E_0`. For every integer `p ≥ 64`, `8 L ≤ p`. The base is
`8 · 7 = 56 ≤ 64` at `p = 2^6`, and `8 ≤ 64`. If `8(m + 1) ≤ 2^m`, then
`8(m + 2) ≤ 2^m + 8 ≤ 2^{m+1}`. On each dyadic interval the largest ratio of
`L` to `p` is at the left endpoint, so `8 L ≤ p`. The gate gives
`2 g L ≤ p/8` and `4 g ≤ p/4`. The linear factor obeys
`(2 K + C) p ≤ p^2 / 2` exactly when `p ≥ 4 K + 2 C`, because
`2(2 K + C) = 4 K + 2 C`. The four pieces sum to at most `p/2 + p^2/2`, and
the slack against `p^2` is `p(p - 1)/2`. At `p = 2` this slack is 1, and it
increases by `p` at the next integer. Thus `E_0 ≤ -C p - 1`.

The telescoping identity multiplies by `p^4 / 9`. Since `9 > 8`,
`1/9 < 1/8`, and `p^4 ≤ 2^{4 L}`, so

```text
p^4 / 9 < 2^{4 L - 3}.
```

The product is strictly less than `2^E` for

```text
E = E_0 + 4 L - 3 = 2 g L + 4 g + 5 L - 3 + 2 K p - p^2.
```

Clear the eighths of `E + C p`. The four pieces scale as
`8 · 2 g L = 16 g L ≤ p`, `8 · 4 g = 2 · 16 g ≤ 2 p`,
`8 · 5 L = 5 · 8 L ≤ 5 p`, and `8 (2 K + C) p ≤ 4 p^2` once
`p ≥ 4 K + 2 C`, because `8(2 K + C) = 4(4 K + 2 C)`. The constant `-3`
contributes `-24`. Their sum is at most

```text
-4(p^2 - 2 p + 6).
```

The coefficients of `p` are `1 + 2 + 5 = 8`, which cancels the `-8 p` inside
four times the polynomial, and the `4 p^2` from the linear gate cancels four
times `p^2`. At `p = 2` the polynomial equals 6, and the step to the next
integer is `2 p - 1`. It is therefore at least 6, so eight times `E + C p`
is at most `-24`. The exponent `E` is at most `-C p - 3`, and the monomial
is strictly less than `2^{-C p}`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so `p/(32 log2 p) ≤ p/(16 L)` and the gate holds eventually.
Every fixed `K` and `C` then satisfy `p ≥ 4 K + 2 C` as well.

At `g = p^2` the monomial equals `g (9 p^2)^g exp(-p^2) · p^4 / 9`. Here
`(9 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `9 p^2 ≥ 36 > 4` and `e < 4`,
while `p^4 / 9 > 1` because `p^4 ≥ 16 > 9`. The product is greater than 1,
which is not below `2^{-C p}`.

## Not covered

- A proof that each section inverse is at most `9 p^2`, or that each section
  error is less than `p^6 exp(-p^2)`. This comparison starts from both.
- Replacing any inverse ceiling by the approximant norm
  `9 p^2 + p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-fold --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-fold
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T01:52:41Z and was
still that commit.

Overlap snapshot: open PRs fetched 2026-10-22T01:53:32Z (349 records) and
discussions fetched 2026-10-22T01:54:16Z (3373 records). A search for
`p^4 / 9`, `4 L - 3` and `(9 p^2)^{g-1}` returned this draft and the #4495
handoff, which leaves the telescoping factor open. A search miss is not a
novelty certificate. #4495 is the predecessor monomial. HALO is the written
error.

## Open next questions

1. **Does the approximant base `9 p^2 + p^6 exp(-p^2)` stay inside this
   budget?** The first step is to show `p^6 exp(-p^2) < 1/2` for every
   integer `p ≥ 64`, and then compare `9 p^2 + 1` with `16 p^2`.

## Credit

- The four-bit exponent `L + 4 g + 2 g L + 2 K p - p^2` is #4495's.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The telescoping shape with coefficient 10 is #4485. This package is the
  coefficient-9 monomial.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
