# A sharp call-budget bound for the hidden windows in PR6049

This resolves a restricted version of the fixed-budget question stated in
[PR6049](https://github.com/CrocSwap/integer-mult-bounds/pull/6049): its minimal
power-of-two rank alphabet. The proof also permits irrational interior roots.
It does not resolve the question for arbitrary rank alphabets or larger support.

## Statement and normalization

Fix an integer h >= 1. Let A_j and B_j be nonnegative **integers**, indexed by
j=0,...,2h+2, representing paid calls of rank 2^j. Suppose each profile contains
at most N calls, for a positive integer budget N. Put

    Q(x) = sum_j (B_j - A_j) x^j,
    F(p) = Q(2^p).

Assume F has a zero of multiplicity at least h at each of p=0 and p=1, and
two distinct interior zeros alpha < beta in (0,1), with F positive between
them (the losing window for B relative to A). Then, writing w=beta-alpha,

    w > 2 * 6^h / (N * ln(2)).                         (1)

For h=1 the ranks are {1,2,4,8,16}, and the numerator is 12. The constant
2*6^h/ln(2) in a bound of the form w > constant/N is asymptotically optimal.
This is an infimum over all eligible budgets and profiles. A stronger discrete
bound below proves exact optimality at an infinite sequence of budgets, but
we do not give a closed formula for the exact optimum at every finite N.

The budget N is **per profile**, including any common paid calls. The endpoint
condition already implies equal counts and equal rank mass, so the combined
two-profile count is T=2N_actual. With a combined-count budget T_max, (1)
becomes w > 4*6^h/(T_max*ln(2)). Using N for the sum of both profiles would
lose a factor of two. Replacing p by the saving coordinate C=1-p preserves w.

## Integer quadratic reduction

The substitution x=2^p is analytic with nonzero derivative, so it preserves
zero multiplicities at x=1 and x=2. Let r=2^alpha and s=2^beta. The nonzero
polynomial Q has degree at most 2h+2, and already has at least 2h+2 roots
counted with multiplicity: h each at 1 and 2, and one each at r and s.
Thus its degree is exactly 2h+2, its endpoint multiplicities are exactly h,
and its two interior roots are simple. Division by the monic integer factors
(x-1)^h and (x-2)^h leaves an integer quadratic. Choose its orientation as

    Q(x) = epsilon * (x-1)^h * (x-2)^h * R(x),
    R(x) = a*x^2 + b*x + c = a*(x-r)*(x-s),  a > 0,
    epsilon = (-1)^(h+1),     1 < r < s < 2.

The stated epsilon follows from positivity of Q on (r,s). All other signs
are then forced: Q is negative on (1,r) and (s,2). The discriminant

    Delta = b^2 - 4*a*c = a^2*(s-r)^2

is a positive integer, hence Delta >= 1. Rational roots are not required.

## Recovering the count from the coefficients

Every root of Q is positive. Expanding its product of real linear factors
therefore yields alternating, strictly nonzero coefficients. In particular,
all 2h+3 ranks occur in the difference, even though the premise only restricted
the allowed alphabet. It follows that

    sum_j |q_j| = |Q(-1)|
                 = 6^h * a*(1+r)*(1+s)
                 = 6^h * (a-b+c),        q_j = B_j-A_j.

Because Q(1)=0, its positive and negative coefficient sums agree. Write their
common value as W. This is the number of calls on either side after cancelling
calls shared by the profiles:

    W = (6^h/2) * a*(1+r)*(1+s) = (6^h/2)*(a-b+c),
    sum A_j = sum B_j = W + sum_j min(A_j,B_j) <= N.     (2)

This cancellation identity is why common padding cannot evade the bound.
No rank mass, productive target or compiler charge is substituted for W.

## Width inequality

For every x>1,

    1/x - 4/(1+x)^2 = (x-1)^2 / [x*(1+x)^2] > 0.

Integrating from r to s gives the strict inequality

    ln(s/r) > 4*(s-r) / [(1+r)*(1+s)].                 (3)

Multiplying (3) by (2) proves the stronger discriminant-sensitive statement

    W * ln(s/r) > 2*6^h * a*(s-r)
                 = 2*6^h * sqrt(Delta).

Consequently

    w > 2*6^h*sqrt(Delta) / [W*ln(2)]
      >= 2*6^h / [N*ln(2)],

as claimed. The proof is uniform in h and N. The finite checker does not
supply or replace the integration, degree-counting or limiting arguments.

## Sharpness of the universal constant

For any integer n>=3 take

    r_n = (n+1)/n,       s_n = n/(n-1),
    R_n(x) = (n*x-(n+1))*((n-1)*x-n)
           = n*(n-1)*x^2 - (2*n^2-1)*x + n*(n+1).

These roots lie strictly between 1 and 2, and Delta=1. Form Q with the
endpoint factors and orientation above, and use its positive and negative
coefficients as the disjoint integer profiles. They satisfy every premise,
with

    N = W_h(n) = (6^h/2)*(4*n^2-1),
    w_n = log_2(n^2/(n^2-1)).

For x>0, ln(1+x)<x. Together with the strict proved lower bound, this yields
the completely explicit squeeze

    1 < W_h(n)*w_n*ln(2)/(2*6^h)
      < (4*n^2-1)/(4*(n^2-1))
       = 1 + 3/[4*(n^2-1)].

Thus the normalized product tends to 1. Any proposed larger universal
constant fails for a sufficiently large n. The widths tend to zero as
Theta(1/N), while both endpoints tend to p=0. This does not conflict with
PR6049's unbounded-budget construction of a window in any prescribed gap.

An arithmetic common productive target can be chosen as in PR6049: equal
rank mass M exceeds the largest used paid rank, since each coefficient side
has at least two positive terms and one side contains that largest rank.
This is only an arithmetic invoice; it is no claim of a physical supplier.

## A stronger discrete bound and exact attainment at selected budgets

Independent review supplied a second derivation that improves the finite-budget
statement. Define the integers

    S = 6^h/2,   D = a-b+c = W/S,   z = -b,   k = R(1) = a+b+c.

Since both roots exceed 1, k is a positive integer. Thus

    D = 2*z+k,   k>=1,
    z <= Z = floor((floor(N/S)-1)/2).

The positive roots imply z>sqrt(Delta)>=1, so Z>1 for every eligible input.
The root ratio is

    s/r = (z+sqrt(Delta))/(z-sqrt(Delta)).

For positive denominators this ratio increases with sqrt(Delta) and decreases
with z. Hence

    w >= log_2((Z+1)/(Z-1)).                            (4)

Equivalently, the ratio comparison follows by positive cross multiplication
from Z*sqrt(Delta)>=z, whose square is the exact integer comparison
Z^2*Delta>=z^2. No numerical logarithm is needed to certify that comparison.

For the family above, k=1, Delta=1, N=S*(4*n^2-1), and Z=z=2*n^2-1.
Equality holds in (4). Therefore that family **exactly minimizes width among
all eligible profiles with at most S*(4*n^2-1) calls per side**, including
those with irrational roots or common padding. This establishes exact
finite-budget optima at those budgets, not just asymptotic sharpness.

The family need not remain optimal between those budgets. At h=1,N=120,
R=6*x^2-19*x+15 has roots 3/2 and 5/3, W=120, and width log_2(10/9),
less than the n=3 family's log_2(9/8). It also attains (4), with Z=19.
For other budgets the discrete bound need not be attained; this handoff makes
no general attainability claim.

The identity ln(s/r)=2*atanh(sqrt(Delta)/z)>2*sqrt(Delta)/z also proves
the strictly stronger continuous estimate

    w > 2*6^h / [(W-S)*ln(2)]
      >= 2*6^h / [(N-S)*ln(2)].                        (5)

All denominators here are positive for eligible profiles. The elementary
integral proof of (1) remains a separate cross-check of the normalization.

## Exact bounded search at N=1000

For h=1, write b=-z. Every eligible quadratic obeys

    1 <= a < N/12,     2*a < z < 4*a,
    max(z-a+1,2*z-4*a+1) <= c
        <= min(floor((z^2-1)/(4*a)), floor(N/3)-a-z).

These inequalities are both necessary and sufficient: they respectively
place the vertex inside (1,2), make the endpoint values positive, make the
minimum negative, and impose W=3*(a+z+c)<=N. They give a finite, exhaustive
enumeration, not a random search. Since

    w = log_2((1+sqrt(Delta/z^2))/(1-sqrt(Delta/z^2))),

minimizing width is exactly equivalent to minimizing the rational Delta/z^2.
The checker enumerates all 8,158 quadratics with N=1000, including 899 rational
and 7,259 irrational root pairs. Its exact minimum is 1/25921=1/161^2, giving
width log_2(81/80). There are two minimizing oriented quadratics:

    60*x^2 - 161*x + 108,   W=987,
    72*x^2 - 161*x + 90,    W=969.

Both have Delta=1. Common padding is not counted as a new quadratic. This is
a finite computation corroborated by a separate coefficient-simplex census;
it does not furnish a closed formula for every N.

## A rational mesh consequence, with its exact scope

The strict convexity of 1/x gives the composite trapezoidal upper bound

    ln(2) < (1/4)*(1/2 + 4/5 + 2/3 + 4/7 + 1/4)
          = 1171/1680 < 7/10.

Therefore every window covered by the theorem has

    w > 20*6^h/(7*N).

A uniform grid {k/m: 0<=k<=m} with

    m = ceil(7*N/(20*6^h))

has maximum gap at most this lower bound and must contain a grid point
strictly inside any such window. This explains how a known integer call
budget changes the fixed-grid obstruction in this specific class. It does
not certify arbitrary exponential sums, a larger rank alphabet, a different
zero pattern, or any physical supplier. The underlying quadratic can also
be analyzed directly; this is a consequence for sampling, not a claim that
sampling is the best algorithm.

## Dependencies, credit, and uncertainty

The project-specific starting point is zxv's PR6049 at commit
2646b6d67ceb74b9868e632f3a27312d8be62a0e, including its explicit open
fixed-budget question. That work credits Nick Petalas's PR5174 threshold
construction and Ali Romman's root-budget work. The polynomial-to-profile
construction, endpoint multiplicity framework and minimal-support result
belong to those predecessors. Integer discriminants, alternating
coefficients of positive-root polynomials, the logarithmic integral and
adjacent rational fractions are classical tools.

The contribution here is the stated sharp budget-width inequality for this
alphabet, its integer-quadratic extension and explicit sharpness family.
No global novelty claim is made. This is a focused follow-up to PR6049's
explicit fixed-budget question. The exact optimum at general finite N, beyond
the attained cases and bounded census above, and the arbitrary-rank problem
remain open here. The independent AI review contributed the stronger discrete
argument (4) and shifted continuous argument (5). This proof and its checks
were produced with substantial OpenAI Codex assistance, including GPT-6 Astra
and separate AI review. Neither independent human review nor proof-assistant
verification is claimed. The included scope counterexamples delimit, rather
than enlarge, the hypotheses of the main theorem.
