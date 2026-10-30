# A sign-cut bound for complete complementary callers

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Contract and claim

Fix a finite set of coordinate axes. On axis a let Q_a be the usual lifted
Gaussian at width f, and put J_a=Q_a^2. The Q_a commute, J_a^2=I, and f>=3.
An ordinary operation is complex-linear and has a matrix on field indices whose entries are complex
scalar combinations of products of the J_a. This grants all such operations
for free. It includes arbitrary field mixing, COPY, retained observations,
owned zero fields, CLEAR, and ordinary sector projectors. It does not grant
an arbitrary address permutation, value conjugation or an odd Gaussian input gauge.

A whole B or C call has 112 main pairs. There are 56 A pairs and 56 exceptional
pairs of the stated type. In the common coordinate chart its main blocks are

    A = D [[1,0],[Q^-1,1]],
    B = D [[1,0],[1,Q]],
    C = D [[Q,0],[1,1]].

Here D is the product on seven distinct transverse axes, and Q is on a
different central axis. A call can choose its axes, central axis, main fields
and port placement. Different calls can reuse axes and fields. Inverses,
transposes, inverse transposes and the source even-power corrections are
allowed. Each call retains its exact paid profile and all 408 independent
helper outputs. Helpers are separate from the caller's main computation;
no helper input or output is a shared main resource. Native internal maps
are part of the whole-call premise, not extra free caller operations.

An additional query applies a product of coordinate Gaussians or their
inverses to one field. Its charged rank r is the number of odd axes after
even powers are removed. All these queries are charged, including idles
and corrections. There is no upper bound on r. The caller can have any
finite number of main inputs, fields, steps and calls. It is a linear
straight-line program; its choices do not depend on the input values.

The productive main outputs are independent full Gaussian jobs on distinct
original arbitrary fields, on the declared coordinate axes. Their ranks
r_i are the numbers of odd axes. Invertible ordinary input/output basis
changes do not affect the proof. A projected component of a field is not
credited as a full independent Gaussian job.

Let L_B,L_C count the whole calls. Write P_X(t),H_X(t) for the sums of
rank^t in the exact paid and helper profiles. For every 0<t<1, define

    K(t) = 28 + 140*7^t + 84*8^t,
    Delta_X(t) = P_X(t) - H_X(t) - K(t).

**Theorem.** The complete target-minus-paid moment satisfies

    F(t) <= -L_B*Delta_B(t) - L_C*Delta_C(t) < 0

if at least one B or C call occurs. Both deltas are strictly positive.
The result permits any main target ranks and any additional query ranks.
It holds at each width f>=3. Thus this model has no positive complete
recursive moment at any saving exponent 0<C<1, where t=1-C.
It does not claim a universal obstruction for other address alphabets,
helper sharing, native source changes or nonlinear callers.

## 2. Faithful characters and rank distance

The one-bit Gaussian is

    (1/2) [[1+i,1-i],[1-i,1+i]].

Its two eigenvalues are 1 and i. The f-fold address lift has eigenvalues
i^k for 0<=k<=f. For f>=3 all four fourth roots occur. In each J_a sector,
both signs of a chosen square root q_a of J_a therefore occur. Different
coordinate axes are tensor factors, so all joint sign choices occur in
every joint even-power sector. This uses tensor products on addresses,
not tensor powers of the two-field A/B/C matrices.

Fix one even-power sector and a base character q=(q_a). For a set S of
axes, let q' negate q_a exactly on S. Every ordinary matrix is identical
at q and q'. For any two field matrices define their rank distance by

    d(M(q),M(q')) = rank(M(q)-M(q')).

The telescoping identity for a product of matrices gives

    d(G_n(q)...G_1(q), G_n(q')...G_1(q'))
      <= sum_j d(G_j(q),G_j(q')).

Each term is multiplied on its left and right by other matrices, which
cannot increase its rank. Pad the finite computation to one field bank
to include copies, zero fields and retained results. Restricting to the
original input columns and productive output rows cannot increase rank.
This proves the same inequality with arbitrary interleaving and feedback
through previously computed linear values. It is not a one-snapshot bound.

For independent diagonal Gaussian targets, the left side is exactly the
number of target supports that meet S in odd cardinality. Their nonzero
diagonal values change sign exactly in that case. Invertible ordinary
boundary matrices preserve this rank. A rank-r additional query has rank
distance one or zero under the same odd-intersection rule.

## 3. Exact cut charge of a whole B/C call

Let c indicate a central sign flip and e indicate an odd number of flips
among the seven transverse axes. Then D changes to (-1)^e D. Direct
subtraction of the two displayed pair matrices gives these ranks:

| c | e | A pair | B pair | C pair |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 1 | 1 | 1 |
| 0 | 1 | 2 | 2 | 2 |
| 1 | 1 | 2 | 1 | 1 |

For example, in the last row the B difference is
D*[[2,0],[2,0]], while the A difference is 2D*I.
These calculations hold for every nonzero complex q and D.
Transposition preserves rank. Also

    M(q)^-1 - M(q')^-1
      = -M(q)^-1 (M(q)-M(q')) M(q')^-1.

Both outside matrices are invertible, so inverse and inverse-transpose
calls have exactly the same ranks. The source even-power corrections have
the same values at both characters and preserve rank. The 56/56 direct
sum and ordinary port permutations give a whole-call cut charge of 0,
112,224,168 in the four table rows.

Now flip each global axis independently with probability p, where
0<p<1/2. Put

    h_p(r) = (1-(1-2p)^r)/2.

This is the probability of an odd number of flips on r distinct axes.
The central flip and the transverse parity are independent within each
call. Axis reuse by different calls does not change linearity of
expectation. The expected whole-call charge is exactly

    224*h_p(7) + 112*p - 168*p*h_p(7)
      = 140*h_p(7) + 28*h_p(1) + 84*h_p(8).

The verifier also obtains this polynomial by enumerating all 256 masks
and their exact Bernoulli weights. For any complete caller, the rank
distance inequality therefore gives

    sum_i h_p(r_i)
      <= (L_B+L_C)*(140*h_p(7)+28*h_p(1)+84*h_p(8))
         + sum_extra_queries h_p(r).

No serial topology, fixed number of main owners, disjoint stage axes or
target/query rank cutoff is used here.

## 4. From random cuts to every positive saving exponent

For 0<t<1, the number

    Z_t = integral_0^infinity (1-exp(-s))*s^(-t-1) ds

is positive and finite. Near zero its integrand has order s^-t; near
infinity it has order s^(-t-1). The substitution u=rs gives

    r^t = (1/Z_t) integral_0^infinity (1-exp(-r*s))*s^(-t-1) ds.

Set p=(1-exp(-s))/2. Then 1-exp(-r*s)=2*h_p(r).
Integrate the preceding cut inequality against this positive measure.
All sums have finitely many nonnegative terms. This gives

    sum_i r_i^t <= (L_B+L_C)*K(t) + sum_extra_queries r^t.

The exact extra-query moment cancels its charged cost. It cannot open a
gap by using a higher rank or by feeding a later native call. Add the
separate native helper targets and subtract the exact local paid profiles
to obtain the asserted upper bound on F(t).

This argument also applies to positive mixtures of the functions
1-exp(-s*r), with a nonnegative linear term. It does not assert the
whole-caller capacity inequality for every concave function. The bill
comparison in the next section does hold for every nondecreasing concave
g with g(0)=0; these are distinct statements.

## 5. Exact complete bills and strict sign

The frozen PR4703 profiles, audited in PR4712, are:

| Type | Paid rank:count | Independent helper rank:count | Net rank mass |
|---|---|---|---|
| B | 1:1956, 2:450, 3:403, 4:127, 5:28, 8:8 | 3:2, 4:26, 6:7, 7:47, 8:326 | 1688 |
| C | 1:2011, 2:445, 3:427, 4:112, 5:12, 7:8 | 3:26, 4:2, 6:6, 7:48, 8:326 | 1680 |

After subtracting the capacity coefficients 1:28, 7:140, 8:84 and
cancelling equal ranks, the exact delta coefficients are:

| Type | Positive terms | Negative terms |
|---|---|---|
| B | 1:1928, 2:450, 3:401, 4:101, 5:28 | 6:7, 7:187, 8:402 |
| C | 1:1983, 2:445, 3:401, 4:110, 5:12 | 6:6, 7:180, 8:410 |

Remove 8*g(1) from the positive B terms. The remaining positive and
negative rank masses are equal: 4567 for B and 4576 for C. Every positive
rank is at most 5; every negative rank is at least 6. For a nondecreasing
concave g with g(0)=0, the ratio g(r)/r is nonincreasing. Consequently

    Delta_B(g) >= 8*g(1) + 4567*(g(5)/5-g(6)/6),
    Delta_C(g) >=           4576*(g(5)/5-g(6)/6).

For g(r)=r^t and 0<t<1, the common ratio gap is strictly positive.
This proves the sign for the full open interval, without sampling
exponents. In the linear limit t=1, the deltas are 8 and 0.

As a quantitative example only, at C=9/2500=.0036 the exact interval
checks give Delta_B>31.58147 and Delta_C>23.98603. These are deficits in
the raw recursive moment per whole call, not kappa values. The checker
uses integer powers to enclose each r^(-9/2500); decimal arithmetic only
proposes the endpoints. Any finite native work or outer reserve that was
granted free can only worsen the already negative bill in this model.

## 6. What changes this conclusion

PR4848 proves a serial ceiling on the same 224 owners and fresh stage
axes. This proof removes those premises. Merely adding main owners,
interleaving paid queries, reusing axes, changing port placement, using
noncoordinate scalar role gauges, or packing ordinary even-power sectors
does not evade this theorem while its contract holds. The scalar
rank-distance and integral facts are classical; the exact application to
the admitted 56/56 B/C endpoint and complete bill is the new result.

The following changes require a new proof and bill: shared or productive
helper feedback into the main computation; a joint native call with a
different endpoint or paid profile; noncommuting address maps between
calls; a target in another address chart; nonlinear operations; or a
source resource with an odd input gauge whose preparation has a different
contract. These are boundaries, not claims of feasible profitable callers.

The eight-transverse-axis A interface has rank capacity 1904 in the linear
limit, rather than 1680. The checker retains this positive scope control.
No obstruction for the productive eight-axis P104 family follows. A
query-only caller also attains equality, at any query rank, including ranks
above eight. The theorem is not a universal lower bound for multiplication.

## 7. Verification and inherited obligations

The written proof quantifies over all callers in the stated model and all
f>=3. The standard-library verifier authenticates frozen source bytes,
checks 864 rational pair/orientation/sign cases, enumerates the cut
polynomials, and checks 5952 character pairs in twelve mixed finite-field
circuits. It verifies the bill cancellation, exact power intervals and
four corruption controls. Those finite checks support the algebra; they
are not substituted for the all-width or all-caller proof.

The full native word, phases, helper ownership and compiler are inherited
from the cited source and audit. They were not rerun here. No new native
caller, formal proof-assistant theorem, complete multiplication algorithm,
selected-frontier change or independent scientific acceptance is claimed.

Credit Dugongue for PR4703 and the typed-provider work in PR5578/5586;
Cao Yifan/intqwq for PR4712; Chris R/Clear1nsight for PR4848; Cinna Davis
for PR4674 and the controller lineage; Ali Romman for PR5626's query-rank
perspective; DaysSky, zxv, Jacob Alan Sussman and all retained source authors.
