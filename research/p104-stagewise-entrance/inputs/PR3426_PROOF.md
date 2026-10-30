# Correlated first-collector entrance

Let `pi=1+i`, and let `B=B9` be the Gaussian Newton lattice

\[
 B=\{f(x)=\sum_{S\subseteq[9]}a_S x^S:\pi^{|S|}\mid a_S\}.
\]

It is a free `Z[i]` module of rank 512. All statements below concern the
literal PR2586 word at its first collector entrance, immediately before
zero-based event 2025. The exact sources and dependencies are in SOURCES.json.

## Inherited operator hypotheses

We use PR3382's theorem that the actual Gaussian wrappers and coordinate
butterflies are automorphisms of B, and agree with their signed-floor
implementations on B. Their inverses preserve B as well.
We use PR3416's finite native covariance theorem, including global phase.
Writing `A_H` for the empty-to-frame operator, each ideal transport from H
to K equals `A_K A_H^-1`. Thus every ideal bank has a well-defined
frame-normalized value `A_H^-1 v`. A transport leaves that value fixed.
An ADD with a common source/destination frame adds its stated scalar multiple
of the normalized source. These dependencies are inherited, not re-proved by
our three numerical fixtures.

## The ideal final-cut classification

Take arbitrary initial values of the 58 dependencies in B. Denote the five
initial D values by `d_j`, the initial Q7 by `q`, and the 52 initial Y values
by `y_s`. No independence restriction is imposed on these values.

Backward slicing the authenticated destination-first word gives 257 events.
There are 200 transports and 57 ADDs. Fifty-two ADDs are positive quarters,
and five subtract initial D values into Q7 before those D banks acquire
any quarter contribution. The program groups the Y sources into disjoint
sets `S_j` of sizes 3, 7, 7, 11 and 24 for D31, D30, D29, D28 and D27.
The complete source/event lists and coefficient rows are in RECEIPT.json.
For example, `S_31={Y27,Y26,Y99}`, read at 1090, 1129 and 1231.
All 52 source paths contain transports only before their required read.

An induction in source order, using the common ADD frames, proves

\[
 D_j^{cut}=A_{F_D}\left(d_j+\frac14\sum_{s\in S_j}y_s\right),
 \qquad
 Q7^{cut}=A_{[364]}\left(q-\sum_jd_j\right),
\]

where `F_D=[256,136,64,40,16,4,2,1]`. This is an ideal rational Gaussian
operator identity. It does not assume intermediate values are integral or
that an unrestricted signed-floor execution follows this identity.

Since `d_j,q` belong to B and both displayed frame operators are
B-automorphisms, all six ideal outputs belong to B if and only if

\[
 \boxed{\ \sum_{s\in S_j}y_s\in4B\quad\text{for each of the five groups.}\ }
\]

Necessity follows by applying the inverse frame and subtracting `d_j`.
Sufficiency follows by adding a B quarter-sum to `d_j`; Q7 is always in B.
This proves the full ideal criterion for this stated initial B domain.

For each group choose its first source as pivot. Keep the other Y coordinates
and replace the pivot coordinate by the sum of its group. The inverse replaces
the pivot by that sum minus the other group coordinates. These are integral
inverse changes of bank coordinates. The checker constructs both 52-by-52
matrices and verifies both products are the identity. Consequently the admitted
Y module is isomorphic, by this explicit change of coordinates, to

\[
 B^{47}\mathbin{\oplus}(4B)^5.
\]

Every ideal admitted input is obtained by choosing arbitrary nonpivot Y
values in B, arbitrary `z_j` in B, and setting
`y_pivot=4 z_j-sum(nonpivot values in its group)`.
The quotient of `B^52` by this module is exactly `(B/4B)^5`, of cardinality
`2^10240`. This is an algebraic index, not a storage or operation bill.
PR3423's separate `y_s in 4B` restrictions characterize its stronger invariant
that every relevant prefix stays in B. They remain sufficient but are not
necessary for the ideal final cut.

## A literal reachable cancellation

Set `Y27=64 delta_0`, `Y26=-64 delta_0`, and every other component of all
358 initial banks to zero. Each nonzero initial bank is in B and outside 4B.
Indeed every Newton coefficient of `delta_0` is a sign, and
`v_pi(64)=12`. The degree-nine condition for 4B would require valuation 13.

The checker executes every event from 0 through 2024 with exact Gaussian
integer components. Every fractional ADD is checked for componentwise exact
division. All 883 native occurrences are bound to their old/new frames and
ranks. Zero-input transports stay zero. On all active coordinate pairs, it
compares the literal signed-floor result against the ideal Gaussian pair.
All 7,680 comparisons pass across 26 active native occurrences.

The first non-B event output is D31 at 1090. Its mask-349 Newton coefficient
is `-4-4i`, with degree six and pi valuation five. At the collector entrance,
all six produced banks are literally zero. The two nonzero initial Y values
are distinct physical roles. Their frames follow their actual histories,
so the cancellation is not an identification of storage roles.

Deleting the Y26 input leaves the actual Y27-only counterexample from PR3423.
Our separate full-prefix implementation reproduces its failing D31 output,
with 256 nonzero Gaussian components and the same final array hash. The
amplitude-256 positive control stays admitted. These controls retain the
actual prefix and do not substitute an ADD at a freely chosen read point.

The numerical fixture is a finite certificate. It also gives a narrow
analytic extension. A Gaussian integer multiple of this initial vector has
a Gaussian integer ideal state at every certified stage, because all those
states are Gaussian integer and the ideal operations are Gaussian linear.
For a coordinate pair, Gaussian integrality of the ideal outputs means the
real and imaginary input differences have the same parity. The literal pair
then equals the ideal pair, since
`floor(a/2)+ceil(b/2)=(a+b)/2` when `a,b` have the same parity.
Induction therefore proves the same exact full-prefix cancellation for every
Gaussian integer multiple. When the multiplier is not divisible by pi, the
two initial banks remain outside 4B and event 1090 still leaves B.
This extension is a proved consequence of the integral trace, not an
exhaustive numerical sweep of multipliers.

## Scope and remaining obligations

The universal theorem is about the ideal final cut. The exact literal trace
establishes one strict cancellation example and its Gaussian multiples.
A general correlated-domain classification for arbitrary rounded executions
is not proved. The 52-source prefix theorem in PR3423 and the independent
product-domain theorem in PR3406 are not contradicted.

We do not supply a caller that prepares these correlations, control other
collectors, price ownership, route sources, preserve all downstream recipient
histories, or change PR3423's unchanged-profile stopping decision. A final-cut
cancellation cannot remove costs from the consumer or compiler without an
additional argument. No supplier admission, improved kappa, selected-frontier
change or complete multiplication theorem follows.

Credit ywz65/PR2586 for the word and recipes, Arham Tahir/PR2665 for the
retained inputs, Clear1nsight/PR3382 and PR3423 for the Newton domain and actual
producer/consumer work, Tekalign/PR3025 for the signed-floor bijection,
Ross Richardson/PR3068 for the exactness-domain question, Nick Petalas/PR3406
and PR3416, and all retained native, geometry, compiler and precision lineage.
The new result is the correlated ideal entrance and the exact literal
cancellation separating it from the prefix invariant. Apache-2.0.
