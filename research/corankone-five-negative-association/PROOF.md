# Five-indicator negative association

This proof was produced by Nick Petalas. Apache-2.0.

## Statement and boundary

Let m>=5. Let U_1,...,U_5 be pairwise orthogonal rank-one idempotents on
F_2^m. Draw G uniformly from the complete group GL_m(F_2). For each i let
E_i mean that every leading principal minor, of orders 1,...,m-1, of
G(I-U_i)G^-1 is nonzero. Put Z_i=1_{E_i}.

**Theorem.** For any disjoint nonempty subsets A,B of {1,...,5} and
nonconstant coordinatewise increasing functions f:{0,1}^A->R and
g:{0,1}^B->R,

    Cov(f(Z_A),g(Z_B)) < 0.

If either function is constant, its covariance is zero. Thus Z is negatively
associated in the usual non-strict sense as well. These hypotheses fix the
field, kernel geometry and probability measure. They do not cover restricted
or conditioned header collections.

This is a scoped proof with an exact finite component. The new step closes
Open next question 1 of Krzysztof Wojt's PR5093. The moment laws and the
four-event method are cited inputs, not new results or audited deliverables.

## Counting inputs

The five image lines together with their common-kernel complement give a
simultaneous basis taking U_i to e_i e_i^T. A fixed change of basis permutes
the whole header domain. Permuting the five distinguished lines also preserves
its uniform measure, so the indicator law is exchangeable.

Write n=m-1, X=2^(n+1), and p_k=Pr(E_1 and ... and E_k), with p_0=1.
Use Nick Petalas's PR4227/4261/4275 character law and PR4599 four-event
spectrum, and Ryanson Jonathan's PR4607 five-event spectrum:

    p_k = N_k(n) / [2^(kn) product_(j=0)^(k-1)(X-2^j)],
    N_k(n) = sum_z s_(k,z) z^n,                         0<=k<=5.  (1)

All integer pairs (z,s_(k,z)) are retained as SPECTRA in verify.py. The first
spectra are {1:1}, {3:1}, and {9:1,7:-2,5:1}. The five-event spectrum has 62
nonzero terms, headed by 243^n-20*189^n+60*171^n. Its published character
computation is a cited mathematical input. It was used once to obtain the
literal table; this contribution does not import or replay that executable
in its verifier, or claim independent validation of that spectrum. SOURCES.json
pins the exact proof and source bytes on the scientific base.

Use the common strictly positive denominator

    Q(n)=32^n product_(j=0)^4(X-2^j),
    A_k(n)=2^((5-k)n) N_k(n) product_(j=k)^4(X-2^j).

For every n>=4, p_k=A_k/Q and A_0=Q. These identities retain every finite-GL
factor. Replacing X-2^j by X would change the probability law.

## Exhaustive increasing-event reduction

Any increasing Boolean function on s bits is determined by its truth table.
A nonconstant such function is zero at the empty subset and one at the full
subset. Enumerate every integer truth table from 1 to 2^(2^s)-2, keeping it
exactly when

    F(x) <= F(x union {j}) for every x and every bit j.          (2)

For s=1,2,3,4 the resulting list lengths are 1,4,18,166. This is an exhaustive
finite loop over at most 65,534 candidates, not a symmetry assumption.

Subset Mobius inversion gives a unique multilinear expansion

    F(z)=sum_I a_I product_(i in I) z_i.

Let a_k=sum_(|I|=k) a_I. Then E[F]=sum_k a_k p_k. For a second increasing
event H on disjoint coordinates, with grouped coefficients b_l, exchangeability
and disjointness give

    E[F H]=sum_(k,l) a_k b_l p_(k+l).

The positive covariance gap therefore is

    Delta(F,H)=E[F]E[H]-E[F H]=P_(a,b)(n)/Q(n)^2,
    P_(a,b)=(sum_k a_k A_k)(sum_l b_l A_l)
             - Q sum_(k,l) a_k b_l A_(k+l).                    (3)

Up to exchanging the two supports and permuting coordinates, all possible
support sizes are

    (1,1), (1,2), (1,3), (1,4), (2,2), (2,3).

The verifier visits all 277 labelled pairs on these canonical supports,
including functions which ignore an input. It reconstructs each truth table
from its individual Mobius coefficients before grouping by degree. Expanding
(3) and collecting identical power sums gives 37 distinct nonzero polynomials.
The old support types give 11 distinct gaps. The new 4+1 and 3+2 types supply
the other 26. No conjunction-only shortcut is used.

## Exact signs for every dimension

For each of the 37 polynomials, write

    P(n)=c B^n + sum_(z<B) c_z z^n,
    b=max{z<B:c_z!=0},   C=sum_(z<B)|c_z|.

All bases here are positive integers. The verifier regenerates each polynomial
by integer addition and multiplication, and checks that the literal TAILS row
records exactly B,c,b,C,N, with B>b>0 and c,C>0. It checks

    c B^N > C b^N.                                            (4)

For every n>=N, since b/B<1,

    P(n) >= c B^n-C b^n > 0.

For each remaining integer 4<=n<N it checks P(n)>0 using exact integers,
and separately compares P(n)/Q(n)^2 with direct rational evaluation of (3)
using (1). Thus the finite prefix and the tail cover every n>=4, with no
unchecked interval. N is at most 179, so every gap has an analytic tail from
m=180 onward. Individual gaps often have much earlier tails.

The complete 37-row certificate is the TAILS tuple in verify.py. Each row
contains integers only and is regenerated and checked, rather than trusted
as an execution receipt. The verifier emits the corresponding support sizes,
coefficient vectors, polynomial lengths and tail data for inspection.

These exact finite checks and the elementary tail inequality prove
Delta(F,H)>0 for every nonconstant increasing Boolean pair on disjoint
nonempty supports.

## Increasing real functions

On a finite Boolean cube, an increasing real function f can be written as its
minimum plus a finite nonnegative linear combination of its nonconstant
increasing superlevel-set indicators. Explicitly, for distinct values
v_0<...<v_r of f,

    f=v_0+sum_(j=1)^r (v_j-v_(j-1)) 1_{f>=v_j}.

Every coefficient is positive. The same decomposition holds for g. Covariance
is bilinear, constants contribute zero, and every indicator pair has strictly
negative covariance by the preceding section. If f and g are nonconstant,
there is at least one summand in each decomposition, so their covariance is
strictly negative. This proves the theorem.

## Verification boundary

The standard-library verifier also evaluates all 277 truth-table pairs directly
on the 32 atoms at m=5,6,8,16, using inclusion-exclusion from (1). This checks
the grouped-coefficient and disjoint-support calculation by a separate path.
It verifies every atom is nonnegative and the masses sum to one. These are
bounded corroborations, not a separate complete-GL enumeration or an audit of
the moment law.

Invalid domain, sign, tail-mass and cutoff controls remain active under
optimized Python. A two-point perfectly correlated distribution is detected as
having positive covariance, so exchangeability alone cannot replace (1).
The claim does not supply a physical header sampler, producer, consumer,
restoration protocol, stock/tape budget or supplier admission. It gives no
odd-field, six-indicator or nonorthogonal-kernel theorem. Independent human
and formal proof-kernel review are unclaimed. No multiplication exponent or
selected-frontier change follows.
