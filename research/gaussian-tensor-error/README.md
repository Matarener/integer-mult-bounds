# The factor (10 p^2)^g is absorbed by the same gate

**Claim type:** an explicit absorption bound for one tensor error.
**No new κ.** The per-axis ceiling `10 p^2` stays a hypothesis. The selected
record remains `23/10000`.

## Question

#4482 leaves HALO's tensor error as `g p^{10 g} exp(-p^2)`. The open step is
to replace `p^{10}` by the inverse ceiling `10 p^2` and ask whether
`g log p = o(p)` still puts the error below `2^{-C p}` for every fixed `C`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (10 p^2)^g exp(K p - p^2) < 2^{-C p}.
```

Thus a global factor `exp(K p)` does not change the conclusion. Whenever
`g log p = o(p)`, every fixed pair `K, C` satisfies the gate for all large
`p`. The exponent 10 is not required for this absorption.

The gate is not optional for every `g`. At `g = p^2` the same substituted
error is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`: the values at 2, 3 and 4 are `2`, `6` and `24`,
and the step uses `k + 1 ≥ 2`. The tail of `e` is then at most the geometric
series of ratio `1/2`, so `e < 3 < 4` and `exp(K p) < 4^{K p} = 2^{2 K p}`
whenever `K p > 0`. At `K = 0` the factor is 1.

Since `10 < 16`, `(10 p^2)^g < 2^{4 g} p^{2 g}`. Also `p ≤ 2^L`, so
`p^{2 g} ≤ 2^{2 g L}`. The hypothesis `16 g L ≤ p` forces `g ≤ p ≤ 2^L`, and
therefore

```text
g (10 p^2)^g exp(K p - p^2) < 2^{L + 4 g + 2 g L + 2 K p - p^2}.
```

It remains to show that the exponent is strictly less than `-C p`. For every
integer `p ≥ 64`, `8 L ≤ p`. The base is `8 · 7 = 56 ≤ 64` at `p = 2^6`, and
`8 ≤ 64`. If `8(m + 1) ≤ 2^m`, then `8(m + 2) ≤ 2^m + 8 ≤ 2^{m + 1}`. On each
dyadic interval the largest ratio of `L` to `p` is at the left endpoint, so
`8 L ≤ p` for every integer `p ≥ 64`.

The gate `16 g L ≤ p` gives `2 g L ≤ p/8` and `4 g ≤ p/4`. The linear factor
obeys `(2 K + C) p ≤ p^2 / 2` exactly when `p ≥ 4 K + 2 C`, because
`2(2 K + C) = 4 K + 2 C`. Adding the four pieces produces at most

```text
p/8 + p/4 + p/8 + p^2/2 = p/2 + p^2/2.
```

The slack against `p^2` is `p(p - 1)/2`. At `p = 2` this is 1, and it
increases by `p` at the next integer. The exponent is therefore at most
`-C p - 1`.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so `p/(32 log2 p) ≤ p/(16 L)` and the gate `16 g L ≤ p`
holds eventually. Every fixed `K` and `C` then satisfy `p ≥ 4 K + 2 C` as
well.

At `g = p^2`, `(10 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `10 p^2 ≥ 40 > 4`
and `e < 4`. The substituted error is then greater than 1, which is not below
`2^{-C p}`.

## Not covered

- A proof that each section inverse is at most `10 p^2`. This comparison
  starts from that ceiling.
- The `g`-fold telescoping shape `g (10 p^2)^{g-1} p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-error --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-error
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T00:55:03Z, 336 records;
discussions fetched 2026-10-22T00:55:50Z, 3362 records) names this draft, the
locality audit that keeps `g p^{10 g} exp(-p^2)`, discussion comment 19078965
(a factor 2 in front of that product, not the `10 p^2` substitution),
`research/gaussian-expansion-headroom` (an unrelated tensor-error transport),
and #4481/#4482. No other package assigns the `(10 p^2)^g` absorption. A
search miss is not a novelty certificate. #4482 is the core-side comparison.
HALO is the error sentence.

## Open next questions

1. **Does the telescoping tensor bound stay absorbed?** A `g`-fold product
   of section inverses is at most `g (10 p^2)^{g-1}` times one section error
   `p^6 exp(-p^2)`, not necessarily `g (10 p^2)^g exp(-p^2)`. The first step
   is to put the extra factor `p^4 / 10` into the same power-of-two budget.

## Credit

- The tensor sentence and the gate `g log p = o(p)` are #4100's.
- The ceiling `10 p^2` is Ryanson Jonathan's #4462, as carried through #4481.
- The question is the open step of #4482.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
