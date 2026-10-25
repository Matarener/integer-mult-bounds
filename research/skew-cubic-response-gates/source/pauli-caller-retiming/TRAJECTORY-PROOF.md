# Exact trajectory bounds for fixed common-frame words

This package certifies a rank-mass lower bound for the eight pinned finite
words in `TRAJECTORY-CERTIFICATES.json`. It does not search for a new caller.
The Pauli-response DEFAULT and ISOLATED words at q=2 and q=3 are sharp in
the stated retiming model: the lower bounds are respectively 60 and 112,
equal to both their saved native bills and their endpoint stocks. The older
repaired and admitted two-site words receive valid but weaker bounds 62 and
118. Those bounds do not establish their optimality.

## Model and boundary

Fix a complete chronological word on n arbitrary fields. Its gates are
literal unary Clifford families, scalar field ADD/SCALE, and literal
BANK_SWAP. Every source unary family is specified as an actual coordinate
circuit, its signed Pauli tableau, and the scalar correction to its f-fold
tensor power. Fix those unaries and the scalar ADD topology. This is not a
model in which the unaries can be replaced by other operators having the
same final overall function.

At every ADD, its two operands must have one identical Clifford frame
representative. The graph relaxation retains only that they have the same
Lagrangian frame; allowing all Lagrangians is a relaxation of the literal
frame constraint. Scalar coefficients commute with the address operators.
Every SCALE and BANK_SWAP remains a paid whole-field operation. The native
rank tariff alone assigns them no positive rank.

The original physical inputs and final physical outputs are fixed. Their
frame gauges are therefore identity, or, harmlessly for this relaxation,
physical monomials preserving the coordinate Z Lagrangian. In particular the
Pauli target FJ already occurs in the fixed source word. Its rank is 10f in
ambient 12f for q=2 and 14f in ambient 16f for q=3. It is not replaced by a
full ambient Fourier transform, and its two spectator axes are not discarded
or charged as independent public progress. The corresponding endpoint stocks
are n times 10 and n times 14. A variable right input gauge or a changed
terminal owner contract is outside the present boundary.

## The distance and edge tariff

Let Z be the coordinate Z Lagrangian in the 2mf-dimensional binary symplectic
space. For two mf-dimensional subspaces set

    d(U,V) = mf - dim(U intersection V) = rank(span(U,V)) - mf.

This is a metric on subspaces of the given dimension. Indeed

    dim(U intersection W) >= dim(U intersection V)
                              + dim(V intersection W) - mf

gives its triangle inequality. Every invertible linear map acts by isometries.
For a Clifford G,

    native_rank(G) = rank(B_G) = d(Z,G Z).

Contract each ADD to one common-frame node. Keep each maximal unary segment
as an edge e=(u,v,G_e), and keep all physical input/output boundaries at the
fixed node 0. BANK_SWAP transports the pending segments and physical strand
labels; it is not silently omitted. An edge can also be an identity segment.
At an arbitrary retiming assign a Lagrangian L_v to every node, with L_0=Z.
The edge native tariff is

    c_e = d(L_v, G_e L_u).

For actual frame representatives T_v with L_v=T_v Z, this is exactly the
native B-rank of T_v^-1 G_e T_u. Splitting the segment into more native
queries can only increase total rank mass by rank subadditivity. Thus this
edge-tariff model also lower-bounds such splittings. It does not give the
concave positive-exponent moment: different splittings can change that bill.

## Boundary-to-boundary strand bound

Partition every edge into directed paths from node 0 to node 0. Internal ADD
nodes have two incoming and two outgoing strands. They may be paired either
straight or crossed, because all four ends carry the same L_v. For a path
with edge operators G_1,...,G_l in chronological order, the triangle inequality
and isometry give

    sum_path c_e >= d(Z, G_l ... G_1 Z).

One way to see the telescoping explicitly is to pull the frame at the j-th
node back by (G_j ... G_1)^-1. Consecutive pulled-back distances equal c_e,
the initial pulled-back frame is Z, and the terminal one is
(G_l ... G_1)^-1 Z. Its distance from Z equals the displayed right side.

The paths are edge-disjoint and exhaustive. Summing their bounds therefore
counts each edge tariff once, with no assumption that their value contents
are independent, copied, or zero. The path holonomy is a graph invariant;
it is not asserted to be an entry of the complete caller matrix. The proof
uses arbitrary original inputs only through the fixed physical endpoint and
common-frame gate contract.

The producer uses straight pairing at all actual ADD nodes and transports
strand identities across each actual BANK_SWAP. It saves every edge, path,
signed holonomy tableau, full literal coordinate circuit, and tensor-phase
correction. An independent traversal of the physical labels checks circuit
order and all scalar phase corrections. Global Clifford phases and field
SCALE factors do not affect the subspace distance; they are retained or
counted separately, not used to declare scalar-equivalent operators equal.

## Exact fixtures

The ranks below are in *initial strand label* order. A list in final physical
bank order can be a permutation of the same multiset.

| Family | q | Holonomy ranks per f | Floor | Source mass | Stock |
| --- | --- | --- | ---: | ---: | ---: |
| Pauli DEFAULT | 2 | 8,10,10,10,10,12 | 60 | 60 | 60 |
| Pauli DEFAULT | 3 | 12,14,14,14,14,16,14,14 | 112 | 112 | 112 |
| Pauli ISOLATED | 2 | 8,10,10,10,10,12 | 60 | 60 | 60 |
| Pauli ISOLATED | 3 | 12,14,14,14,14,16,14,14 | 112 | 112 | 112 |
| Repaired SIMPLIFIED | 2 | 8,10,10,10,12,12 | 62 | 80 | 72 |
| Repaired SIMPLIFIED | 3 | 12,14,14,14,16,16,16,16 | 118 | 136 | 128 |
| Admitted two-site | 2 | 8,10,10,10,12,12 | 62 | 76 | 72 |
| Admitted two-site | 3 | 12,14,14,14,16,16,16,16 | 118 | 132 | 128 |

For the four Pauli fixtures the original gauge assignment reaches the floor,
so the lower bound is sharp over *all* Clifford Lagrangian gauges. This is
stronger than a finite generator search. It does not newly admit selected
native recipes for the ISOLATED changed unary: those events are used as
literal Clifford words and the source's explicit admission limit is retained.

The proof is all-positive-f for each listed finite q fixture. Its holonomies
are tensor products up to the saved global phases, so the B-ranks scale by f.
Arbitrary retiming frames may mix tensor coordinates: the metric proof still
takes place in the full mf-dimensional space and does not impose a tensor
ansatz on those frames. No all-q formula is inferred from q=2 and q=3.

## Controls and limits

Every fixture rejects an omitted path edge and a specific actual BANK_SWAP
whose strand transport is omitted. All frozen input pins and the native-rank
invoice are checked without floating-point arithmetic. `python -B` and
`python -B -O` reproduce the same saved result; the checks use explicit
exceptions, not assertions that disappear under optimization.

A new response, changed unary holonomies, a nonlocal scalar rewrite across
native sites, new helper interactions, or an altered owner/input/output
contract requires a new graph and certificate. In particular the weaker
62/118 bounds do not close the old original-kernel caller. This package
establishes no new kappa, joint BIT compatibility, rounding, source access,
physical machine controller, storage, or complete supplier admission.
