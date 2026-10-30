# Shared-kernel root fibers force 178 incidences

Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
This is a finite exact certificate and mathematical argument for review, not a
formal proof or a new multiplication construction.

## Statement and literal caller

Let K be any characteristic-zero field. Let C be the evaluation code on the
112 projective E8 root representatives left after the pinned eight-root frame
is removed. If eleven vectors p_i in K^112 span a space containing six
independent vectors of C, then

    sum_i |supp(p_i)| >= 178.

The vectors p_i need not be independent for this theorem. The literal historical
caller is the independent eleven-piece profile (2,2,5,6,6,6,6,6,6,6,6), in the
(6,5) cell of PR3154. It has strict excess sum(w_i-2)=35<36. The inherited
rank-support capacities 2,2,12,20,...,20 total 176, giving a contradiction of
margin two. The preferred five-piece capacity is 56, so the old strict
below-distance-53 quotient-basis test does not apply. The original unchanged
PR3154 `feasible` and `killed` functions are called on this exact profile.

If T is its eleven-dimensional piece span and dim(T intersect C)>=6, then
its quotient dimension is at most five. The six pieces of weights
2,2,5,6,6,6 have union capacity 76<d_2(C)=78. Their span intersects C in
dimension at most one, so its quotient dimension is at least five. Thus the
literal caller has quotient dimension exactly five and intersection dimension
exactly six. These capacities and d_2 are inherited premises, individually
identified below. The new geometric incidence theorem does not depend on d_2
or any rank-support capacity.

## Rational roots and scalar extension

Use doubled E8 roots of squared norm eight. The pinned model has 120 root
lines, rational coordinates, and pairwise inner products -4,0,4 for distinct
representatives. The 112 live columns satisfy sum_r rr^T=112 I_8, so evaluation
is injective over every characteristic-zero field.

Write a basis of a six-dimensional D subset C as evaluations of six independent
linear forms. Together these give a surjective map E:K^8 -> K^6 with
L=ker(E) of dimension two. Let s be the number of FULL 120 root lines in L,
and z the number of LIVE 112 root lines in L. Always z<=s<=3. The two counts
must not be identified: the punctured frame may contain kernel roots.

Ranks of matrices with rational entries are unchanged by extension Q -> K,
since their nonzero minors are unchanged. Thus a collection of rational roots
contained in a K-subspace of dimension d has rational rank at most d. If it
contains d independent roots, its K-span is the scalar extension of their
rational span. Intersections and dimensions of rational subspaces are also
preserved, by solving the same rational linear equations over either field.
This uses no embedding K -> R. Positivity below concerns rational root Gram
matrices only.

The primary exact full-shell closure census proves:

| rank | root-spanned flats by number of lines |
| --- | --- |
| 2 | 2:3780; 3:1120 |
| 3 | 3:37800; 4:40320; 6:7560 |

Every root in a root-spanned flat extends to a basis of that flat, so grouping
all independent bases by canonical rational row space and taking the union
of their root indices gives the complete closure. In particular a full
three-dimensional root space has no five-line closure. An arbitrary
three-dimensional subspace containing five root lines must have root rank
three, and therefore contains precisely a six-root rational flat.

## Two saturated flats cannot meet in a nearly root-free plane

**Lemma.** Two distinct full six-root three-dimensional spaces whose
intersection has dimension two contain at least two common root lines.

Suppose instead that their common root set has zero or one line. Their union
contains at least eleven root lines and spans dimension four. Choose four
independent roots in that union, scaled by one half so their Gram matrix G
has diagonal 2 and off-diagonal entries in {-1,0,1}. All 729 possible symmetric
matrices are enumerated. Sylvester's criterion (ALL leading principal minors
positive) leaves 393 positive definite matrices.

For any root in their four-dimensional span, the vector k of its inner
products with this basis is in {-2,-1,0,1,2}^4 and satisfies

    k^T adj(G) k = 2 det(G).

The inner-product map is injective on that span. Opposite k represent one
root line. These equations give a superset of all actual root lines. Every
case has at most twelve candidates; only 105 cases have at least eleven.
For each of those 105 cases the certificate enumerates every rank-three
candidate closure, verifies its size is at most six, and finds exactly twelve
six-line closures. The intersections of distinct six-line closures have
sizes two or three: 1890 and 5040 pairs respectively across all cases.

For completeness, an actual six-root flat is contained in one of these
candidate closures, and the verified cap six forces equality. Consequently
the candidate roots in the intersection of two such closures are actual
roots in both flats. The certificate's candidate supersets cannot introduce
spurious intersection roots in this argument. The asserted zero/one
intersection is impossible, proving the lemma.

For two different nonzero projective E-fibers, their preimages E^-1(Kv) are
three-dimensional and intersect in L. If both contain six full roots, they
are scalar extensions of rational root flats and the lemma applies.
Therefore when s<=1, at most ONE distinct nonzero projective fiber can have
a six-root preimage. This is a bound on distinct fibers, not on piece indices.

## Orthogonal two-root kernel planes

If s=2, the two kernel roots are orthogonal. A nonorthogonal pair a,b has
inner product +/-4 and a-sign(a dot b)b is a third E8 root in their span;
this is verified directly against the pinned shell. Hence L is the scalar
extension of a rational orthogonal-root plane.

For every one of the 3780 orthogonal pairs, the primary verifier groups all
120 full roots by their nonzero projective images under the exact rational
projection

    r -> 8r - (r dot a)a - (r dot b)b.

Every plane has the identical nonzero class-size histogram

    6 classes of size 4, 32 classes of size 2, 30 classes of size 1.

The largest eleven classes contain 6*4+5*2=34 roots. The independent verifier
constructs the root shell afresh and instead eliminates two pivot coordinates
to represent the quotient; all 3780 partition digests agree. Thus neither
transitivity of the punctured model nor an unproved Weyl reduction is used.
Deleting the eight frame roots only decreases any fiber population. Scalar
extension preserves equality and proportionality of rational quotient
vectors, so the same bound holds over K.

## Grouped singleton incidence count

Choose lifts of the six D basis vectors to the eleven piece coefficients.
Let v_i in K^6 be the coefficient column for piece i. At a coordinate r,

    E(r) = sum_i v_i p_i(r).

Call a live site active when E(r)!=0. There are N=112-z active sites. An
active site with exactly one nonzero p_i(r) has E(r) proportional to the
nonzero v_i. Group piece indices by the projective class K v_i, discarding
zero v_i. The singleton sites of pieces in the same group are DISJOINT and
all lie in one projective E-fiber. Thus the total number u of active singleton
sites is bounded by the sum of populations of at most eleven DISTINCT
fibers. Repeated or proportional coefficient columns never multiply the
population of one fiber. A zero v_i cannot contribute an active singleton.

Every other active site contributes at least two piece incidences, so
M=sum_i |supp(p_i)| >= 2(112-z)-u. Zero-evaluation sites, including any
cancellations among nonzero pieces, only add incidences and may be omitted.

| s: full kernel roots | upper bound on u | z bound | lower bound on M |
| --- | --- | --- | --- |
| 0 | 6+10*4=46 | 0 | 178 |
| 1 | (6-1)+10*(4-1)=35 | 1 | 187 |
| 2 | 34, exact orthogonal-plane certificate | 2 | 186 |
| 3 | 11*(6-3)=33 | 3 | 185 |

For s<=1, the saturated-flat lemma and the absence of five-root closures
bound all but at most one fiber by four full roots INCLUDING the s kernel
roots. For s=3, the rank-three cap six suffices. Fewer than eleven distinct
nonzero fibers only improves the bounds. The minimum is 178, as claimed.

## Corollary: the rank-at-most-six strict-deficit branch

Suppose there are at most eleven pieces, their binary support ranks have
bounds w_i in {2,3,4,5,6}, and sum_i(w_i-2)<36. Then their span cannot contain
six dimensions of C, conditional on the inherited support capacities

    g(2),g(3),g(4),g(5),g(6) = 2,4,8,12,20.

The first three capacities follow because distinct labels have leading bit
one, and a binary w-space has at most 2^(w-1) vectors in that affine slice.
The last two are the pinned analytic capacities credited below.

Pad the actual piece list to eleven with zero vectors. This preserves its
span and total support, so the 178 theorem applies without requiring
independence. Assigning each padded zero the loose upper capacity g(2)=2
only increases the proposed total upper bound and costs zero excess.

Put c=w-2 and h(c)=g(c+2)-2. For c=0,1,2,3,4, the values of h are
0,2,6,10,18, with successive increments 2,4,4,8. They are nondecreasing.
Whenever two entries satisfy 0<c<=d<4, replacing (c,d) by (c-1,d+1)
preserves the excess budget and does not decrease total h. Repeating these
transfers concentrates the budget into entries equal to four and at most
one remaining positive entry. Since h is strictly increasing, the maximum
under an eleven-slot budget at most35 uses exactly35. It is attained at

    c = (0,0,3,4,4,4,4,4,4,4,4),
    sum g(w) = 22 + 10 + 8*18 = 176 < 178.

An exact budget dynamic program and a separate exhaustive multiset check
confirm every length from zero to eleven and the unique sorted eleven-slot
maximizer w=(2,2,5,6,6,6,6,6,6,6,6). Thus the literal caller chosen above is
extremal for this entire explicitly bounded branch. This corollary needs
no claim about historical-filter completeness or other shortening results.
It permits neither weight-seven pieces nor more than eleven pieces, and
does not close full C5 or establish a new multiplication algorithm.

## Scope, dependencies and credit

The E8 geometry and evaluation-code line are inherited from DavidArias's
root-code program and joaqcoo's root-simplex model. NickPetalas's PR3269
(ebe02d33157dc6c6d3b35df204e4a39242b7429e) and the mainline quadratic-support
proof supply capacities 12 and 20; capacities 2 are immediate. DreamingOfClouds's
PR3154 (708f0ad8928c383de8294aea3c126e9461d2066d) supplies the literal filter,
cell convention, and the inherited second generalized weight 78. The pinned
source manifest identifies exact local bytes; no predecessor source is edited.

PR3991 (e4eb3b7a1334b6fef88fc251c43d9940c8d38de8, Chris R / Clear1nsight with
Codex) introduced the six-dimensional singleton/pair incidence framework and
floor 164. This work reuses that framework and rational elimination, replacing
separate fiber capacities with a simultaneous shared-kernel restriction.
It raises the uniform eleven-piece floor by 14, and binds one different
literal profile of capacity 176. This is E8 root geometry and generalized
support-weight coding theory combined with incidence geometry of intersecting
three-planes, not an enlarged common-cut inventory.

Overlap was checked against the parent session's 702 open-PR body snapshot
at 08:35 UTC on 2026-10-19, nearby C5 handoffs, and local exact-profile searches.
This does not certify that every historical argument in every discussion is
absent. No full (6,5) cell closure, global C5 proof, or priority change is
claimed. Human or formal review of the argument and inherited capacity/d_2
premises remains required. The theorem restricts a decoder/rank-shape route;
it supplies no faster multiplication algorithm and no improvement to selected
kappa 0.001672660197076918.

### Bounded caller-overlap screen

For this exact profile, every five-piece capacity sum is at least56, so
normalizations requiring a certified quotient basis of support below53 do
not apply on capacity data alone. Every four-piece sum is at least36,
blocking the common-cut29 rank-six triple and common-cut30 six-endpoint
contracts (and the smaller four/five-endpoint cut29/28 bounds). Mixed566
endpoints leave minimum four-small-piece capacity44>35; mixed556 leave
62>39; three rank-at-most-five endpoints leave80>47. Thus the published
PR3262, PR3205, PR3278, PR3368 and PR3283 shortening applications used in
the preceding stream do not certify this profile through those capacity
sums. The six-piece concentration lemma requires four endpoints of rank
at most five, while this profile has only three such pieces. Deleting to a
ten-piece or nine-piece caller loses a guaranteed code dimension per deleted
piece, so a six-dimensional exclusion at the smaller length is not directly
applicable. These are scoped application checks, not proofs that no other
public argument can exclude the profile. They are not inputs to the new178
incidence theorem.
