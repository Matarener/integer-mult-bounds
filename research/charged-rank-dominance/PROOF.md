# A sufficient paid replacement theorem for finite rank moments

Let `o_r,n_r` be nonnegative integer counts supported on ranks `1,…,T`,
with `T ≥ 2`. Set `d_r = n_r − o_r` and

    C_k = Σ_r d_r min(r,k),       0 ≤ k ≤ T.

Assume equal rank mass (`C_T = 0`) and `C_k ≤ 0` for every k. For any
exact rational interval `0 < ℓ ≤ u < 1`, define the entirely rational credit

    L = (−C_1) · 4ℓ/(3 + 2ℓ)
        + Σ_{k=2}^{T−1} (−C_k) · ℓ(1−u)/((k+1)(1+uk)).

**Theorem 1 (uniform quantitative replacement).** For every real
`a ∈ [ℓ,u]`,

    Σ_r o_r r^(1−a) − Σ_r n_r r^(1−a) ≥ L.

The capped-mass order is the retained predecessor theorem, not a new
majorization mechanism. The contribution here is its explicit rational
positive-cost budget, uniform on a saving interval.

## Discrete identity and proof of Theorem 1

For `f(0)=0`, put `θ_k = 2f(k)−f(k−1)−f(k+1)`. Direct subtraction of
successive slopes, or collecting the coefficient of each `f(r)`, gives

    f(r) = r(f(T)−f(T−1)) + Σ_{k=1}^{T−1} min(r,k) θ_k.

Multiply by d_r and sum. The linear term vanishes because `Σ r d_r=0`.
Consequently the old-minus-new bill is `Σ_k (−C_k)θ_k`.
This is the exact finite identity already used in `ranked-pair-verification`.

Take `f(x)=x^(1−a)`, with `f(0)=0`. At k = 1,

    θ_1 = 2(1−exp(−a log 2)) ≥ 4a/(3+2a) ≥ 4ℓ/(3+2ℓ).

Indeed `exp(x) ≥ 1+x` gives `1−exp(−x) ≥ x/(1+x)` for x ≥ 0.
Also `log 2 ≥ 2/3`, from the positive atanh series with argument 1/3.
The map `x/(1+x)` is increasing, as is `4a/(3+2a)`, proving the bound.

For each k ≥ 2, two applications of the fundamental theorem of calculus give

    θ_k = a(1−a) ∫_{−1}^1 (1−|t|)(k+t)^(−1−a) dt.

There is no singularity here: `k+t ≥ 1`. Throughout this integral,

    (k+t)^(1+a) ≤ (k+1)^(1+a)
                    ≤ (k+1)(1+ak) ≤ (k+1)(1+uk).

The middle inequality is the concave tangent inequality
`x^a ≤ 1+a(x−1)` at x = 1 for 0 < a < 1.
The triangular kernel integrates to 1, and
`a(1−a) ≥ ℓ(1−u)`. Thus

    θ_k ≥ ℓ(1−u)/((k+1)(1+uk)).

Every coefficient `−C_k` is nonnegative, so multiplying and summing these
bounds proves Theorem 1. Empty sums, including T = 2, cause no exception.

## Positive physical charges and normalization

**Theorem 2 (sufficient paid admission transfer).** Let `e_r` be any finite
nonnegative integer overhead histogram on positive integer ranks, let
`Q = Σ_r r e_r`, and assume `Q < L`. For any unchanged positive dimension
m, positive normalizer W, and any common additional cost H(a), define

    M_old(a) = H(a) + (1/W) Σ_r o_r (r/m)^(1−a),
    M_paid(a) = H(a) + (1/W) Σ_r (n_r+e_r)(r/m)^(1−a).

Then `M_paid(a) < M_old(a)` for every a ∈ [ℓ,u]. In particular, wherever
`M_old(a) < 1`, the fully charged new moment is also strictly below 1.
For legal recursive children separately require every used rank < m and all
applicable compiler/halving/physical hypotheses; this inequality does not prove
them.

Proof: since integer r ≥ 1 and 0 < 1−a < 1, `r^(1−a) ≤ r`. Thus the raw
overhead bill is at most Q. Theorem 1 yields raw net saving at least L−Q > 0.
Normalize by the positive factor `m^(a−1)/W` and add H(a). This proves the
assertions without any sign condition on H. More generally any independently
proved uniform raw overhead upper bound Q can replace rank mass; it must be a
bound for the actual added costs, not an optimistic omitted invoice.

**Corollary 3 (batch and paid-rank budget).** N disjoint copies with otherwise
unchanged costs can pay any aggregate positive-rank overhead of rank mass
`Q < N L`. This follows by summing Theorem 1 before paying the overhead.
For an integer budget the largest universally certified strict rank mass is
`ceil(NL)−1`. It need not be achievable by a particular physical implementation.
The theorem provides a sufficient acceptance rule, not a necessary condition:
a rejected charge may still be affordable by a sharper argument.

## Exact source-bound calibration

Using the literal old/ranked receipt pairs retained on canonical main, at
`ℓ = 17/10000` and `u = 18/10000`, the certificate computes:

| historical pair | rational credit L, approximately | certified added rank-1 children |
| --- | ---: | ---: |
| h = 23 | 1.7941489099235164 | 1 |
| h = 25 | 3.590143033771788 | 3 |

The exact fractions and every C_k and curvature lower bound are in
`RESULT.json`; the decimals above are presentation only. These strict paid
comparisons hold simultaneously throughout the displayed saving interval.
The interval is a pricing interval, not an assertion that these historical
complete suppliers admit those savings. No new word or physical routing is
constructed, and no current κ improvement follows just from this calibration.

The proof is informal mathematics. The exact finite identities and fractions
are replayed by Python; no Lean or independent human proof review is claimed.

## A directly actionable current-profile target

The exact complete T360 histogram published in PR3857 has 2,349,000 rank-2
children (the unchanged PR3815 construction). Consider a proposed transformation
replacing two rank-2 children by one rank-1 and one rank-3 child. It preserves
rank mass and has C_2 = −1 and every other C_k = 0. On the interval above,
the theorem assigns each such exchange the exact credit

    L_unit = 84847/150540000.

Therefore **1,775** such exchanges have credit
`1775 · 84847/150540000 > 1`, enough to pay one additional rank-1 child while
strictly improving the moment throughout that interval. The current profile
contains the required 3,550 rank-2 children. The proposed pre-overhead profile is
obtained by adding 1,775 rank-1 and rank-3 children and removing 3,550 rank-2
children; the additional paid child is separate. The exact complete signed
profile and quantitative certificate are regenerated in RESULT.json.

This is a sufficient numerical contract for an actual future implementation:
if it preserves m, W, the caller ABI and every common cost, and its complete
additional raw bill is at most one rank-1 child, its moment is strictly better.
It supplies no circuit identity, legal regrouping, physical realization or
stock/chronology proof. The new rank-3 child may have a different recursive
interface; algebraic relabelling cannot supply it. The point is to give that
implementation search an explicit fully charged acceptance target, not to
announce another supplier or a new κ. A richer paid overhead bill can be
submitted to the same sufficient test.
