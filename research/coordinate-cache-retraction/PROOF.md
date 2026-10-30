# Coordinate reduction of a cache tree

This proof and its finite checker were produced by Nick Petalas.

## Contract and result

Let K be any field, including characteristic two. Let V=K^(2n), n>=1,
with symplectic basis e_1,...,e_n,f_1,...,f_n and alternating form
<e_i,f_j>=delta_ij. A chart is an n-dimensional isotropic subspace.
Its paid rank distance is

    d(L,M) = n - dim(L intersect M).

The use of this distance for binary Clifford transports, and the typed-copy
contract distributing one unchanged logical snapshot, are cited from zxv's
PR5283. This proof does not re-establish its native compiler or physical
contract. The all-field statement below is linear algebra; its direct
Clifford application is over F2.

A coordinate chart chooses one vector from each pair {e_i,f_i}. Write A for
the set of these 2^n charts. There is an explicit map R from every chart to A
such that

    R(A) = A for every A in the coordinate set,
    d(R(L),R(M)) <= d(L,M) for every pair of charts.

Consequently a finite tree with fixed coordinate terminal charts and arbitrary
intermediate charts has a coordinate-labeled replacement with the same tree
and no larger paid cost, for any nonnegative nondecreasing tariff on each
edge. Tariffs may differ between edges. This includes r^s for every s>0,
with 0^s=0. Concavity is not required.

The contribution is this search reduction for the cache contract. Echelon
pivots and initial-subspace arguments are elementary linear algebra. No claim
of priority for those general ideas or for building retractions is made.

## 1. The pivot map

Order coordinates as

    c_1,...,c_(2n) = e_1,...,e_n,f_n,...,f_1.

The reversed order of the f coordinates matters. The only nonzero coordinate
pairings have indices summing to 2n+1, and their values are units 1 or -1.

For any subspace W, take a row-reduced echelon basis in this order. Let P(W)
be its pivot positions, and define

    I(W) = span{c_j : j in P(W)}.

A nonzero linear combination of echelon rows has its first nonzero coordinate
at the first pivot whose row has nonzero coefficient. Therefore P(W) is exactly
the set of possible first nonzero positions of nonzero vectors in W. It
follows that |P(W)|=dim W and, whenever W is contained in U,

    P(W) is contained in P(U).

In particular

    P(U intersect W) is contained in P(U) intersect P(W),
    dim(U intersect W) <= dim(I(U) intersect I(W)).             (1)

A coordinate subspace is fixed by I.

## 2. Isotropic spaces stay isotropic

Suppose an isotropic W had complementary pivots i,j with i+j=2n+1.
Choose their echelon rows u,v, normalized to have leading coefficient one.
Every supported coordinate of u has index at least i; every supported
coordinate of v has index at least j. A nonzero term of <u,v> requires the
two coordinate indices to sum to 2n+1. Since i+j already has that value,
the only possible term is the leading pair i,j. Its coefficient is 1 or -1,
which is nonzero in every field. This contradicts isotropy.

Thus P(W) contains no complementary pair. For an n-dimensional chart L,
there are n pivots among n pairs, so exactly one position in each pair is
chosen. Hence I(L) is a coordinate chart. Define R(L)=I(L). Equation (1)
proves the distance inequality. Since coordinate charts are fixed, R is a
retraction. Its Lipschitz constant one is sharp: opposite coordinate charts
remain at distance n.

This argument proves every field and dimension directly. The finite census
is corroboration, not an extrapolation to those quantifiers.

## 3. Retraction of an entire tree

Fix any finite tree T and any assignment L_v of charts to its vertices.
Every prescribed terminal must lie in the same coordinate set A. Replace
L_v by R(L_v) at every vertex. Terminals are fixed, and each edge uv obeys

    phi_uv(d(R(L_u),R(L_v))) <= phi_uv(d(L_u,L_v)).

Sum over edges. The tree, its vertex count, and its terminal assignments
are unchanged; internal vertices or zero-rank edges need not be deleted.
For each fixed topology the two exact minimum costs agree, because every
unrestricted assignment retracts and every coordinate assignment was already
allowed. Over all finite topologies their infima also agree. Existence of a
global optimizer is not needed for the replacement claim.

In the abstract typed-copy contract, each vertex still represents the same
snapshot in its newly chosen chart. Implementing the changed transports
requires the predecessor's exact phase and ordinary-operation contracts.
The inequality prices only the rank-dependent edges. It does not bound
ordinary monomial work or certify an emitted physical word.

Fixed productive credits depending only on unchanged terminals can be
subtracted from both sides. A negative term depending on a variable internal
edge, such as -d^s, reverses monotonicity and is not covered. Nor are additional
restrictions on intermediate charts unless the map preserves them.

## 4. Connection to canonical coordinate-subspace frames

PR5283 gives the canonical binary chart

    Lambda(U) = {(x,x+z) : x in U, z in U-perp}.

If every required U is spanned by a subset of one standard coordinate basis,
these charts choose between (e_i,e_i) and (0,e_i) independently for each i.
Those are paired vectors of a common symplectic basis. They satisfy the
hypothesis above. Arbitrary subspaces U, or arbitrary terminal charts, need
not share such a basis. No claim that a selected caller has this property
is made here.

## 5. Finite evidence and failure boundaries

The checker enumerates row-reduced bases rather than sampling charts.
Distances are independently computed by enumerating vector spans and counting
their literal intersections. It checks the intersection-leading inclusion,
all ordered chart pairs in the registered domains, retraction idempotence,
and the complete coordinate image. Finite monotone tariff tables and a
four-terminal tree census corroborate the cost consequence.

The self-dual coordinate order cannot be discarded. In interleaved order
(e_1,f_1,e_2,f_2), the isotropic plane spanned over F3 by
(1,0,1,0),(0,1,0,-1) has pivots e_1,f_1. Their coordinate span is not
isotropic. Reordering to the stated self-dual order repairs this example.

Two distinct lines span(e_1) and span(e_1+f_1) over F2 have distance one
and retract to the same line. Thus a decreasing tariff or a negative
internal-edge credit can increase. The second line also shows that a
non-coordinate terminal need not remain fixed. These are explicit scope
controls, not a universal obstruction to changed contracts.

Physical movement, dirty restoration, ownership, source-row lifetimes,
precision, native phases, compiler closure and the complete signed supplier
invoice remain separate obligations. No new kappa or complete multiplication
theorem follows from this rank-only reduction.

## Credit

Credit zxv for PR5283's snapshot tree, paid Lagrangian metric and cache cost
interface; Matarener for PR5060's preceding center-intersection argument;
Dugongue for PR4534's owned-center retiming contract; and the native, helper,
compiler and supplier contributors retained in PR5283's source notices.
The predecessor files are cited as immutable provenance, not imported or
replayed. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
