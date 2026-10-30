# Independent static review of the joint A/B/C family ceiling

Date: 2026-10-26. Reviewed artifact:
`../economics/JOINT-EXCHANGE-CEILING.md`, particularly sections 2–6.
This is an independent agent paper review with finite rational-algebra
checks. It is not independent human or proof-kernel acceptance. No scientific
replay, source-function import, native compilation, price engine, numerical
root search or physical construction was performed. Only this review file
was written for this assignment.

## Decision and exact scope

**No mathematical blocker found.** Under the specified PR5545 local paid
inventory, fixed helper/main targets, unchanged nonlocal recursive bill and
18 local invocations, the three-generator histogram relaxation has a unique
single-invoice integer optimum `(a,b,c)=(219,222,112)` for every `0<t<1`.
Granting free pooling across all 18 calls strengthens the optimum to
global counts `(A,B,C)=(3942,4005,2016)`, or averaged local counts
`(219,445/2,112)`. Even granting reverse exchanges, arbitrary sequencing,
newly created H5 reuse and zero restoration debit, the stronger pooled
complete target-minus-paid margin at saving `.0033` is strictly below
`-14.4551134`. The normalized monotonicity proof excludes
every larger saving below one in this same family.

This is a scoped necessary-budget ceiling on the stated rank-profile
family. It does not establish a ceiling for all P104 words, rank
redistributions, target inventories, callers, compiler architectures or
supplier classes. It does not produce a physically realizable optimum or
certify PR5551's complete admission or claimed funded endpoint.

## Inventory and recycling proof

The baseline is

`{1:2428,2:557,3:389,4:112,5:107,6:17,7:13,9:1}`.

For signed integer net exchange counts `a,b,c`, the changes in varying
counts are exactly

`(-a+b+c, -2b-c, b, -c, -a+c, a)`

at ranks 1–6. Therefore nonnegative final histograms necessarily obey
`a<=107+c`, `b<=floor((557-c)/2)` and `c<=112`. These inequalities include
all H5 jobs created by C before A consumes them. Reverse operations and
cycles do not escape the argument: every such sequence has signed net
counts satisfying the same final histogram equations. No assumption of
nonnegative net counts was used. For completeness, feasibility also implies
`a>=-17` and hence `c>=-124`, although the upper-bound proof does not need
this lower bound.

Each forward gain is positive on `0<t<1`:

- `gA=1+5^t-6^t`, by strict subadditivity;
- `gB=2*2^t-1-3^t`, by strict concavity;
- `gC=2^t+4^t-1-5^t`, by decreasing equal-length increments.

For fixed c, maximizing a and b gives the relaxed upper envelope
`F(c)=(107+c)gA+floor((557-c)/2)gB+c*gC`. On increasing integer c by one,
the floor loses either zero or one B exchange. Thus the gain is either
`gA+gC` or `gA+gC-gB`. The former is `2^t+4^t-6^t>0`. The latter is
`1+3^t+4^t-2^t-6^t>0`: the strict inequality
`3^t-1 > 6^t-4^t` and `2>2^t` add to the desired expression.

Consequently c=112 is uniquely optimal, then a=219 and b=222 are uniquely
optimal. The resulting profile
`{1:2543,2:1,3:611,6:236,7:13,9:1}` is feasible in the unrestricted
histogram relaxation: execute 112 C exchanges, 222 B exchanges and 219 A
exchanges. It has 3,405 local jobs and rank mass 5,894. This ordering is a
multiset feasibility witness, not a legal source-chart itinerary. Starting
from the claimed PR5551 B+C successor gives the same optimum after net
remaining counts `(219,221,111)`.

This first result applies to each integer local invoice separately. Pooling
all 18 calls permits nine extra B exchanges, so that first bill would be an
insufficient envelope for the pooled family. The revised designer proof
correctly removes the artificial floor for real averaged counts. After
saturating a and b, the objective's derivative in c is
`gA+gC-gB/2>0`, following from `gA+gC-gB>0` and `gB>0`. The unique
averaged optimum is `(219,445/2,112)`. Its 18-fold total
`(3942,4005,2016)` is integral and feasible in the pooled histogram
relaxation. The averaged local profile is
`(5087/2)H1+(1223/2)H3+236H6+13H7+H9`, with zero H2, H4 and H5.
It still has 3,405 jobs and rank mass 5,894. This explicitly covers
heterogeneous choices between calls, rational mixtures and pooled rank
inventory; no physical sharing of independent inputs is inferred.

## Full bill and target-point certificate

Independent integer recounting from the retained PR5545 complete invoice,
adding the pooled global profile delta, gives exactly the full paid
histogram printed in revised section 4. Its count is 65,970. The unchanged
productive count is 12,814, with complete target-minus-paid rank mass 760.
The signed coefficients at ranks 1–9 are exactly

`{1:-47343,3:-11007,4:918,5:648,6:-4248,7:198,8:2196,9:5274}`.

Relative to the separate-integer-local bill, the pooled bill has nine more
rank-one jobs, eighteen fewer rank-two jobs and nine more rank-three jobs.

The high terms are the unchanged seven 416-fold `(H_(r+1)-H_r)` pairs at
`r=16,24,32,40,48,56,64`, one 208-fold pair at 72, and 208 targets at 145.
No helper, query, idle or main-bank count is removed by this recount.

The reused baseline certificate is
`outputs/p104-contact-reassessment-20261025/RESULT-normal.json`, SHA256
`3c4d8db5a9695924027f5801901b55cefe0cdc5ea07450aaf396de7e5887e608`.
This review reauthenticated that exact hash, its reviewed source head
`18968423711fd902aaee1099979497d55603e1dc`, `C_probe=33/10000`, and its
retained outward upper endpoint
`-64.2349800489874753468185 < -64`. The scientific interval calculation is
inherited from that qualified receipt; it was not rerun here. Its checker
constructs rational lower/upper sums with signed outward selection
(`outputs/p104-contact-reassessment-20261025/check.py:185-203`).

The proposed gain functions are concave in saving C on `[0,1]`. Their
second derivatives have the asserted signs. For gB, the sufficient
comparison is `(log3)^2>2(log2)^2`; for gC it is
`(log5)^2>5(log2)^2`, using `2^t,4^t<=5^t` for `t>=0`.
The tangent-at-zero upper bounds therefore apply over the entire required
domain, not just near zero.

This reviewer independently evaluated only finite rational sums and
inequalities, using Python standard-library `Fraction`, with no exponent
or logarithm approximation engine. For n=2,3,5, the proposed atanh series
with N=32, `z=(n-1)/(n+1)`, lower partial sum and geometric tail bound
strictly establish all three displayed log brackets. Each tail is less
than `1/10^10`. Exact rational substitution confirms the tangent constants
`2705/1000`, `524/1000`, `1117/1000` and both second-derivative sufficient
inequalities.

The first separate-integer-local calculation independently checks as

`219*(2705/1000)+222*(524/1000)+112*(1117/1000)=833827/1000`,

and

`-64+18*(33/10000)*(833827/1000)=-72353381/5000000=-14.4706762<0`.

For the stronger pooled family, the nine extra B exchanges add less than
`9*(33/10000)*(524/1000)=0.0155628`. Exact rational addition gives

`-72353381/5000000+9*(33/10000)*(524/1000)`
`=-72275567/5000000=-14.4551134<0`.

These are conservative strict upper bounds, not computed values of the
actual margins or new numerical roots. The revised designer proof uses
the stronger pooled bound for its final ceiling.

## Monotonic extension and domain

The proof normalizes the optimal complete moment by `9^t` for
`0<=t<=1`. Only positive low-rank coefficients at 4,5,7,8 can contribute
negative derivatives. Their total magnitude is less than `3960*log9`.
The negative rank-one term alone contributes at least
`(47343/9)*log9`, which is strictly greater. Every other negative low-rank
term has nonnegative derivative; rank 9 is constant. For high paired
terms, `x^t*log x` increases for `x>1,t>=0`, so their derivatives are
positive; the rank-145 target derivative is positive as well.

Thus the normalized moment is strictly increasing in t. Its endpoint
values are `-53156` and `760/9`, exactly as stated. It has one zero, and
the negative `.0033` bound puts the corresponding saving strictly below
`.0033`. For every `.0033<=C<1`, the optimal family moment stays negative;
all other family members are pointwise no better by the preceding
inventory argument. This does not extrapolate the analytic proof to
`t<0` or a saving outside its declared `0<C<1` domain.

## Premises to retain in any handoff or publication

The exclusion requires the exact baseline paid inventory, the same complete
targets and nonlocal recursive lines, eighteen source-call multiplicities,
the price law `H_r=r^(1-C)`, nonnegative final paid counts and a complete
changed invoice in the A/B/C span only. The stronger proof even grants real
averaged counts and free pooling across calls. The inherited signed
moment must remain a necessary condition for the proposed supplier and
compiler contract. Restoration costs were relaxed in the favorable
direction; extra debits or lost targets cannot repair the failed margin.

The three exchanges are granted at the histogram level. The proof does
not need all of PR5551's actual source contacts to be freshly admitted,
because granting unavailable or incompatible contacts only enlarges the
family being bounded. Source-native validity and full compiler/outer,
precision/tape, erasure and analytic recovery premises remain separate.
The 182-map native qualification and the different-head transfer note
therefore keep their own coverage boundaries.

The initial mathematical proof was correct for separate integer-local
inventories. Root's pooling refinement enlarged that scope; the added
global/rational envelope and revised bound were independently checked here.
The revised artifact also quotes the exact retained baseline outward upper
endpoint next to the `.0033` step, making the reused numerical premise
visible without reconstructing an engine. No unresolved mathematical
correction remains in the revised scoped proof.
The useful stopping rule is specific: a `.0033` proposal staying entirely
inside this fixed A/B/C family fails before physical construction. Smaller
funded improvements and source changes outside that family remain open.
