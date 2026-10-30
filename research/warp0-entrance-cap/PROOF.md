# Exact entrance feasibility with adaptive native boundaries

SPDX-License-Identifier: Apache-2.0. Prepared for ToikY with substantial
OpenAI Codex assistance, including separate mathematical review. This is
written mathematics, not a new proof-assistant or independent human review.

Credit Dugongue's PR3929 at `0c0e31cf12e8f4f07e8419a6d33ae85129fb5a01`
for the transported-frame construction and compiler; dataisfire/PR3734,
zxv/PR3682, Ross Richardson/PR3605, Jeremy Kothe, Sagar Thakrar/PR3687,
Arham Tahir/PR3693 and the retained native lineage keep their source credit.
The retained notices remain authoritative for copied predecessor code.

## Fixed domain

All frames are subspaces of V=F2^9; + means subspace join. Freeze the source
register inventory, ordered scalar operations and coefficients, native maps
and their order, complete A/cut prefix, B prefix before zero-based warp0,
start frames, target/helper terminal caps and wrapper contracts. Each scalar
gate must use a common frame containing its ORIGINAL frame and the incoming
frames of every operand. Each later native entrance must contain its ORIGINAL
entrance and its incoming lender frame; its exit is the image under its
unchanged invertible map. Such boundaries may adapt and enlarge. No scalar
reordering, new nonidentity operation, smaller original scalar frame, changed
native map, changed endpoint or additional helper belongs to this domain.

Here warp0 means array index zero, NOT the chronologically first native warp:
eight other B native events precede its position and remain in the frozen
prefix. All chronological event ordering, including native events at a shared
B position before that position's scalar event, is retained.
Warp0 uses lender 243 at original B position 916. Its original entrance is
U0=span(261,133,85,45), of dimension four. Choose U' containing U0 and set
its exit to G0 U'. Its incoming frame is the frozen prefix's original frame,
which must lie in U0. An explicit paid identity climb supplies the entrance
when needed. A candidate is frame-feasible if all subsequent common frames
can be chosen and each final frame lies in its fixed terminal cap.

## Least forward closure is exact for legality

At a scalar event touching registers R with original frame Q, set

    F_new(r) = Q + sum_(s in R) F_old(s)       for every r in R.

At a later native event on r with original entrance U and fixed map G, set

    W = U + F_old(r),       F_new(r) = G W.

Other registers keep their frames. Seed warp0 with F_new(243)=G0 U'.
These transformations preserve inclusion: joins and images of subspaces
are monotone. Induction shows that this closure is componentwise contained
in every legal completion with the same seed U'. Indeed every candidate
scalar frame contains the displayed join, and every candidate native
entrance contains W, so its exit contains G W. Thus a least-closure failure
of a fixed terminal cap excludes every completion for that U'. Conversely,
if all least frames lie in their caps, these explicit choices, paid entrance
climbs and final climbs give a legal frame assignment. This establishes
minimality for legality, without asserting minimum monetary or moment cost.

In particular, if U1 is contained in U2, every least frame for U1 is contained
in the corresponding frame for U2. Failure at U1 persists at U2. This fact
does not require the larger seed to have only one extra dimension.

## Backward capacities give the exact maximal seed

Start with capacity C_r equal to the fixed terminal cap of each register.
These capacities characterize the incoming states from which some legal
completion exists: precisely those with F_r contained in C_r for every r.
Process events in reverse order, using the following exact rules.

For a scalar event touching R with original floor Q, let

    K = intersection_(r in R) C_r.

Require Q contained in K, then replace every touched capacity by K. The
common frame Q+sum F_r lies in every outgoing capacity exactly when Q and
each incoming F_r lie in K. Untouched capacities retain their values.

For a native event on r with original entrance U and invertible map G, let

    K = G^(-1)(C_r).

Require U contained in K, then replace C_r by K. There exists an entrance
W containing U+F_r with G W contained in the outgoing capacity exactly when
both U and F_r lie in K. The least choice W=U+F_r attains this condition.
The floor checks are essential: a preimage alone cannot waive the original
native entrance or scalar frame. A failed constant floor makes the entire
fixed-domain suffix infeasible. A valid original word supplies a consistency
check against this failure.

Induction proves the product-of-capacities characterization. Immediately
after warp0, pull lender 243's capacity back through G0 and call it C0.
Check all other frozen incoming frames against their capacities and check
U0 contained in C0. Then the admissible seeds are EXACTLY

    U0 contained in U' contained in C0.

Thus C0 is the unique maximal legal entrance in this domain, independently
of how scalar frames are optimized within the remaining legal capacities.

## Concrete conclusion and independent evidence

The matched, source-authenticated forward and backward receipts establish

    C0 = U0 + span(7),       dim(C0)=5,

Thus there is exactly one nontrivial legal entrance enlargement. Every
dimension-six-or-larger seed is impossible. Equivalently, the five-dimensional
quotient V/U0 has 31 lines; precisely the line represented by 7 is admitted.
Any higher-dimensional quotient subspace contains a rejected line, and
forward monotonicity preserves its failure. The backward intersection and
forward 31-line enumeration are distinct ways to certify the same boundary.
The forward checks also validate all other frozen prefix-register frames.
There are 374 superframes of U0, with quotient-dimension counts
(1,31,155,155,31,1); exactly two are feasible and the other 372 are excluded.
The receipts bind the directly authenticated BASE-WORD, not an inverse
reconstruction of an example or a copied PASS string.

## Billing, semantics and limitations

All centre descents, target cut-level tests and prelude warp resets precede
the changed B suffix. Preserve their original accounting convention. The
retained frame walker bills centre descents without replacing its persistent
current-centre entry; the compiler separately tracks the last served frame.
Do not silently repair that inherited convention or infer a new physical
invoice from it. No centre is touched in B. The sole centre-touching restore
gate is restore[191], on registers 230 and 92. The retained compiler replay
checks that its entire original record, including the eight-dimensional
frame, is unchanged before cancelling centre costs.
FULL cleanup occurs after the terminal tests and cannot rescue their failure.

Changing frames and inserting scalar identities leaves the ordered free
operator product unchanged; recomputed literal inverse cleanup therefore
has the same arbitrary-dirty-input algebraic endpoint. This is a source
operator statement, not a fresh exact-native phase certificate. Realization
at new boundaries inherits PR3929's transported-frame theorem and requires
the prescribed exact lifts/phase recipes for any physical admission claim.

## Exact price and the nonminimal-frame control

With every entrance and terminal climb charged, the canonical completion's
new-minus-original profile is 27 H1 - 14 H2 - H3 + H4, of rank mass zero.
For the power tariff f(r)=r^q, 0<q<1, its price difference is

    27-14*2^q-3^q+4^q = (2-2^q)(12-2^q)+(3-3^q) > 0.

Both summands are strictly positive. The ordinary raw moment has the same
sign, since r*(m/r)^a=m^a*r^(1-a) with q=1-a and m^a positive. This is a
strict loss for this canonical completion at all power tariffs in that
range, not a universal scalar-price obstruction. Indeed the concave tariff
min(r,2) gives the opposite sign, -1, against the original profile.

More importantly, PR3929's published recipe uses the SAME enlarged warp0
entrance and is a legal nonminimal completion within the stated frame-floor
domain. Its original-frame containments, compiled word and stored profile
are checked separately. Canonical-minus-published is

    -H1 + 2 H2 + 3 H3 - 3 H4,

again of rank mass zero. Its sums against min(r,j), for j=1..4, are
(1,3,3,0). For any discrete concave f on {0,1,2,3,4}, with f(0)=0, put
c_j=2f(j)-f(j-1)-f(j+1)>=0 for j=1..3. Direct expansion gives

    -f(1)+2f(2)+3f(3)-3f(4) = c_1+3c_2+3c_3 >= 0.

Every c_j is positive for f(r)=r^q, 0<q<1, so the canonical completion is
strictly MORE expensive than that published nonminimal completion on all
these power tariffs. This is an explicit counterexample to inferring price
optimality from least-frame minimality; it is not a new cheaper supplier.
The published-minus-original price is also strictly positive:

    28-16*2^q-4*3^q+4*4^q = 4*((2-2^q)^2+(3-3^q)) > 0.

Recompiling a retained recipe and authenticating its result does not rerun
the predecessor's native phase calculation.

Larger legal scalar frames can merge later climbs and change prices; their
optimization remains open. No global scalar-price obstruction, complete
owner/idle allocation, fresh native replay, physical caller, recurrence,
supplier, kappa improvement or selected-frontier change follows here.
