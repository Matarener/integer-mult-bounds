# The published weight error lowers four halo exponents inside one cell

**Claim type:** conditional exponent arithmetic for one within-cell block.
**No new κ.** The ideal gaps stay hypotheses. The selected record remains
`23/10000`.

## Question

#4451 showed that the published absolute weight error is a relative error
below `δ = 2^{2-32760p}`, which is stronger than `1/(16p^2)`. Do the
exponents 12, 26, 28, 28 and 6 still apply inside one cell, and is
`16p^2-1` still the inverse ceiling?

## Lemma

Let `p ≥ 2` be an integer and let `W` be an integer at most `p-1`. Assume
each ideal row off-sum and each ideal column off-sum is at most
`1 - 1/(8p^2)`. Inside the cell, assume `0 ≤ Ghat ≤ G` and
`a - 4η < ahat ≤ a` whenever `a > 2^{-8p}`, with `P = 32768p` and
`η = 2^{-P}`.

Let `D = 2^{32760 p}` and

```text
U = 8 p^2 (D - 4) / (D - 32 p^2).
```

Then both rounded off-sums are strictly below `(1 - 1/(8p^2)) / (1 - δ)`,
every absolute row sum and column sum is strictly below 2, and the Neumann
bounds on `||A^{-1}||_1` and `||A^{-1}||_∞` are strictly less than `U`. In
particular `8 p^2 < U < p^6` and `U < 16 p^2 - 1`. At `p = 2`, `U > 32 = p^5`.

For this block the polynomial

```text
P = p^{-11} sum_{j < p^{24}} Q^j A^*,    Q = I - p^{-11} A^* A,
```

satisfies `||P - A^{-1}||_2 < p^6 exp(-p^2)`. Its bandwidth is at most
`(2 p^{24} - 1) W < p^{26}`, and the looser count `(2 p^{24} + 1) W` has
the same ceiling. A row at distance `p^{26}` from a section edge agrees
with the block row.

So 12, 26, 28, 28 and 6 still apply. The normalizer 6 remains the smallest
uniform integer with that role. The other four are no longer smallest:
11, 24, 26 and 26 replace them. The value `16p^2-1` still upper-bounds the
inverse, and it is strictly larger than `U`.

## Proof

The denominator repair gives `a / ahat < 1/(1-δ)` with
`δ = 4/D = 2^{2-32760p}`, because `4η < 2^{-8p}` is the exponent identity
`32768 - 8 = 32760`. A downward kernel does not increase the entry. An
ideal off-sum at most `1 - 1/(8p^2)` therefore rounds to an off-sum
strictly below

```text
(1 - 1/(8p^2)) / (1 - δ) = (D / (D - 4)) (1 - 1/(8p^2)).
```

The complementary gap is strictly larger than `(1/(8p^2) - δ) / (1 - δ)`,
so the Neumann bound is strictly less than `U`. Since `D > 32 p^2`, the
rounded off-sum is also strictly below 1, and both matrix norms that enter
the 2-norm comparison are strictly below 2.

For every integer `p ≥ 2`, `2^{2p} ≥ p^2 + 1`. The base is `16 ≥ 5`. The
step is `4(p^2 + 1) - (p + 1)^2 = 3p^2 - 2p + 3`, and after `p = 2 + t`
every coefficient of that quadratic is positive. Also `2p + 6 ≤ 32760 p`:
at `p = 2` the numbers are `10 ≤ 65520`, and the slack increases by
`32758`. Therefore `D ≥ 2^{2p+6} = 64 · 2^{2p} ≥ 64(p^2 + 1)`.

Clearing the positive denominator shows `U > 8 p^2` exactly when
`32 p^2 > 4`. At `p = 2` that lower bound is `32 = p^5`, so `U > p^5` and
`U^2 > (8p^2)^2 = p^{10}`. The same clearing gives `U < p^6` once
`32(p^6 - 1) < D(p^4 - 8)`. At `p = 2` this is `2016 < 8 D` with
`D ≥ 2^{16}`. For `p ≥ 3`, the comparison
`64(p^2 + 1)(p^4 - 8) - 32(p^6 - 1)` equals `32(p^6 + 2p^4 - 16p^2 - 15)`.
After `p = 3 + t` every coefficient is positive, and `p^4 ≥ 81 > 16`.

The looser multiple `V = 8 p^2 D / (D - 32 p^2)` satisfies `U < V`. Then
`V^2 < p^{11}` once `64 D^2 < p^7 (D - 32 p^2)^2`. At `p = 2` this is
`D^2 < 2(D - 128)^2`, and `D^2 - 512 D + 32768` is positive for
`D ≥ 2^{16}` because `2^{32} > 2^{25}`. For `p ≥ 3`, `32 p^2/D < 1/2`, so
the squared factor exceeds `1/4` and `p^7/4 ≥ 2187/4 > 64`. Thus
`U^2 < p^{11}`. The eigenvalues of `A^* A` are strictly larger than
`p^{-11}` and strictly smaller than `4`. Since `4 < p^{11}`, they are
strictly smaller than `p^{11}`. The matrix `Q = I - p^{-11} A^* A` has
spectrum in `[0, 1 - p^{-22})`. The length `p^{24}` contributes `p^2`.
The length `p^{23}` contributes only `p`. The scalar step is strict
because `1/2! < 1`.

The bandwidth identity is

```text
p^{26} - (2 p^{24} - 1)(p - 1) = p^{24} ((p - 1)^2 + 1) + p - 1 > 0.
```

At `p = 2` the loose radius `(2 p^{24} + 1) W` equals `p^{25} + 1`. For
every integer `p ≥ 3`,
`(2 p^{24} - 1)(p - 1) - p^{25} = p^{24}(p - 2) - (p - 1)`, and
`p^2 - (p - 1) = p^2 - p + 1 > 0`, so the sharp radius exceeds `p^{25}`.
Exponent 25 is not a uniform ceiling. Exponent 26 is, for the bandwidth
and for the agreement distance.

Finally `V < 16 p^2 - 1`. The cleared difference
`2(8p^2 - 1)(p^2 + 1) - p^2(16p^2 - 1)` equals `15p^2 - 2`, which is
positive for every integer `p ≥ 2`. Combined with `D ≥ 64(p^2 + 1)`, this
is `(8p^2 - 1) D > 32 p^2 (16p^2 - 1)`. At `p = 2` the same comparison is
`31 D > 8064`. The older ceiling remains legal and is strictly coarser
than `U`.

| Role | Under `1/(16p^2)` | Under `δ` | Smallest |
| --- | ---: | ---: | --- |
| Spectral endpoint | 12 | 11 | 10 fails at `p=2` |
| Series length | 26 | 24 | 23 fails at `p=2` |
| Bandwidth | 28 | 26 | 25 fails |
| Agreement distance | 28 | 26 | 25 fails |
| Normalizer | 6 | 6 | 5 fails at `p=2` |

## Not covered

- Across-cell entries. #4449 gives `0 ≤ H ≤ n` for those entries. This
  package does not move the global reference.
- A proof that the ideal gaps exceed `1/(8p^2)` for every prime.
- The core exponent 400. It still dominates an agreement distance of 26.
- Any new κ. The #4100 notes keep 20, 42, 45, 48 and 100.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-delta-exponents --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-delta-exponents
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-21, using the snapshot fetched at 21:26 UTC and a
later look at the newest handoff comments and open pull requests, matched
this draft, PR #4451, and an unrelated digit string in
`research/capped-fusion-t74-k554`. It did not find another assignment of
11, 24, 26, 26 and 6. #4451 is the relative-error comparison. #4439 is the
coarser budget `1/(16p^2)`. A search miss is not a novelty certificate.

## Open next questions

1. **Do 11, 24, 26, 26 and 6 survive across a cell?** #4449 puts each
   across-cell entry in `[0, n]`, with absolute error below `4η`. The
   within-cell factor is now `1/(1-δ)`. The first step is the same column
   split as #4442, with `δ` in place of `1/(16p^2)`.

## Credit

- HALO's locality witness and its written exponents are #4100's.
- The sharp radius `(2J-1)W` is Nick Petalas's halo audit, PR #4217.
- The in-cell ideal column gap is Ryanson Jonathan's #4402.
- The relative budget `1/(16p^2)` is #4438. The coarser exponents are #4439.
- The published error `δ = 2^{2-32760p}` is #4451.
- The across-cell repair `0 ≤ H ≤ n` is Mihir S's #4449.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
