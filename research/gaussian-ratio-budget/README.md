# The published weight error meets the 1/(16p^2) ratio budget

**Claim type:** a uniform relative-error comparison inside one cell.
**No new κ.** Across-cell rounding is outside this claim. The selected
record remains `23/10000`.

## Question

Downstream rounds each weight by a downward exponential routine with
absolute error below `4η`, where `P = 32768 p` and `η = 2^{-P}`, and it
records `2^{-8p} < a_j ≤ 1`. The within-cell entry is the ratio
`ahat_j Ghat_(j-l) / ahat_l`. Does that absolute error keep the ratio
inside the relative budget `ε ≤ 1/(16p^2)` for every integer `p ≥ 2`?

## Lemma

Let `p ≥ 2` be an integer. Suppose a true weight satisfies
`a > 2^{-8p}`, its repaired value satisfies `a - 4η < ahat ≤ a`, and a
repaired kernel coefficient satisfies `0 ≤ Ghat ≤ G`. Then each
within-cell off-diagonal entry obeys

```text
ahat_j Ghat / ahat_l < (a_j G / a_l) / (1 - δ),
```

where `δ = 2^{2 - 32760 p}`. This `δ` is strictly less than `1/(16p^2)`.
The factor `1/(1-δ)` is therefore strictly smaller than
`1/(1 - 1/(16p^2))`.

## Proof

The downward kernel bound and the downward numerator give

```text
ahat_j Ghat / ahat_l ≤ (a_j / ahat_l) G.
```

The denominator satisfies `ahat_l > a_l - 4η`. The room `4η < 2^{-8p}` is
the comparison `32760 p > 2`, since `32768 - 8 = 32760` and `4 = 2^2`.
Thus `ahat_l > 0` and

```text
a_l / ahat_l < 1 / (1 - 4η/a_l) < 1 / (1 - 4η/2^{-8p}) = 1/(1-δ).
```

The exponent of `δ` is `2 + 8p - 32768p = 2 - 32760p`.

It remains to prove `16 p^2 δ < 1`. First, `p^2 < 2^{2p}` for every
integer `p ≥ 2`. The base is `4 < 16`. If it holds at `p`, the next square
obeys `4(p+1)^2 ≤ 9 p^2`: the difference `4(p+1)^2 - 9p^2 = -5p^2 + 8p + 4`
is 0 at `p = 2`, and raising `p` by one changes it by `-10p + 3`, which is
already `-17` at `p = 2` and becomes more negative. Since `9 < 16`,

```text
(p+1)^2 ≤ (9/4) p^2 < 4 p^2 < 4 · 2^{2p} = 2^{2(p+1)}.
```

Second, `2p < 32760 p - 6` for every integer `p ≥ 2`. At `p = 2` the
slack is positive, and it increases by `32758` at each later integer.
Therefore `2^{2p} < 2^{32760 p - 6}`, and `p^2 < 2^{32760 p - 6}`.
Multiplying by the remaining power of two,

```text
16 p^2 δ < 16 · 2^{2-6} = 2^4 · 2^{-4} = 1.
```

The inequality is strict because both comparisons above are strict. At
`p = 2` the same exponent is concrete: `4 < 2^{65514}`.

So the relative weight error `ρ = 4η/a` satisfies `ρ < δ < 1/(16p^2)`,
which is the budget used for the within-cell factor `1/(1-ε)`. The gauge
audit's allowance `ε ≤ 1/2` is a larger number. At `p = 2`,
`1/2 > 1/64 = 1/(16·4)`.

## Not covered

- Across-cell entries. That rounding question is claimed separately.
- A proof that the ideal row and column gaps exceed `1/(8p^2)` for every
  prime. The ratio bound above takes the true entry `a_j G / a_l` as given.
- The halo exponents. Meeting `ε ≤ 1/(16p^2)` is the budget comparison,
  not a new assignment of 12, 26, 28 or 6.
- Any new κ, and any edit to the #4100 notes.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-ratio-budget --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-ratio-budget
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-21: discussion 4444 claims the across-cell two-ulp
repair left open by #4442. This package is the within-cell ratio under the
published absolute error. A search hit is not a novelty certificate.

## Open next questions

1. **Do 12, 26, 28, 28 and 6 now apply inside one cell for every integer
   `p ≥ 2`, with this `δ` in place of a separate `ε` hypothesis?** The
   ratio factor is strictly stronger than `1/(1 - 1/(16p^2))`. The ideal
   gaps `1/(8p^2)` are still the eventual statements in GAUSSIAN and
   #4402. The first step is to substitute `δ = 2^{2-32760p}` into the
   within-cell ceiling arithmetic.

## Credit

- The absolute error `4η`, the weight floor `2^{-8p}`, and the ratio entry
  are the phase-cell downstream note's.
- The budget `1/(16p^2)` is #4438. The within-cell exponents are #4439.
- The allowance `ε ≤ 1/2` is the capped-gauge audit's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
