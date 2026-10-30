# Five ranks can hide a losing power window from any fixed finite grid

Equal call count and rank mass, a fixed five-rank support, and favorable signs
at every member of an arbitrarily large finite sample do not certify a favorable
power-moment comparison. There is a losing open interval between samples.
Five is the smallest possible support for a difference with this two-crossing
sign pattern and the two equalities. This is a scoped algebraic theorem,
with exact finite checks, not a supplier or new kappa.

The theorem extends [Nick Petalas](https://github.com/petalas)'s one-threshold
[PR #5174](https://github.com/CrocSwap/integer-mult-bounds/pull/5174) rank-exchange construction (pinned in SOURCES.json). The existing exact
[root-budget tool](../../docs/research/recursive-power-variation.md) already
handles multiple crossings; no defect in that tool is alleged. The new result
is the sharp fixed-support impossibility of replacing a complete certificate
by any fixed finite grid. The construction also matches any prescribed finite
number of endpoint derivatives, with a sharp larger support bound.

## Theorem and construction

Let S be any finite subset of (0,1). Let J be any nonempty open subinterval
of (0,1) avoiding S, and let h>=1 be an integer. There are two nonnegative
integer paid profiles A,B, whose combined support consists of exactly the ranks

```
1, 2, 4, ..., 2^(2h+2),
```

whose difference F(p)=sum_r (B_r-A_r) r^p has these properties:

1. F and its first h-1 derivatives vanish at both p=0 and p=1.
2. There are alpha<beta in J with F>0 on (alpha,beta) and F<0 everywhere
   else in (0,1), except for its two zeros alpha,beta.
3. Their count and rank mass agree. Each has paid ranks below a common
   productive target, so subtracting that same target changes none of the signs.
4. The 2h+3 nonzero ranks in the difference are minimal for this sign pattern
   and these endpoint multiplicities, among arbitrary distinct positive ranks.

Choose positive rationals u=a/b and v=c/d with
`1<u<v<2` and `[log_2 u, log_2 v]` contained in J. Such choices exist because
p -> 2^p is continuous and strictly increasing and the rationals are dense.
Expand the integer polynomial

```
Q(x) = (-1)^(h+1) (x-1)^h (x-2)^h (b*x-a) (d*x-c)
     = sum_(j=0)^(2h+2) q_j x^j.
```

At rank 2^j put max(-q_j,0) calls in A and max(q_j,0) calls in B. Then
`F(p)=Q(2^p)` exactly. For 1<x<2, the endpoint factors have sign (-1)^h.
The two rational factors have positive product outside (u,v) and negative
product inside. The prefactor therefore gives precisely the asserted signs.
The substitution has nonzero derivative, so endpoint zeros have multiplicity
exactly h and the two interior zeros are simple. Every root of Q is positive;
its coefficients alternate and no elementary symmetric coefficient vanishes.
Thus every one of the 2h+3 displayed ranks occurs in the difference.

In particular F(0)=0 gives equal counts, and F(1)=0 gives equal rank mass M.
Take H_M as the common productive target. Each profile has at least two
positive terms, and the side containing the largest rank has further positive
mass. Hence M exceeds every paid rank. The theorem supplies arithmetic
invoices, with no assertion of a common physical implementation.

### Sharp support bound

A nonzero sum of s exponentials with distinct real exponents has at most s-1
real zeros counted with multiplicity. Here is the needed elementary proof.
For s=1 it has none. Divide by the smallest exponential, which preserves zeros.
The derivative has at most s-1 exponential terms; by induction it has at most
s-2 zeros. Rolle's theorem, including repeated-zero multiplicities, gives at
least N-1 derivative zeros if the original has N zeros. Thus N<=s-1. Apply
this on a finite interval containing any proposed set of zeros; it proves the
same global bound. Zero coefficients are omitted first.

F has at least h zeros at each endpoint and two distinct interior zeros, so
`s-1 >= 2h+2`, or **s>=2h+3**. The construction attains equality. For h=1,
the fixed support is {1,2,4,8,16}, independently of sample count or gap width.
Large or narrowly placed samples can require large **multiplicities**; this
result does not hold under a separately fixed coefficient budget.

## Small explicit failed sampling construction

Take h=1,u=5/4,v=3/2. Then

```
Q(x) = 8*x^4 - 46*x^3 + 97*x^2 - 89*x + 30,
A = 89 H_2 + 46 H_8,
B = 30 H_1 + 97 H_4 + 8 H_16.
```

Both profiles have 135 calls and rank mass 546. Their difference is negative
at p=1/4 and 3/4 but positive at p=1/2. Exactly,
`F(1/2)=256-181*sqrt(2)>0`, since `256^2 > 2*181^2`.
Thus the sampled cheaper candidate is dearer inside the missed interval.
A multiplier saving C uses p=1-C, which just reverses interval order.

No finite sample set alone certifies a comparison on the entire interval;
a proved root budget, a sign enclosure on every cell, or a structural order
can do so. The selected source's exact interval checks are not replaced by
this example. No sampled native search is declared invalid merely because
it uses samples for discovery.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/hidden-power-windows
python3.12 -B scripts/check_research_commit.py --package research/hidden-power-windows
```

The standard-library verifier builds gap witnesses for every interior gap in
uniform grids with denominator 2..24, and narrow root brackets around p=319/320 (saving .003125).
It checks every grid sample using exact integer comparisons of factored
rational roots, reconstructs all integer coefficients, count/mass and endpoint
multiplicity, and verifies the hidden sign at an intervening rational exponent.
Exponent denominators are capped at 2,048 before integer powering; the first
authoring run exceeded its intended memory bound with a large denominator and
was terminated, then replaced by these bounded fixtures. Higher multiplicity
h=1..8 and independent expanded-polynomial interval checks
on the small explicit example are included. Reversed signs, wrong roots, missing
coefficients and false multiplicities are rejected. Normal and optimized modes
are registered and write no package files. The written proof is uniform in S,J,h;
the finite checks corroborate its implementation.

Base: canonical main 721c03822c421b7f7fcbb2598993b947c4d88419, revision 8,
refreshed on 2026-10-28 UTC. Full selected-supplier replay was not run. The
optional full-source-history check refuses this shallow repository; every pin
is at the immediate main-branch base. No full-history pass is claimed.

## Significance for researchers

Even a small rank alphabet with conservation laws can require an interval-wide
power certificate. This gives a sharp adversarial fixture for proposed search
screens and makes the missing hypothesis explicit: sample density alone is
insufficient when integer multiplicities are unbounded. It explains when the
power reduction in [PR #6047](https://github.com/CrocSwap/integer-mult-bounds/pull/6047) needs its ordered-spread premise.

## Open next questions

With a fixed maximum coefficient or total-call budget, how narrow can the hidden
window be? First bound the separation of two rational roots of this quadratic
interior factor at that budget, then compare general exponential sums. The
unbounded-multiplicity theorem provides no finite-budget lower bound.

Can a legal supplier realize a two-crossing exchange? Extract a source-bound
five-rank change with a complete common boundary and all fees. These synthetic
profiles supply no physical construction, restoration, compiler or outer admission.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Nick Petalas](https://github.com/petalas)'s rational-threshold construction
supplies the polynomial-to-invoice precursor. [Ali Romman](https://github.com/aliromman)
supplies the root-budget tool and its retained predecessors; the exponential
zero bound, Rolle argument and polynomial factorization are classical. The
sharp hidden-window formulation and endpoint-matching extension are the scoped
contribution. No independent human or proof-assistant review is claimed. Apache-2.0.
