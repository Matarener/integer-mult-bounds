# Higher-order exchanges that improve every rank power

## Exact universal statement

Let n ≥ 2 be an integer, x ≥ 1 and h ≥ 1 be integers, and let 0 < a < 1.
Define the signed profile on the n+1 ranks x,x+h,…,x+nh by

    d_(x+jh) = (−1)^j binomial(n,j),       0 ≤ j ≤ n.

Positive coefficients are children added; negative coefficients are children
removed. Then the change in raw recursive bill is strictly negative:

    Σ_{j=0}^n (−1)^j binomial(n,j) (x+jh)^(1−a) < 0.        (1)

The stencil preserves both child count and rank mass. It also annihilates every
polynomial of degree less than n. A finite nonempty sum of these stencils with
positive multiplicities again strictly improves the bill for every 0 < a < 1,
provided the resulting finite child counts are nonnegative. For unchanged
positive dimension m and positive live normalizer W, multiplying by
`m^(a−1)/W` proves the same strict comparison of normalized moments.
This is a sufficient profile theorem, not an implementation of the exchanges.

## Proof for every order

Write q = 1−a and f(t) = t^q for t > 0. The n-th derivative is

    f^(n)(t) = (−1)^(n−1) A_n(a) t^(−(n−1+a)),
    A_n(a) = a(1−a) ∏_{j=1}^{n−2}(a+j) > 0.

The product is empty for n = 2. Iterating the fundamental theorem of calculus,

    Δ_h^n f(x) = ∫_[0,h]^n f^(n)(x+t_1+…+t_n) dt_1…dt_n.

All evaluation points are positive. The negative of the signed bill in (1)
is therefore exactly

    S_n(x,h,a) = A_n(a) ∫_[0,h]^n
                  (x+t_1+…+t_n)^(−(n−1+a)) dt > 0.        (2)

The integrand and coefficient are strictly positive and the cube has positive
volume. This proves (1). The stencil sum on a polynomial is `(-1)^n Δ_h^n`
of that polynomial, hence zero for degree less than n; taking degrees 0 and 1
proves count and rank-mass conservation. Sum the strict inequalities for a
finite nonempty positive collection, then normalize by a positive factor.
No implicit gadget, rounding operation or physical implementation enters this
argument. The iterated finite-difference identity is classical; novelty is not
claimed for that identity or complete alternation of sublinear powers.

## A uniform rational credit that pays positive costs

Fix rational 0 < ℓ ≤ u < 1, a positive integer B, and n,x,h as above.
Let `c_s` be the coefficient of z^s in `(1+z+…+z^(B−1))^n`. Put

    A_* = ℓ(1−u) ∏_{j=1}^{n−2}(ℓ+j),
    R_s = x + (s+n)h/B,
    L_B = A_* (h/B)^n Σ_{s=0}^{n(B−1)}
                     c_s / (R_s^(n−1)(1+u(R_s−1))).        (3)

**Theorem (uniform paid replacement).** For every real a ∈ [ℓ,u],
`S_n(x,h,a) ≥ L_B > 0`. For any collection of these stencils with positive
integer multiplicities N_i, any complete additional positive-integer-rank
histogram e_r of rank mass Q = Σ r e_r satisfying

    Q < Σ_i N_i L_(B,i)

leaves the fully charged new moment strictly below the old moment throughout
[ℓ,u], at unchanged m,W and unchanged other costs. Wherever the old moment
is below 1, the fully charged new moment is also below 1. Legal recursion
separately requires all used ranks < m and all relevant halving/compiler rules.

Proof: partition each cube coordinate into B equal intervals. If the sum of
their zero-based indices is s, the sum argument is at most R_s, and there are
exactly c_s such cells. For a ∈ [ℓ,u], `A_n(a) ≥ A_*`. For any cell argument
t ≥ 1 with t ≤ R_s, the concave tangent bound at 1 gives

    t^(n−1+a) ≤ R_s^(n−1) R_s^a
                 ≤ R_s^(n−1)(1+a(R_s−1))
                 ≤ R_s^(n−1)(1+u(R_s−1)).

Thus each cell's integrand is at least the reciprocal in (3); multiplying by
the cell volume `(h/B)^n`, its coefficient and A_* proves the lower bound.
Every summand in (3) is positive, so the bound is strict above zero.
The extra raw bill is at most Q because `r^(1−a) ≤ r` for every integer r ≥ 1.
Subtract Q from the total certified saving and normalize, proving the paid rule.
Any independently proved uniform upper bound for the actual extra raw cost can
replace Q; omitted costs cannot.

The implementation computes c_s by polynomial convolution, with only
`n(B−1)+1` coefficients rather than enumerating B^n cells. The coefficient
sum is exactly B^n. For nested grids B,2B,4B,… the lower credits are
nondecreasing: each refined cell has an upper argument no larger than its
parent, and the rational lower-envelope function in (3) decreases with R.
This is a proof-preserving way to refine a difficult credit without pricing
an entire moment root. The theorem holds for every finite order and B; the
bounded implementation intentionally supports orders 2 through 12 and B ≤ 128.

## Why this adds coverage beyond concave order

For n = 3, x = h = 1, the stencil is

    3 children of rank 2 + 1 of rank 4
      → 1 child of rank 1 + 3 of rank 3.

Its capped sums `C_k = Σ d_r min(r,k)` for k = 1,…,4 are `(0,−1,1,0)`.
The positive C_3 means this move fails the all-concave sufficient test used by
`ranked-pair-verification` and PR3863. Indeed the concave function `min(r,3)`
gets strictly more expensive. In contrast every power `r^(1−a)`, 0 < a < 1,
strictly decreases by the third-derivative identity above. This establishes a
strict extension of that sufficient certificate domain, rather than merely
another estimate for a move it already accepts.

For n = 4 the move is

    4 children of rank 2 + 4 of rank 4
      → 1 child of rank 1 + 6 of rank 3 + 1 of rank 5.

Its capped sums are `(0,−1,2,−1,0)`. The same distinction applies. Both moves
preserve count and mass and use ranks already present in the current histogram.

## Source-bound current pricing targets

Using PR3857's retained complete PR3815 T360 histogram, ℓ = 17/10000,
u = 18/10000 and B = 16:

| order | raw saving per copy, certified approximately | copies that pay one additional rank-1 child | largest independent batch supported by source counts |
| --- | ---: | ---: | ---: |
| 3 | 0.0002856291624839168 | 3,502 | 330,480 |
| 4 | 0.0001408758746078832 | 7,099 | 82,620 |

All proof-relevant comparisons use the exact rational fractions in RESULT.json.
The source has 2,349,000 rank-2 and 330,480 rank-4 children, so both batches
pass the literal aggregate inventory test. These two examples are separate
comparisons against the original source, not simultaneously claimed batches.
Both certify a fully charged moment improvement *if* the displayed exchange is
implemented with that complete extra cost, the same normalizers and ABI.
The source counts do not establish operand compatibility, legal grouping,
chronology, stock, frames, dirty restoration, gathering or an actual circuit.
No new physical supplier, κ, selected-frontier change or full multiplication
theorem is claimed. The result supplies broader exact sufficient targets for
that implementation search. The proof is informal; Python replays finite
identities and rational budgets, not a Lean kernel proof.
