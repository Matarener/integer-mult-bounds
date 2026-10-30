# Two fixed-source BIT price gates

These are two separate applications of complete paid and target accounting.
Neither gives a new supplier or a multiplication kappa value.

## 1. Fresh commuting axes on the fixed PR589 word

Fix the original scalar events, native frame paths, and owned operations.
All free maps act as the identity on the added axes. The main boundaries and
all target credits outside the selected helper set stay unchanged. A field
state can carry any subset of the new commuting axes. Scalar contacts must
have the same subset. A native MOVE with original rank r and a change of s
new axes has rank r+s; this direct-sum charge is part of the lift contract.

Choose a nonempty set of helpers and add k>0 fresh commuting axes to each
chosen final helper job. The physical k is an integer. The original helper
job has rank eight. Each chosen helper starts with no new axis and ends with
k new axes. Along its own register path, let s_j count the changed new axes
at MOVE j. Every final axis must change at least once, so sum_j s_j>=k.
Scalar events cannot make this change. An owned COPY does not change its
persistent source register.

The exact source census shows that every helper has a paid MOVE and that
every such MOVE has original rank r_j<=7. Different persistent helper paths
use distinct MOVE events. For f(r)=r^(1-C), 0<C<1, define

    g(s)=f(7+s)-f(7).

The function g is increasing and concave, with g(0)=0. It is subadditive:
g(a)+g(b)>=g(a+b). This follows by writing each increment as an integral of
the decreasing derivative of f. Hence the paid increment on one helper path
is at least

    sum_j [f(r_j+s_j)-f(r_j)]
      >= sum_j g(s_j)
      >= g(sum_j s_j)
      >= g(k)
      > f(8+k)-f(8).

The final strict inequality follows from strict concavity and 7<8. This is
larger than the new helper target credit. Distinct helper paths give distinct
charges. Further copied fields and boundary work have nonnegative cost.
Every nonempty choice loses. The same proof permits different positive k
values on different chosen helpers.

Reversing the source leaves each helper's own MOVE ranks unchanged. The BIT
rank-eight helper job is an involution, so the same target rank and argument
apply in the reverse direction. The verifier checks the two rank censuses;
it does not claim a new native reverse-word replay.

This proof fixes the original word and its contact rules. It does not cover
new scalar operations, status-changing free maps, different output jobs,
preloaded added-axis status, shared persistent ownership, or a different
native operation. No mincut computation is needed for the theorem.

## 2. The retained paired-k3 p12 source

Fix the paired-triple geometry parameter at 12. The retained generator and
frozen matching give h=24, v=1760, R=19788 and centre debt c=528. Let L_r be
the complete local paid histogram, including both main boundary legs. Let
H=R H24 be the complete local helper target list. The source compiler gives

    sum_r r L_r - 24 R = 2 v (24-1) + 528.

The verifier reconstructs L from the unchanged generator, checks the scalar
decoder, and includes its target-side main legs and source-side main legs.
Each main side has rank mass v(24-1). No productive helper is made free or
credited twice. The retained compiler's modular-rank argument and native
invoice convention are inherited; this is not a new native admission proof.
The predecessor's standalone independent `check_paired_cube_bit.py` is not
rerun. The tariff conclusion applies to the reconstructed generator invoice.

Let p>=1 now denote the balanced controller parameter, not the geometry
parameter. Put d=23 and let a=floor((p-1)/2), b=p-1-a. Its paid list is

    (p+2)L + v(p-1)H1
    + 2v sum_(s in {a,b}) sum_(j=1)^s H_(d(j+1)).

Its target list is

    (p+2)R H24 + 2v H_(1+d(p+2))
    + 2v sum_(s in {a,b}) sum_(j=1)^s H_(1+d(j+1)).

The exact target rank minus paid rank is 1232p+704. This positive rank
surplus is not enough to obtain a useful exponent.

Set C=1/500 and t=1-C. Let delta be the local paid moment minus local helper
moment, and let M(p) be the complete target moment minus paid moment. Each
side pair contributes at most one unit before multiplication by 2v:

    (x+1)^t-x^t <= 1.

There are p-1 such pairs. Subtracting the thin calls gives

    M(p) <= U(p)
    U(p) = -(p+2)delta + v(p-1) + 2v(1+d(p+2))^t.

The verifier uses exact rational enclosures from the retained positive-series
engine. It proves M(p)<0 for p=1,...,64. It also proves U(64)<0 and U'(64)<0,
using a lower enclosure for delta and upper enclosures for the positive
endpoint terms. Since U''(p)<0, the derivative decreases. Therefore U(p)<0
and M(p)<0 for every real p>=64. These checks cover every positive integer
controller parameter.

To interpret this as a raw-saving bound, normalize M by 24^t. Every local
paid rank is less than 24, which the verifier checks. The normalized negative
local term decreases with C. The normalized thin debit also decreases. The
endpoint rank exceeds 24, so its normalized credit decreases with C. Every
side pair has x>=46>24. The function

    ((x+1)/24)^t-(x/24)^t

increases with t>0: the derivative of y^t log y in y is positive for y>1.
Hence each normalized side credit decreases with C. Thus M/24^t is strictly
decreasing for 0<C<1. Since M(0)=1232p+704>0 and M(1/500)<0, the raw crossing
for each p is strictly below 1/500.

The retained p=11 crossing lies in

    (0.00164539220, 0.00164539221).

It is a positive sign-change control. This package does not claim that p=11
is the global optimum. It performs no floating root search, matching search,
or scan over other source geometries.

This second gate fixes the p12 module, decoder, matching, full unnormalized
invoice, and balanced caller. It does not cover a changed local recipe,
partial-gauge optimization, another geometry parameter, or another caller.
Its raw crossing is not the complete multiplication exponent.

## Source-rank appendix: permutation-only completion

This appendix bounds binary correction rank, not native factorization cost.
Let J be the 111-by-111 noCOPY matrix in the pinned PR589-H-NATIVE source.
The source factors A=J+I as U V, with rank nine. Thus U and V both have rank
nine, and A and U have the same column code. The 511 nonzero words in this
code all have weight at least 48. The verifier checks this exact
code and its full weight distribution.

Suppose a permutation matrix P had rank(J+P)<=8. Then

    rank(P+I) <= rank(J+P)+rank(J+I) <= 17.

A nontrivial permutation cycle of length l moves l rows and contributes
l-1 to rank(P+I). Since l<=2(l-1) for l>=2, P can move at most 34 rows.
Delete these moved rows from A. The remaining rows still have rank nine:
a nonzero vector in the column code of U cannot be supported on only 34 rows,
because its minimum weight is 48. On every remaining row P equals I, so J+P
agrees with A there. Hence rank(J+P)>=9, a contradiction.

The identity permutation attains rank nine. Thus

    min_(P a permutation matrix) rank(J+P) = 9.

The retained arbitrary-invertible completion changes three rows and yields
an invertible output code. Its target code need not be a permutation. That
rank-three construction does not contradict this permutation-only theorem.
Conversely, this theorem gives no lower bound on the native cost of a new
factorization, a general invertible output code, or a multi-call controller.
The direct-sum plane price screen is not part of this appendix.

## Exact evidence and controls

RESULT.json contains outward rational enclosures, rounded by integer floor
and ceiling to a denominator of 10^12. The verifier checks the unrounded
exact signs first and checks that every displayed enclosure contains them.
No floating-point value enters either gate.

Ten live input files are pinned before external source code is loaded. The
verifier executes those source bytes directly and does not use an inherited
bytecode cache. Changed bytes in every source are rejected. It also rejects
an own helper MOVE of rank eight, a helper without a paid path, a missing
paid rank-one job, an unearned helper credit, and omission of the local gap
from the analytic tail. The appendix rejects a changed decoder row and a
zero-rank defect.

These checks verify the stated source census, declared complete invoice, and
price implications. They do not verify a common-cover supplier, full native
payload, ordinary movement and precision budget, uniform compiler, or outer
multiplication theorem.
