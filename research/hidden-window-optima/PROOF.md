# Exact minimum width at every normalized budget

Research draft, 2026-10-29. Substantial OpenAI Codex assistance.
Apache-2.0. This is a proposed mathematical proof, not a formal certification.

## Scope and inherited reduction

Fix integers h,N >= 1. Let A_j,B_j be nonnegative integers for
0 <= j <= 2h+2, with sum A_j <= N and sum B_j <= N. Put
F(p) = sum_j (B_j-A_j) 2^(jp). Require zeros of multiplicity at least h
at p=0,1, two distinct interior zeros alpha<beta, and F>0 between them.
The quantity to minimize is w=beta-alpha. N is the budget **per profile**,
including common paid padding, not the combined count of the two profiles.

Karnaugh33's PR6139 supplies the following reduction, which we also explain
so its applicability is explicit. Set x=2^p. Nonzero Q(x)=F(log_2 x) has
degree at most 2h+2; its required roots already account for that degree.
Division by the monic integer endpoint factors gives

    Q(x)=(-1)^(h+1)(x-1)^h(x-2)^h R(x),
    R(x)=a*x^2-z*x+c,  a,z,c positive integers,
    1<r<s<2,  Delta=z^2-4ac>0.

Every root of Q is positive, so its coefficients alternate strictly. Q(1)=0
makes its positive and negative coefficient sums equal. Each equals

    W=|Q(-1)|/2 = S*(a+z+c),  S=6^h/2.

These are the counts after cancelling common calls; every realization adds
the same nonnegative integer padding vector H to both coefficient parts.
It is allowed precisely when sum H <= N-W. Conversely every quadratic with
the displayed root conditions yields such profiles with the required signs.
Thus, with L=floor(N/S), feasible residuals are exactly

    a,z,c positive integers; D=a+z+c <= L;
    2a<z<4a; a-z+c>0; 4a-2z+c>0; Delta=z^2-4ac>0.       (A)

The strict vertex, endpoint and discriminant conditions in (A) are necessary
and sufficient for two distinct roots in (1,2). Width increases strictly with

    Delta/z^2,   w=log_2((z+sqrt(Delta))/(z-sqrt(Delta))). (B)

In particular, k=R(1)=a+c-z is a positive integer, D=2z+k and
z <= Z=floor((L-1)/2). These facts, the discriminant bound and the family
below are inherited from PR6139. PR6153 classifies equality in its lower bound
log_2((Z+1)/(Z-1)); it leaves the actual optimum at other budgets open.

## Theorem

1. If L<31, there is no eligible profile pair.
2. If 31<=L<=34, the unique oriented residual is (a,z,c)=(5,15,11).
   Its discriminant is 5 and the minimum width is
   log_2((15+sqrt(5))/(15-sqrt(5))).
3. For every L>=35, **every** width-minimizing residual has Delta=1.
   Let z_star be the largest odd z for which some positive integers a,c obey

       4ac=z^2-1,  a+z+c<=L,  2a<z-1,  z+1<4a.        (C)

   Then the exact minimum width is log_2((z_star+1)/(z_star-1)).
   All minimizing residuals are precisely all triples satisfying (C) with
   z=z_star. Every minimizing profile is their signed-coefficient construction
   with any identical padding of total at most N-S*(a+z+c).

The theorem is uniform in h,N. The search characterization of z_star is exact;
it is not claimed to be an elementary closed expression in L.

## Small budgets, by endpoint coordinates

A separate adversarial AI review supplied a direct algebraic argument, removing
any dependence of this base case on a finite table. Define

    k=R(1)=a-z+c,  ell=R(2)=4a-2z+c,  v=3z-4a-2c.

Then the exact identity is

    R(x)=k(2-x)^2-v(x-1)(2-x)+ell(x-1)^2.

The increasing substitution y=(x-1)/(2-x) maps (1,2) bijectively onto
(0,infinity), with x=(1+2y)/(1+y). Consequently

    (1+y)^2 R((1+2y)/(1+y)) = ell*y^2-v*y+k.

The two roots of R are distinct and strictly interior precisely when
k,ell,v are positive integers and v^2>4*k*ell. Necessity follows from
positive endpoint values, and from the positive sum and product of the two
positive y roots. Sufficiency follows from the same sum/product conditions
and the strictly positive discriminant. The inverse integer map is

    a=k+v+ell,  z=4k+3v+2ell,  c=4k+2v+ell,
    D=a+z+c=9k+6v+4ell.

Since k,ell>=1, the discriminant condition forces v>=3. Hence D>=31,
with equality only at (k,v,ell)=(1,3,1). Any different positive integer
triple satisfying these lower bounds increases D by at least four. Thus
there are no eligible residuals below 31, and (a,z,c)=(5,15,11) is the
only one through 34. It has Delta=5 and both roots strictly in (1,2).
This proves both small-budget statements without a computational assumption.
The polynomial itself already appears as a semantic control in PR6153's
verifier; its existence is predecessor evidence, not a new discovery here.
The new statement is the exact infeasibility/uniqueness threshold.

The literal coefficient and endpoint-coordinate censuses independently
corroborate this argument. The exception prevents extending the rational-root
optimizer conclusion to every feasible budget.

## Why discriminant one always wins above the threshold

For L>=35 choose n=floor(sqrt((L+1)/4)), equivalently the largest integer n
with 4n^2-1<=L. Then n>=3. The PR6139 family

    (a_0,z_0,c_0)=(n(n-1), 2n^2-1, n(n+1))

has D_0=4n^2-1<=L, Delta_0=1 and roots (n+1)/n, n/(n-1) in (1,2).
Maximality of n implies L<=4(n+1)^2-2 and hence

    Z <= 2n^2+4n,
    2z_0-Z >= 2n^2-4n-2 > 0  (n>=3).                 (D)

An integer quadratic discriminant is 0 or 1 modulo 4. Consequently any
positive discriminant different from one is at least four. Every such
eligible quadratic satisfies

    Delta/z^2 >= 4/Z^2 > 1/z_0^2.

The last inequality is strict by (D). The available family member therefore
has strictly smaller width by (B). No Delta>1 residual can minimize width,
including scaled rational-root residuals and irrational-root residuals.
This domination is a proof for all budgets, not an extrapolation of a census.

## Exact search, complete optimizers and certificates

For Delta=1, z must be odd. The roots are (z-1)/(2a) and (z+1)/(2a),
so the strict root conditions are exactly the last two inequalities in (C).
For a fixed z, write t=(z-1)/2. Then ac=t(t+1), and (C) is equivalent to

    a divides t(t+1),
    (t+1)/2 < a < t,
    c=t(t+1)/a,   a+(2t+1)+c<=L.                       (E)

This gives a direct divisor verifier. Search odd z from the largest odd
integer <=Z down to z_0 inclusive. The first nonempty list in (E) supplies
z_star and every minimizer. Existence at z_0 proves termination. Earlier
odd z must all have empty lists; lower z give strictly larger width, and the
dominance lemma already excludes every other discriminant.

A second exact representation is useful for efficient construction. For
1<=k<=L-2z, set

    U=2zk+k^2+1.

The identity (c-a)^2=(a+c)^2-4ac shows that a candidate exists precisely when
u=isqrt(U) obeys u^2=U, z+k-u is even, and

    a=(z+k-u)/2,  c=(z+k+u)/2

satisfy the strict conditions (C). Here c>a follows from rs>1. Conversely
these tests imply Delta=1 and D=2z+k<=L. Iterating k returns all residuals
for the chosen z without any factorization assumption. The constructor uses
this square test; the certificate verifier independently uses (E).

The number of tested odd z is O(sqrt(L)), because Z-z_0<=4n+1. The maximum
k is at most L-2z_0<=8n+4. Thus the constructor makes O(L) exact square
tests; this is an arithmetic-operation bound, not a bit-complexity claim.
The simple divisor verifier is slower and is deliberately a separate route.

The finite oracle also minimizes all discriminants: for a fixed z,a in (A),
Delta/z^2 strictly decreases as c increases. Therefore only the largest
allowed c need be tested to recover every minimizing residual at a budget.
This justifies the independently organized quadratic-size oracle in verify.py.
It does not assume the discriminant-one theorem.

## What changes relative to predecessors

PR6139 proves the normalization, width bound, comparison statistic, feasible
seed family, and one exact budget census. Nick Petalas's PR6153 proves the
complete equality-budget classification. This draft adds the strict domination
of all Delta>1 residuals for every L>=35, the complete small-budget exception,
and the exact optimization/certificate procedure for every remaining budget.
It does not supersede or claim authorship of their results.

The base construction belongs to zxv's PR6049, with Nick Petalas's PR5174 and
Ali Romman's rank-budget lineage. Integer discriminants, the quadratic formula,
divisor enumeration and monotonicity are classical. No global novelty claim.

## Limits and review

The exact minimal power-of-two alphabet and endpoint multiplicities are essential.
PR6139 already gives a larger-support counterexample to a broader inverse-budget
claim. Nothing here covers arbitrary alphabets, actual supplier realization,
independent targets, native operators, dirty restoration, compiler admission,
stock, precision/tape, or analytic recovery. No new kappa or multiplication
algorithm follows. The selected result and all five assumptions remain unchanged.

Finite exact checks corroborate the proof; neither human mathematical review
nor proof-assistant verification has occurred. Both predecessor PRs are recorded
as partially reviewed in the current repository ledger. The author checks have been supplemented by separate AI proof/code and
adversarial reviews, including differently organized exact censuses. These
reviews can still share reasoning errors and do not constitute human or formal
acceptance. The next useful task is independent human or proof-kernel review
of (D), the strict root endpoints and certificate soundness.
