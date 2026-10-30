# A census-free pair-reader floor for even orthonormal partitions

## Claim and exact scope

Take any finite indexed set of n ports carrying labels in F2^d. Partition the
ports into groups, each of positive even size, whose within-group Gram matrix
is the identity. Consecutive ports of a group form complete Gram-I2 planes.
Its two alternating halves give scalar indicator vectors. Write all these
vectors as v_c and put K = sum_c v_c v_c^T. No condition on cross-group
pairings or on the number or sizes of the groups is required.

Let a,b be two distinct indicators. Their scalar supports are disjoint. Their
complete groups have sizes m_A,m_B and may coincide. Over an arbitrary
coefficient field F, suppose a finite list satisfies

    aa^T + bb^T = sum_i u_i q_i^T,
    q_i = x_i a + y_i b.

Readers u_i are arbitrary vectors on all n ports. They may cancel outside
supp(a) union supp(b). Query count, projective direction count, coefficients,
repetitions, signs, denominators and characteristic are unrestricted.

For any vector v, cl(v) includes both ports of each plane touched by a nonzero
entry. The actual-reader tariff is the binary rectangular rank

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Then

    sum_i C(u_i,q_i) >= m_A + m_B.

The original two terms attain this floor. Disjoint replacements of indicator
pairs by arbitrary finite lists in their pair spans cannot lower the literal
whole-K total 2n. This is a sharp lower bound for this additive support tariff.
It does not price a physical implementation.

The concrete replay specializes this conditional theorem to the 112 selected
P112 labels and Tekalign's PR3370 sixteen-group fixture, giving whole-K total
224. The theorem requires no census of that fixture's pairings. Concurrent
PR3459 reports the same literal P112 conclusion through submodular support
layers and an exhaustive rank census. The new contribution here is the
extension-field proof for every even orthonormal partition, independent of
that finite census.

## Transfer all projective classes to characteristic two

Discard zero queries. They contribute neither to the operator nor to its tariff.
Group the remaining queries by their projective pair [x_i:y_i]. Let D_j be a
class and S_j its common source closure. Scalar multiples have the same closure.
Since a,b have disjoint supports, an axis class has source closure G_A or G_B;
every nonaxis class has source closure G_A union G_B.

Use the rational function field L = F2(t). Keep each occurring axis fixed.
Map the finitely many nonaxis classes injectively to

    d_j = (1,t^j), j = 0,1,...,

using a different exponent for each nonaxis class. These pairs are nonzero,
nonaxis and pairwise nonproportional in L squared. Thus every two different
class images span L squared. Set q'_j = d_j1 a + d_j2 b over L. Its source
closure is S_j. No homomorphism from F to L is asserted or needed.

At a port p, the old operator gives

    sum_i u_i(p) (x_i,y_i) = (a(p),b(p)).

Call a class active at p if at least one of its original readers is nonzero
there. Outside both target supports, set all new readers to zero. At a target
port, the right side is a coordinate axis. There is at least one active class.
If only one class is active, its old direction must be that target axis. Its
image is fixed, so one new coefficient realizes the target. If at least two
classes are active, select two. Their images are independent over L, so their
unique two coefficients realize the target. Set every other coefficient to zero.
Doing this separately at every port constructs L-valued readers u'_j with

    aa^T + bb^T = sum_j u'_j (q'_j)^T,
    supp(u'_j) subset union_{i in D_j} supp(u_i).

This argument works for every finite original direction list. It does not claim
that a fixed finite field represents arbitrarily many distinct directions.

## Compare the original binary support bills

Deleting rows or columns of a binary matrix cannot increase its binary rank.
For any fixed source set S and finite reader sets T_i, horizontal concatenation
gives

    rank_F2 Gram(S, union_i T_i) <= sum_i rank_F2 Gram(S,T_i).

Plane closure respects inclusion and finite unions. Applying these facts within
each projective class yields

    C(u'_j,q'_j)
      <= rank_F2 Gram(S_j, union_{i in D_j} cl(u_i))
      <= sum_{i in D_j} C(u_i,q_i).

Although the new coefficient field is L, C is still the same binary rank
of complete-plane supports. Summing shows that the L-valued replacement's
binary tariff is no greater than the original F-valued tariff. Reader entries
outside the target, cancellations among proportional readers, and repeated
queries cause no gap in this comparison.

## The expanded identity works over every characteristic-two extension

For a scalar n-by-n matrix M over L, expand each scalar port into two plane
coordinates and replace M_pq by M_pq times the binary 2-by-2 Gram block of the
planes at p,q. Interpret each binary entry through F2 subset L. This is L-linear.

The expansion of K is I_(2n). A diagonal scalar entry contributes I2. An
off-diagonal nonzero K entry joins different planes within one orthonormal
group, whose Gram block is zero. The two ports of one plane lie in different
alternating halves, so their off-diagonal K entries are zero. These cases cover
every entry. This is the expanded-identity argument retained from Philippe
Van Velzen and PR3345; the extension of its coefficient field is the step used here.

The expansion of an L-valued term u q^T factors through the binary rectangular
Gram matrix between cl(q) and cl(u), up to transposition. Select and repeat
source plane columns at source ports and scale by q's entries. Repeat reader
rows at reader ports and scale by u's entries. This gives exactly its expanded
blocks. Therefore the expanded term has L-rank at most

    rank_L Gram(cl(q),cl(u)) = rank_F2 Gram(cl(q),cl(u)) = C(u,q).

The equality holds because extending a field preserves matrix rank. A binary
matrix has the same nonzero minors over F2 and L, and every larger binary
minor that vanishes over F2 still vanishes in characteristic two. This equality
would not follow by interpreting the matrix in a characteristic-zero field.

Append all untouched literal indicator terms to the new pair realization.
It now realizes K over L. Rank subadditivity and rank_L(I_(2n)) = 2n imply a
total tariff of at least 2n. Untouched terms cost 2n-m_A-m_B, because each
indicator's closure is its orthonormal group. The replacement pair therefore
costs at least m_A+m_B. Its original F-valued bill is at least as large by the
previous comparison. The original a,b terms attain equality over every field.

## What changes relative to the predecessors

CubeJerry's concurrent PR3459 at d1703ebc3f5c0e0b47fa37066a2288367402973a
normalizes axes, applies submodular uncrossing and checks 435,456 states for
the fixed PR3370 fixture. Its proof and scope were inspected during submission
overlap checking; its implementation was not replayed. It has independent
credit for that literal mixed-list result. This theorem removes the finite
geometry census and applies to any even orthonormal partition. It does not
claim the literal mixed-list conclusion is new relative to PR3459.

PR3429 at ffd6d6a9060e12fe7b7854f90aca7f8aa4ca211d mapped at most three
projective directions into F2 squared. Its twelve-site example correctly
rejects such a binary replacement for four arbitrary direction classes.
Mapping into L squared instead supplies as many distinct directions as needed.
The old binary-map obstruction does not obstruct the extension-field map.
The separate checker replays those twelve requests over GF16 as a concrete
control, while confirming that no binary assignment solves them.

PR3447 at 924f3b50741ba2f6dc005b1dee4c9219665296f2 treats arbitrarily many
dense directions, proving the stronger dense-only bound 2 max(m_A,m_B).
The present sharp m_A+m_B bound includes mixed axis/nonaxis lists without a
direction-count limit. It leaves the stronger dense-only statement intact.

PR3383's query self-Gram bound concerns a different quantity. This proof uses
actual readers throughout; it does not transfer a self-cost bound term by term.
No pending predecessor implementation is imported. The geometry fixture is
retained byte-for-byte with its attribution, and the expanded identity is checked
from the selected labels and that fixture.

## Evidence and limits

The written argument proves the universal statement. Finite checks corroborate
its source geometry, support transfer, operator identity and tariff comparison.
They do not turn the rational function field into a fixed finite-field bound.
Independent human and formal proof-kernel review are unclaimed.

Queries outside the pair span, fitting matrices outside the stated recipe,
larger jointly recoded blocks and shared nonadditive native operations remain
separate questions.
This proof does not supply native acquisition, coefficient execution, frames,
dirty restoration, hosting, stock, precision, all-size/compiler admission,
either complete supplier or the outer multiplication theorem. No new kappa or
selected-frontier change is claimed.
