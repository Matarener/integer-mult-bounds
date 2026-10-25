# Architectural limits of productive-helper path constructions

Prepared for [zxv](https://github.com/zxv) with substantial OpenAI Codex
assistance. Apache-2.0. This is a written proof with exact arithmetic support,
not a proof-kernel theorem or a new supplier admission.

## 1. The architecture, and the question it actually answers

The change introduced by [PR4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359)
at κ=.0023 was **productive mixed jobs**. Arbitrary independent helper inputs
finish with autonomous transforms and earn output credit. Their ranks need not
match one another or the paid recursive ranks. A finite compiler turns that
mixed template into a uniform supplier. The supplier test is

\[
 M_t(P)<M_t(T),\qquad M_t(X)=\sum_r X_r r^t,\qquad t=1-C\in(0,1).
\]

Here C is the candidate supplier saving. It is an upper planning budget for
multiplication κ; compilation, BIT and outer losses still have to be paid.
The old balanced conversion a/(1+a) is not this mixed-target test.

Within that broad architecture, a particularly successful **controller
architecture** is the rank-eight paired path, with FULL native invocations,
rank-one QUERY stages, and the retained prefix/suffix idle law. Define its
parameters explicitly:

* v main ports and a fresh block of rank b>1 per FULL; b=8 in every numerical
  application here;
* an autonomous local paid histogram P and productive helper histogram H,
  with local net debt L(t)=M_t(P)-M_t(H);
* any pair count p>=1, any split a+(p-1-a), and any binary mask on 2p+1
  stage positions;
* every QUERY costs v rank-one jobs and earns no helper credit;
* main and whole-idle jobs are exactly those in equation (1) below. Native
  realization is allowed to restrict the family further.

These are architectural hypotheses, not an enumeration of a fixed word.
All p, all splits and all masks are included. Different local words can be
substituted provided the same controller contract is established. A changed
query tariff, nonautonomous outputs, another connection graph, another idle
law or a different degree/rank rule is a different problem.

For n FULL stages, let h_j count the FULL stages preceding a side window in
its outside-to-inside reading, excluding its even stage e_j in {0,1}. For
left windows j<=a this is h_j=sum_(s<2j) x_s; for right windows j>a it is
h_j=sum_(s>2j) x_s. Put f(z)=z^t, f(0)=0. The complete paid-minus-target bill is

\[
 E=v(2p+1)+(L-v)n-2v f(1+bn)
 +2v\sum_{j=1}^{p-1}\{f(bh_j)+e_j f(b)-f(1+b(h_j+e_j))\}. \tag{1}
\]

In particular, turning an even stage FULL restores its paid middle idle.
Deleting its query while retaining old helper credit is a different, invalid
invoice. Recomputing the n=18 invoice from (1)'s canonical mask reproduces
**every paid and productive coefficient** in the retained neutral5413 and
three P104 source receipts. This binds the arithmetic to those submitted
bills. It does not freshly validate their native words or universal premises.

## 2. All masks reduce to one canonical invoice per FULL count

This section generalizes the existing exchange and convexity proofs of
[PR5405](https://github.com/CrocSwap/integer-mult-bounds/pull/5405) and
[PR5409](https://github.com/CrocSwap/integer-mult-bounds/pull/5409) to arbitrary
v, b>1 and L. Their frozen proofs are retained in `inputs/`; the reduction is
credited prior work. The new application to P104 and the per-FULL price
frontier below use that parameter independence explicitly.

Let delta(z)=f(z+1)-f(z). It is positive and strictly decreasing for z>=0,
with delta(0)=1. On either side read one end bit, then pairs (o,e). At fixed
n the local term does not change, so compare only query and window costs.
The following changes never increase E:

1. Delete a 00 pair. Its change divided by 2v is -1+delta(bk)<=0, where k
   is the preceding FULL count.
2. Replace 01 by 10. The change is f(b(k+1))-f(bk)-f(b)<=0 by subadditivity.
3. Split 11 into 10,10. The change is
   1+f(bk+2b)-f(bk+b+1)-f(b)<0. Both differences compare integrals of
   t*z^(t-1) over intervals of length b-1: [1,b] and [bk+b+1,bk+2b].

Each change includes all added/deleted QUERY costs. After these operations
only 10 side pairs remain. Move their FULL bits into any missing end/central
unpaired positions. Each move deletes one pair and changes E/(2v) by
-1+delta(bk)<0 for k>=1. For n<=2 this leaves p=1, all n FULL bits unpaired.
For n>=3 all three unpaired positions become FULL, leaving n-3 side pairs.

Finally balance the two sides. A side with q pairs contributes
-sum_(k=2)^(q+1) delta(bk). Its successive increments are increasing, so a
transfer from a side at least two pairs longer to the shorter side decreases
cost. Thus a=floor((n-3)/2), d=ceil((n-3)/2) attain the minimum.

The **attained optimistic minimum** at fixed n is therefore

\[
 C_n(t)=3v+(L-v)n-2v(1+bn)^t,\qquad n=0,1,2, \tag{2}
\]

and, for n>=3,

\[
 C_n(t)=nL+v(n-3)-2v(1+bn)^t
 -2v\left[\sum_{k=2}^{a+1}\delta(bk)+\sum_{k=2}^{d+1}\delta(bk)\right]. \tag{3}
\]

Empty sums vanish. The first expression extended to n=3 equals the second.
These are invoice comparisons. They need not be physical rewrites preserving
one particular caller's inputs.

For completeness put A_n=f(bn+b+1)-f(bn+1), D_n=C_(n+1)-C_n. Then

\[
 D_n=L-v-2vA_n\quad(n=0,1,2),
\]

\[
 D_n=L+v-2vA_n-2v\delta(b\lfloor(n+1)/2\rfloor)\quad(n>=3).
\]

A_n strictly decreases. Across the only junction,
D_3-D_2=2v[1-delta(2b)+A_2-A_3]>0. Thereafter the delta correction never
increases. Hence C_n is strictly discretely convex on **every integer n>=0**,
independently of L. The three signs

\[
 C_m>0,\quad D_{m-1}<0,\quad D_m>0 \tag{4}
\]

prove E>0 for every p, split and mask. There is no unsearched large-p tail.

## 3. A price frontier for every changed local provider

Write C_n=nL+v c_n, where c_n depends only on b,t,n. For n>=1 define

\[
 \lambda_b(t)=\max_{n>=1}\frac{-c_n(t)}n.
\]

The maximum exists: c_1=2-2(1+b)^t<0, whereas c_n/n tends to 1.
For the latter limit, the main term is O(n^t) and the side sums are O(n^t),
using delta(bk)<=t*(bk)^(t-1). Dividing by n makes both vanish. A negative
minimum of c_n/n is therefore attained at a finite n.

Then equation (1)'s entire controller family has a positive raw surplus
if and only if

\[
 \boxed{L(t)<v\lambda_b(t).} \tag{5}
\]

The n=0 invoice always costs v and cannot help. A negative value of C_n
attains the required surplus in the invoice family; physical admission and
compiler/outer funding remain separate. The inequality is sufficient only
for that relaxed moment problem.

Suppose a changed provider reduces **net** local debt by Delta(t), after
charging its added calls and accounting for its changed helper outputs,
while retaining v,b and the controller contract. The exact necessary and
sufficient threshold for the raw family is

\[
 \boxed{\Delta(t)>\Delta_{\rm req}(t)
       :=L(t)-v\lambda_b(t)=\min_{n>=1}C_n(t)/n.} \tag{6}
\]

A fixed boundary charge is additional; a per-FULL repair reduces Delta by
its full price. No free repair allowance is implicit.

This is an **architectural search filter**: a proposal can be rejected
before constructing a long controller if its optimistic net saving does not
cross (6). It applies to any local mechanism satisfying these interfaces,
not just neighboring edits of the selected native word.

The infinite ratio minimization also needs only three values. Let

\[
 J_n=nC_{n+1}-(n+1)C_n.
\]

Then

\[
 J_{n+1}-J_n=(n+1)(D_{n+1}-D_n)>0,
\]

and C_(n+1)/(n+1)-C_n/n has the sign of J_n. Thus
J_(m-1)<0<J_m proves that m uniquely minimizes C_n/n over all n>=1.
Both J signs are independent of L; c_n and the optimal count are independent
of v as well. **The best FULL count for a fixed required per-FULL discount
is determined by the path geometry and exponent, not by the local word.**

This ratio gate is distinct from minimizing C_n for a fixed provider. Using
the latter minimizer in (6) without a new argument is invalid.

## 4. Extend point exclusions to every larger exponent saving

A sign at one C alone is not an interval theorem. Here is a reusable
sufficient condition for monotonicity. Let b>1 and define

\[
 U=-\frac{P_1\log b}{b}
 +\sum_{r>b}P_r\frac rb\log(r/b)
 +\sum_{r<b}H_r\log(b/r).
\]

If U<0, then d[L(t)/b^t]/dt<0 on 0<t<1. Indeed, divide each local term by
b^t. Bound positive derivatives from paid ranks r>b using (r/b)^t<=r/b,
and those from helper ranks r<b using (r/b)^t<=1. Retain just the negative
paid rank-one term, whose magnitude is at least P_1 log(b)/b, and discard
all other negative derivatives. This gives the displayed upper bound.

Delete 00 pairs first. When n>=1 every remaining window has h>=1 if e=0,
or h>=0,e=1. Its normalized term is

\[
 h^t+e-(h+e+1/b)^t.
\]

Its derivative is negative, because z^t log z increases for z>=1; the
h=0,e=1 case is 1-(1+1/b)^t. The normalized long target has negative
derivative, and the nonnegative query term decreases. The local part is
strictly decreasing by U<0. Thus normalized E decreases in t. Every reduced
invoice positive at t0 stays positive for 0<t<=t0. For an unreduced invoice,
reduction at the new t can only decrease cost and is already covered.
The all-QUERY case n=0 costs v directly.

Consequently a certificate (4) plus U<0 excludes **all C>=C0, C<1**.
The verifier proves U<0 separately for every numerical profile here, with
upper bounds below -549. No unsupported signed-moment monotonicity is used.

## 5. New all-length numerical consequences

The exact integer interval engine independently reconstructs each source
invoice. It uses a 2^224 grid, atanh logarithms with a rational tail and
Taylor exponentials with a rational tail; see section 8. It verifies a
negative canonical witness at each lower endpoint and (4) and U<0 at each
upper endpoint. Hence these enclose the supremum over the **entire** stated
path family:

| Local contract | Lower raw crossing | Upper raw crossing | FULL count at upper gate |
|---|---:|---:|---:|
| #4610 round-three word | .00302177587077 | .00302177587079 | 18 |
| #5413 complete neutral signed invoice | .00302728824993 | .00302728824995 | 18 |
| #5544 P104 productive caller | .00304057807630 | .00304057807631 | 18 |
| #5545 P104 frame contact | .00304117181649 | .00304117181650 | 18 |
| #5551 P104 coupled contacts | .00304153116714 | .00304153116715 | 18 |
| Neutral bill minus all eight paid H8 completions | .00807671283977 | .00807671283979 | 7 |

The P104 rows extend the submitted fixed p16 crossing calculations to all
controller lengths/splits/masks under the same invoice law. They do not
freshly certify the proposed native circuits. The final row is an unrealized
optimistic relaxation, retaining all helper targets and making the actual
eight H8 completion requests free. Its n=7 canonical controller has p=5,
split 2/2. It is not a construction or a universal minimum completion cost.

In particular **any** change whose net saving is at most 8*8^t per FULL,
relative to the neutral bill, retaining this path contract, cannot reach
C=.01, even with arbitrary controller length. At .01 it would still need
more than 21.85249430914 further units per FULL. The earlier centre-free
#4610 bound near .0080596239 is a different, slightly weaker local profile;
it is not silently reused for the neutral word.

All completed native profiles above have L(1)=17v-48. Equation (3) gives

\[
 M_1(T)-M_1(P)=48n-v\quad(n>=3).
\]

Thus the selected n=18 invoice has surplus 752 and P104 has surplus 760.
This conservation law explains the small productive margin. It does **not**
fix the positive-C crossing: the distributions of paid and target ranks
matter. The P104 successors preserve this mass while strictly lowering
positive-C price.

At target C, a changed #5551 provider must save more than the following
amount **per FULL**, with optimal length already included. Displayed
thresholds are rounded down; exact outward endpoints are in RESULT.json.

| C | Optimal FULL count for (6) | Required net discount from #5551 | From #5413 |
|---|---:|---:|---:|
| .0031 | 18 | .80638594481 | .99667194384 |
| .0033 | 17 | 3.54923453123 | 3.72139618536 |
| .0034 | 16 | 4.91394927369 | 5.07657009697 |
| .004 | 14 | 12.96623724304 | 13.06167562796 |
| .006 | 9 | 38.56153416704 | 38.34368776890 |
| .01 | 5 | 85.66448729816 | 84.53539335470 |

## 6. Why derivatives cannot amplify an exhausted bill

Here "derivative" means a construction obtained using the following allowed
operations, with their actual invoices. It does not mean all native rewrites.

**Potential closure theorem.** Fix t and a collection of rules each satisfying
M_t(P)>=M_t(T). Allow disjoint unions, positive whole-array scaling, declared
tensor-product invoices, finite acyclic exact typed job matching/cancellation,
splitting of one job into disjoint-axis parts, and target completion with its
complement paid. None yields a rule with M_t(P)<M_t(T).

Proof: sums and positive scaling preserve inequalities. On a product invoice,
M_t(X tensor Y)=M_t(X)M_t(Y), so products preserve them. Sum the inequalities
of all occurrences in an acyclic typed schedule: each internal job has the
same type/rank/weight on both sides and cancels exactly once. Only external
paid jobs and targets remain. Splitting a+b into a,b increases price since
(a+b)^t<=a^t+b^t. Completing a rank-a target to a+b while paying rank b adds
a^t+b^t-(a+b)^t>=0 to paid-minus-target cost. Additional paid reserve cannot
reverse the sign. This also permits a catalyst that returns unchanged and
cancels once on each side. It does not permit double credit for a shared
input, a new joint consumer, correlated outputs, or an unpriced conversion. ∎

This is a limitation of the stated moment-based construction closure, not a
lower bound on all algorithms. It rules out more tensor depth, more integer
batching, repetitions, or a finer funding grid rescuing a failed fixed bill.
A new cross-boundary identity that changes the bill escapes the theorem.

**Compatible provider menus.** If several autonomous FULL providers have
identical v,b and main contracts, let L_min(t)=min_i L_i(t). Substituting
L_min at every FULL only decreases the invoice. Therefore a mixture of
providers cannot beat the best provider's all-length ceiling at that t.
The minimum over providers and over n commutes. Different geometries or
coupled helper contracts cannot be put in this menu without a new argument.

**Partial-helper completion.** If rank a and complementary rank b are paid
separately to finish a helper at rank a+b, the net change is
(a+b)^t-a^t-b^t<0 in target-minus-paid surplus. Merely relabeling a partial
helper as full, with a properly charged completion, cannot improve κ.
Conversely, a legal paid-path fusion a,b -> a+b reduces price strictly.
This distinction explains the genuine direction of the P104 contact gains.
For #5551 its delta is

\[
 2-3\,2^t+3^t-4^t+5^t
 =[3^t-2^t]+[5^t-4^t]-2[2^t-1]<0,
\]

by decreasing unit increments. No rank-mass saving is required.

## 7. What has and has not been closed architecturally

There is a definitive closure of **controller-only growth at a fixed local
contract**, including arbitrary length and the composition operations above.
There is also a complete numerical filter (5) for any changed provider in
the same rank-eight path architecture. There is **no proof here that every
possible native provider obeys a particular lower bound on L(t)**. Proving
such a lower bound is exactly what a ceiling for the whole local-mechanism
architecture would require.

For example, the claim "productive helpers cannot exceed κ≈.003" does not
follow from the all-length theorem: it freezes a profile that P104 changes.
The free-completion relaxation also has favorable raw invoices near .008,
so the path topology alone cannot imply a .003 ceiling. It does not follow
that that relaxation is physically achievable. The broad mixed-job compiler
is still more general than this path and has no architectural cap proved here.

A universal statement would need one of the following *new* results:

* a native lower bound L(t)>=v*lambda_b(t) over the full allowed provider
  language, with arbitrary helper factorization and all charged repairs;
* a stronger typed potential valid also for coded/coupled states and their
  actual consumers, rather than treating them as autonomous Gaussian jobs;
* a different invariant controlling all allowed controller graphs and idle
  incidences. The prefix/suffix proof does not quantify over those graphs.

The unchanged selected outer contract separately requires effective complex
and BIT budgets strictly above κ. Its admitted BIT budget is .0034. Thus a
COMPLEX-only change cannot promote κ>=.0034 using that fixed budget. This is
an outer-interface restriction, not a BIT impossibility theorem; the actual
ordinary BIT saving, later BIT improvements and a rederived outer contract
are separate questions. Likewise the first-order mass identity 48n-v does
not supply the missing native bound.

## 8. Exact arithmetic and replay boundary

For a positive integer r, put k=floor(log2 r) and z=(r-2^k)/(r+2^k) in
[0,1/3]. Use log r=k log2+2 atanh z, with log2=2 atanh(1/3). After 96
terms the omitted positive log tail is bounded by

\[
 \frac{2z^{193}}{193(1-z^2)}.
\]

Every operation is enclosed on the 2^224 grid by floor/ceiling integer
arithmetic. To evaluate exp(x), 0<=x<=16, evaluate exp(x/16) through degree
64. Since 0<=x/16<=1, its remaining tail is at most
66/(65*65!). Four outward squarings enclose exp(x). No floating-point number,
optimizer result, sampling assumption or decimal tolerance accepts a sign.

The code authenticates raw retained sources with SHA256, Git blob IDs and
complete hash-checked commit/tree paths in ORIGINS.json. Pending source commits
are not claimed as publication ancestors. Compressed Git tree objects are
size-bounded before parsing. It
rebuilds all four current complete invoices, and compares fresh results to
the entire frozen typed receipt. Controls enumerate every mask/split through
p=3 at two rational exponents and check canonical dominance, source accounting,
concavity directions, exact elementary identities and rejection of a false
ceiling below the P104 crossing. The infinite statements rest on the written
proof, not the finite controls. All acceptance predicates survive Python -O.

There is no imported native interpreter, enormous uniform template, Lean
build, Docker run, whole selected replay, or independent human audit in this
package. Source publication/review status is preserved in CLAIMS.md; copying
an exact source receipt does not turn its author-side checks into new native
verification.
