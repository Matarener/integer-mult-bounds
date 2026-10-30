# Adapted t=3,d=3: every all-low actual profile of inside sum at most 32

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

This proof uses the actual-basis contract of PROOF.md and the immutable
written dependencies in DEPENDENCIES.md. ADAPTED-T3-HIGH.md treats actual
high-containing profiles; MERGE.md treats all-low inside sum 33. Together
these notes cover the complete adapted t=3,d=3 branch.

## 1. Contract, scope, and actual ledger

Use the characteristic-zero actual-basis contract of `PROOF.md`.
Here `dim S=11`, `dim C=8`, `dim(C intersect T)=3`, and the threshold space T
spans all S-words of binary support rank at most seven. Assume `r=0`, so
the six actual inside members form a basis of T, while the five actual
outside members have ranks eight or nine. Assume all six inside ranks
are at most seven, their sum is `Sigma<=32`, the raw sum is at most 73,
and, for contradiction, the actual invoice is at most 64.

The theorem of this note is that these assumptions are inconsistent.
It covers every such all-low actual profile, not merely minimum bases.
It leaves inside sum 33 and high-containing actual inside profiles to
separate arguments.

Write `c9` for the number of actual outside rank-nine members, `nT` for
the number of corrected inside members, and J for the set of corrected
outside frame indices. Since `C+T=S`, restriction from `Ann(T)` to C is
injective, so the five outside restricted duals are independent. In
particular their corrected frame indices are distinct. Let k be the
number of active frame axes on the three-dimensional normal space

    D = {h : C_h belongs to T}.

Then `k>=3`, `k<=8-|J|`, and exactly

    raw = Sigma+40+c9,
    nT+|J| >= Sigma-24+c9.                                   (1)

All piece coordinates below are the actual coordinate functionals on D.
There is no replacement of the actual inside basis by a minimum one.

## 2. Full-root versus live support capacities

The analytic table in PR3689 `p112-six-seven-supplement/PROOF.md`, Section 2, bounds **full-root**
support sizes at ranks 4,5,6,7 by 8,12,20,36. Therefore a corrected piece
of the corresponding rank has live support size at most 7,11,19,35:
its label span also contains its excluded matched frame-root point.
This conclusion is independent of the coefficient field. In particular,

    corrected rank 7: live support <=35,
    corrected rank 6: live support <=19,
    corrected rank 3: live support <=3.                       (2)

For rank three, the full capacity four is the elementary leading-one
affine-section bound. Rank-one/two members are uncorrected.

We also need a corrected **root-target** bound. Suppose a rank-seven
actual member A is corrected at a and has nonzero coefficient in an
actual expansion of a scalar root word `C_v`.

* If v is nonframe, that nonzero coefficient implies `(f_a,v)!=0`.
  Thus its excluded frame label is in the full root target of v.
  A rank-seven label space meets this full target in at most 32 points;
  subtracting that frame point gives at most 31 live target sites for A.
* If v is frame, its nonzero corrected coefficient forces v to be its
  matched frame direction, and the retained matched target bound is 20.

The full-root target capacity 32 is the same analytic calculation as
PR3689 `p112-six-seven-supplement/PROOF.md`, Section 4. If a rank-seven affine section is not
contained in the neighbor hyperplane, its neighbor part has rank at
most six and at most 20 points, with at most one self point. A section
inside that hyperplane has 24,28, or 32 full-root points and misses self.
Thus no live/full distinction is being silently dropped here.

Retained inputs used below are the code distance 53, root rigidity
`|Off(h)|<70 => h is a root direction`, the four-axis rigidity bound,
and the fact that nonframe roots have four active frame axes. For any
normal with two or three nonzero frame coordinates the support is at
least 76, so a normal on at most three axes with at most 75 support sites
is a frame direction. Frame words have 56 live sites, and a seven-flat
has frame-target capacity at most 32, or 20 if matched and corrected.

## 3. Complete inventory for actual inside sum at most 32

First exclude six actual ranks at most six. If the smallest rank is at
most four, kill one of the other coordinates in D. The remaining span
has code intersection at least two and consists of four rank-at-most-six
pieces plus the smallest piece on at most eight sites. This contradicts
the source `CALLERS.md` appendix, **Four-six-plus-nine lemma**.

Otherwise all six ranks are five or six. Since their sum is at most 32,
at most two can be six. Killing the two largest coordinates in D leaves
a nonzero codeword in four rank-at-most-five pieces, with support at
most `4*12=48<53`. This is also impossible. Therefore a seven occurs.

Delete one actual seven coordinate. The remaining five independent
pieces have code intersection at least two and total weight at most 25.
The intrinsic five-piece exhaustion used in source `D2.md` can be stated
directly for these actual weights:

* With no seven, four-six-plus-nine handles a smallest rank at most four;
  otherwise the sum bound forces `55555`, and killing one coordinate
  leaves at most 48 sites.
* With exactly one seven, kill it. Capacity 53 for the remaining four
  ranks of total at most 18 forces `6651`. The resulting `76651` is
  excluded by `RIGIDITY.md`, Section 7.
* With exactly two sevens, write `77abc`, where `a+b+c<=11` and `a<=6`.
  Killing one seven, the crude and root-target capacities exclude
  `a<=4` and leave only `541,542,551` when a=5 and `631,632,641`
  when a=6. The smaller `6bc` possibilities have `g(b)+g(c)<=4`
  and are excluded by the source sharp `(7,6)+four-sites` theorem.
* With three sevens, the last two positive ranks sum to at most four,
  leaving `77711,77721,77722,77731`.

For clarity in the a=6 row, the smaller possibilities are `622,621,611`:
their last two actual supports have union size at most four. The profile
inventory therefore follows from intrinsic rank/support statements;
it assumes no minimum-basis normalization or historical list completeness.

Adding back the deleted seven gives exactly these ten candidate actual
profiles:

| Sigma | Actual inside profiles |
|---:|---|
|30|777711|
|31|777721,777541,777631|
|32|777722,777731,777542,777551,777632,777641|

These are necessary profiles only; the table makes no existence claim.

## 4. The four-seven argument permits several small pieces

The four-seven lemma in `ADAPTED-T2.md` remains valid when the small
piece is replaced by any family supported in a common set E of at most
three sites. Every use of that piece in its proof concerns only the
support of the total error term, which remains inside E. In particular:

* Any three of the four seven-coordinate restrictions are independent,
  since their joint kernel would leave one seven plus E, below distance.
* Every pair kernel uses two sevens plus E and has at most 75 sites.
* The root, A2, and incidence arguments concern these normal kernel
  lines and do not require a single small coordinate or a fixed scalar
  multiple of one small word.

Consequently, with q corrected sevens, the following inherited exclusions
hold with this common error set:

    q=4,k<=6; q=3,k<=6; q=2,k<=5; q=1,k<=4; q=0,k<=3.         (3)

In `777711` the two units are uncorrected and their support union has
size at most two. Equation (1) gives `k<=2+q-c9`, so (3) excludes every q.
In `777721` the rank-two piece and unit are uncorrected, their support
union has size at most three, and (1) gives `k<=1+q-c9`; again (3)
excludes every q. No individual small coefficient must be nonzero.

## 5. Closure of 777541

The three seven coordinates form a basis of `D*`: their joint kernel
would leave ranks `5,4,1`, of capacity 21, below distance. Killing the
other two seven coordinates therefore gives, for each seven A, a
nonzero kernel word in `A+L5+M4+e1`, with A coefficient nonzero. It has
at most `36+12+8+1=57<70` sites, so its normal is a root.

If A were corrected, a nonframe-root target would have capacity at most
`31+12+8+1=52<53`. A frame-root target would instead have capacity
`20+12+8+1=41<56`. Thus every seven is uncorrected.

Only L and M can now be corrected. Since `Sigma=31`, equation (1)
requires at least `7+c9` corrections. There are at most seven, so
`c9=0` and all five outside members are corrected. This confines D to
at most three active axes. Every kernel root above must consequently
be frame. But its frame cover has capacity `32+12+8+1=53<56`, the
final contradiction.

## 6. Closure of 777631, with the full-quarter distinction explicit

Write L for the six-piece, u for the rank-three piece, and e for the
unit. The three seven coordinates again form a basis of `D*`, since
`20+4+1=25<53`. Their three pair kernels have representations

    C_v = alpha A7 + beta L6 + gamma u3 + delta e1,

and at most `36+20+4+1=61<70` support sites. Thus each kernel normal
is a root. Its seven coefficient is nonzero by the coordinate basis
property, and its six coefficient is nonzero because `7+3+1` has at
most 41 sites.

If u were corrected, (2) gives `|supp(u)|<=3`. The common error
`supp(u) union supp(e)` would have size at most four. PR3689
`p112-six-seven-supplement/PROOF.md` sharp five-site supplement forbids any nonzero codeword in
one rank-seven piece, one rank-six piece, and this error. Hence u is
uncorrected.

Suppose L were corrected. Then (2) gives `|supp(L)|<=19`. Put
`E=supp(u) union supp(e)`, of size at most five. On one kernel root
the residual outside `U(L)` and E has at least `53-19-5=29` sites.
Source `PROOF.md`, Section 4, therefore forces `U(A)` to be a full
32-root completion X. It misses the parallel **full** 24-root quarter
Q and any live self point. Section 5's **Quarter lemma** says:

    any rank-six label space meets full Q in at most 16 roots;
    if it contains the self label, its Q capacity is at most 12.

If v were a frame root, all 24 quarter roots would be live, while L
and E could cover at most `16+5=21`, impossible. Thus v is nonframe.
Write f for the number of removed frame roots in Q, so `f<=4`. Its
live quarter has `24-f>=20` roots.

If `ell(v)` belongs to `U(L)`, the stronger quarter bound gives at
most `12+5=17<20`, impossible. Otherwise the live self point v must
belong to E. It lies outside Q, leaving at most four error sites for
the quarter. Thus covering the live quarter forces

    24-f <=16+4=20.

Consequently `f=4`, and L's label space contains at least sixteen
**live** quarter points. Their rank is at least six by the global
rank-five capacity twelve. They therefore span the whole rank-six
space `U(L)`, which is contained in the quarter label seven-space.

But L's excluded matched frame label also belongs to `U(L)`. Every
leading-one root label in the quarter label span is a full quarter
point. This supplies a seventeenth full quarter point in `U(L)`,
contradicting the bound sixteen. Equivalently, all four frame neighbors
are in Q, while orthogonal frame points cannot lie in the quarter
label span. This step counts sixteen live points and then adds one
removed point; it does not confuse the 24-point full quarter with
its 20-point live part, or the live self point with a quarter point.

Hence L is uncorrected as well. Only the sevens can now be corrected.
Let their number be q. Equation (1) gives

    q+|J|>=7+c9,   q>=2+c9,   k<=1+q-c9.

Choose a corrected seven A, and kill the other two seven coordinates.
This kills `q-1` distinct corrected frame axes. Its root normal
therefore has at most `k-(q-1)<=2-c9` active axes and must be frame.
Its nonzero A coefficient makes A matched to that frame. The target
cover has capacity `20+20+4+1=45<56`, a contradiction.

## 7. The two four-seven profiles of sum 32

Any three of the four seven coordinates are independent, because a
joint kernel would leave one seven plus at most five error sites,
below distance 53. Thus both remaining seven coefficients are nonzero
on every pair kernel; corrected seven indices are distinct and active.

For `777722`, both rank-two members are uncorrected and their common
error union has size at most four. Write q for the number of corrected
sevens. Equation (1) gives `q+|J|>=8+c9`, so `q>=3+c9` and `k<=q-c9`.

* If q=4, killing two corrected coordinates leaves at most two axes
  and at most `35+35+4=74` sites. It must be frame, impossible because
  both included corrected seven coefficients are nonzero at distinct
  axes.
* If q=3, the count forces `c9=0,|J|=5,k=3`. The three corrected
  axes span D. Kill one corrected coordinate and the uncorrected
  seven coordinate. The resulting normal has at most two axes and
  at most 74 sites, so it is frame, again impossible because both
  remaining corrected seven coefficients are nonzero.

For `777731`, let delta be one if the rank-three member is corrected
and zero otherwise. Its rank-one partner is uncorrected. Equation (1)
gives

    q+delta+|J|>=8+c9,
    q+delta>=3+c9,   k<=q+delta-c9.

If delta=1, the common error union has size at most four. Then:

* q=4 gives `k<=5`; killing two corrected coordinates leaves at most
  three axes and at most 74 sites, forcing a frame with two distinct
  corrected coefficients nonzero, impossible.
* q=3 gives `k<=4`; the three pair kernels obtained by killing two
  corrected coordinates each have at most two axes and at most
  `35+36+4=75` sites. They must be the three remaining matched frame
  lines. Thus D is the full three-frame space. Killing a corrected
  coordinate and the uncorrected seven now leaves two corrected
  coefficients nonzero on a normal with at most two axes and 74
  sites, impossible as above.
* q=2 forces `c9=0,|J|=5,k=3`. Name the corrected sevens A,B and
  uncorrected sevens Q,R. The kernels `(A,Q)` and `(A,R)` both have
  at most two axes, at most 75 sites, and the B coefficient nonzero.
  Both must be the same matched frame line of B, contradicting
  independence of the three coordinates A,Q,R.

If delta=0, the common error union has size at most five. For q=4,
`k<=4`; killing two corrected coordinates leaves at most two axes and
`35+35+5=75` sites, impossible with both remaining corrected coefficients
nonzero. For q=3, counting forces `c9=0,|J|=5,k=3`, and D is the full
space of the three corrected frame axes. Each such frame word uses
its matched corrected seven A, the uncorrected seven Q, and the error
set. The capacity `20+|supp(Q) intersect N_a|+5` forces Q to contain
at least 31 sites of that frame neighborhood. Applying this to two
distinct corrected axes gives

    |supp(Q)| >=31+31-24=38>36,

using the retained common-neighborhood size 24. This is the final
contradiction for `777731`.

## 8. The four remaining three-seven profiles of sum 32

The following share one argument:

| Profile | Pair-kernel crude support bound | Matched frame-cover bound |
|---|---:|---:|
|777542|36+12+8+2=58|20+12+8+2=42|
|777551|36+12+12+1=61|20+12+12+1=45|
|777632|36+20+4+2=62|20+20+4+2=46|
|777641|36+20+8+1=65|20+20+8+1=49|

The three seven coordinates form a basis of `D*` in every row: the
three other pieces together have capacity at most 29, below distance.
Thus every pair kernel has its remaining seven coefficient nonzero,
and by the middle column every such normal is a root.

Let q count corrected sevens and delta count other corrected inside
members. There is a rank-one or rank-two piece in every row, so
`delta<=2`. Equation (1) yields

    q+delta+|J|>=8+c9,
    q+delta>=3+c9,
    k<=q+delta-c9.

In particular q is positive. Choose a corrected seven A and kill the
other two seven coordinates. This kills `q-1` distinct active corrected
axes, so its root normal has at most

    k-(q-1) <=delta+1-c9 <=3

active axes. It must therefore be a frame direction, and the nonzero
A coefficient makes A matched to it. Every last-column bound is below
56, contradicting the actual frame-word support. This closes all four
rows, independently of which of the two intermediate pieces are
corrected or of possible repetitions among their correction indices.

## 9. Assemble the adapted t=3 conclusion

Every all-low actual profile with inside sum at most 32 is excluded above.
For inside sum 33, MERGE.md reduces a duplicate correction pair to the
already established t=2 budgeted d=2 or d=3 theorem. All high-containing
profiles are excluded in ADAPTED-T3-HIGH.md, using an actual five-member
transfer with code intersection exactly two. These cases exhaust the
inside sum bound 33. Thus every adapted t=3,d=3 bad invoice is impossible.

The proofs use actual independent coordinates and the actual correction
ledger. They do not replace the actual basis by a minimum one. Root-system
rigidity, field transfer, intrinsic exclusions and E8 assembly remain
written dependencies, not consequences of a finite coefficient census.
