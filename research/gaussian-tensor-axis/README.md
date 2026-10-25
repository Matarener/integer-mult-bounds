# One tensor axis is at most two section errors

**Claim type:** a telescoping identity with an explicit one-axis norm bound.
**No new κ.** The per-axis norm bounds stay hypotheses. The selected record
remains `23/10000`.

## Question

#4487 bounds the scalar monomial

```text
2 g (10 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(-p^2)
```

and asks whether the tensor difference is at most that monomial. The first
step is one axis of the product.

## Lemma

Let `g ≥ 1`, and let `B_i` and `C_i` be bounded operators on Hilbert spaces.
Write `ε = p^6 exp(-p^2)` for an integer `p ≥ 2`. Suppose that for every axis

```text
||B_i|| ≤ 10 p^2,
||C_i|| ≤ 10 p^2 + ε,
||B_i - C_i|| < 2 ε,
```

and that `||X ⊗ Y|| = ||X|| ||Y||`. Then

```text
⊗_i B_i - ⊗_i C_i = sum_{k=1}^g T_k,
```

where

```text
T_k = (⊗_{i<k} B_i) ⊗ (B_k - C_k) ⊗ (⊗_{i>k} C_i),
```

an empty product being the identity. Every slice satisfies

```text
||T_k|| < 2 (10 p^2 + ε)^{g-1} ε,
```

and the triangle inequality gives

```text
||⊗_i B_i - ⊗_i C_i|| < 2 g (10 p^2 + ε)^{g-1} ε.
```

The factor 2 is the sum of two section errors on the active axis. HALO's
`2g` rectangles are a volume partition, not this factor. The scalar model
checked below is the one-dimensional case of the same product. The gate that
puts the right-hand side below `2^{-C p}` is #4487; it is not re-proved here.

## Proof

For `g = 1` the identity is `B_1 - C_1 = T_1`. If it holds for `g - 1` factors,
then

```text
(⊗_{i<g} B_i) ⊗ B_g - (⊗_{i<g} C_i) ⊗ C_g
  = (⊗_{i<g} B_i) ⊗ (B_g - C_g)
    + ((⊗_{i<g} B_i) - (⊗_{i<g} C_i)) ⊗ C_g.
```

The second sum expands by the inductive hypothesis, and its slices are the
slices `T_k` for `k < g`. The first sum is `T_g`.

The norm hypothesis multiplies across a pure tensor, so

```text
||T_k|| = (∏_{i<k} ||B_i||) · ||B_k - C_k|| · (∏_{i>k} ||C_i||)
  < (10 p^2)^{k-1} (10 p^2 + ε)^{g-k} · 2 ε.
```

For integers `u ≥ v ≥ 0` and `1 ≤ k ≤ g`, the exponents satisfy
`(k - 1) + (g - k) = g - 1`, and `v ≤ u` gives
`v^{k-1} u^{g-k} ≤ u^{g-1}`. Apply this with `v = 10 p^2` and
`u = 10 p^2 + ε`. Each slice is strictly smaller than `2 u^{g-1} ε`. Adding
the `g` slices preserves the strict inequality.

The cap `||B_i - C_i|| < 2 ε` is the sum of two strict section errors. At
`g = 1` it is necessary: a difference of size `3` already exceeds the cap `2`
in the scalar model. The executable check uses the integer caps `10`, `11`
and `2` in place of `10 p^2`, `10 p^2 + ε` and `2 ε`.

## Not covered

- A proof that any axis inverse, approximant, or section error meets the
  three norm hypotheses.
- The comparison of the monomial with `2^{-C p}`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-axis --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-axis
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T01:21:17Z, 341 records;
discussions fetched 2026-10-22T01:22:02Z, 3366 records) names this draft, #4487
(the scalar monomial, which leaves the identification open), and the locality
audit. That audit already gives the telescoping shape with a factor 2 in
front of `p^{10}`. It does not use the ceiling `10 p^2` or the section error
`p^6 exp(-p^2)`. A search for "one axis" also hits unrelated BIT and
expansion notes. A search miss is not a novelty certificate. #4487 is the
scalar monomial. HALO is the tensor sentence.

## Open next questions

1. **Does one core axis meet the three norm hypotheses?** The telescope uses
   `||B_i|| ≤ 10 p^2`, `||C_i|| ≤ 10 p^2 + ε`, and `||B_i - C_i|| < 2 ε`.
   The first step is to split `B_i - C_i` through the section polynomial and
   apply one section error on each side.

## Credit

- The tensor sentence is #4100's.
- The shape of the telescoping sum, with a factor 2 in front of `p^{10}`, is
  the locality-witness audit.
- The ceiling `10 p^2` is Ryanson Jonathan's #4462, as carried through #4481.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The scalar monomial is #4487.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
