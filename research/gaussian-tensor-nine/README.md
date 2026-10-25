# The factor (9 p^2)^g is absorbed by the same four-bit gate

**Claim type:** an explicit absorption bound for one tensor error.
**No new κ.** The per-axis ceiling `9 p^2` stays a hypothesis. The selected
record remains `23/10000`.

## Question

#4493 shows that the within-cell formula is strictly below `9 p^2`, and asks
whether the #4484 gate still absorbs

```text
g (9 p^2)^g exp(K p - p^2).
```

That gate spends four bits because `10 < 16`. The first step is to put `9`
in place of `10` in the exponent `L + 4 g + 2 g L + 2 K p - p^2`, and to test
whether three bits fail because `9 > 8`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (9 p^2)^g exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. A global factor `exp(K p)`
does not change the conclusion. Whenever `g log p = o(p)`, every fixed pair
`K, C` satisfies the gate for all large `p`.

Four bits are enough because `9 < 16`. Three bits are not a majorant of this
shape: `9 > 8`, so

```text
(9 p^2)^g > 2^{3 g} p^{2 g}
```

for every integer `p ≥ 2` and `g ≥ 1`. A negative exponent written with `3`
in place of `4` does not repair that comparison.

The gate is not optional for every `g`. At `g = p^2` the same substituted
error is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`: the values at 2, 3 and 4 are `2`, `6` and `24`,
and the step uses `k + 1 ≥ 2`. The tail of `e` is then at most the geometric
series of ratio `1/2`, so `e < 3 < 4` and `exp(K p) < 4^{K p} = 2^{2 K p}`
whenever `K p > 0`. At `K = 0` the factor is 1.

Since `9 < 16`, `(9 p^2)^g < 2^{4 g} p^{2 g}`. Also `p ≤ 2^L`, so
`p^{2 g} ≤ 2^{2 g L}`. The hypothesis `16 g L ≤ p` forces `g < 2^L`, because
`L ≥ 1` and therefore `g ≤ p/(16 L) ≤ p/16`. Hence

```text
g (9 p^2)^g exp(K p - p^2) < 2^{L + 4 g + 2 g L + 2 K p - p^2}.
```

It remains to show that the exponent is strictly less than `-C p`. For every
integer `p ≥ 64`, `8 L ≤ p`. The base is `8 · 7 = 56 ≤ 64` at `p = 2^6`, and
`8 ≤ 64`. If `8(m + 1) ≤ 2^m`, then `8(m + 2) ≤ 2^m + 8 ≤ 2^{m + 1}`. On each
dyadic interval the largest ratio of `L` to `p` is at the left endpoint, so
`8 L ≤ p` for every integer `p ≥ 64`.

The gate `16 g L ≤ p` gives `2 g L ≤ p/8` and, with `L ≥ 1`, `4 g ≤ p/4`.
The linear factor obeys `(2 K + C) p ≤ p^2 / 2` exactly when
`p ≥ 4 K + 2 C`, because `2(2 K + C) = 4 K + 2 C`. Adding the four pieces
produces at most

```text
p/8 + p/4 + p/8 + p^2/2 = p/2 + p^2/2.
```

The slack against `p^2` is `p(p - 1)/2`. At `p = 2` this is 1, and it
increases by `p` at the next integer. The exponent is therefore at most
`-C p - 1`.

The three-bit comparison reverses. Since `9 > 8 = 2^3`,

```text
(9 p^2)^g > (8 p^2)^g = 2^{3 g} p^{2 g}.
```

At the legal point `p = 128`, `L = 7`, `g = 1`, both
`L + 4 g + 2 g L - p^2` and `L + 3 g + 2 g L - p^2` are negative, while
`9 p^2 > 8 p^2`. Negativity of the three-bit exponent is not an upper bound
for the monomial.

If `g log p = o(p)`, then `g log2 p ≤ p/32` for large `p`. For `p ≥ 3`,
`L ≤ 2 log2 p`, so `p/(32 log2 p) ≤ p/(16 L)` and the gate `16 g L ≤ p`
holds eventually. Every fixed `K` and `C` then satisfy `p ≥ 4 K + 2 C` as
well.

At `g = p^2`, `(9 p^2)^{p^2} > 4^{p^2} > exp(p^2)` because `9 p^2 ≥ 36 > 4`
and `e < 4`. The substituted error is then greater than 1, which is not below
`2^{-C p}`.

## Not covered

- A proof that each section inverse is at most `9 p^2`. This comparison
  starts from that ceiling.
- The telescoping monomial `g (9 p^2)^{g-1} p^6 exp(-p^2)`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T01:47:06Z and was
still that commit.

Overlap snapshot: open PRs fetched 2026-10-22T01:48:03Z (348 records) and
discussions fetched 2026-10-22T01:48:45Z (3371 records). A search for
`(9 p^2)^g`, `three bits` and `L + 4 g` returned this draft and the #4493
handoff, which leaves the absorption open, plus unrelated three-bit tape and
encoding notes. A search miss is not a novelty certificate. #4484 is the
four-bit gate. HALO is the written error.

## Open next questions

1. **Does the same gate absorb `g (9 p^2)^{g-1} p^6 exp(K p - p^2)`?** The
   extra factor against this package is `p^4 / 9`, because
   `g (9 p^2)^{g-1} p^6 = g (9 p^2)^g (p^4 / 9)`. The first step is to place
   that factor in the exponent as `4 L` and clear it against the same eighths.

## Credit

- The four-bit gate and the exponent `L + 4 g + 2 g L + 2 K p - p^2` are #4484's.
- The coefficient 9, and this question, are #4493's.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
