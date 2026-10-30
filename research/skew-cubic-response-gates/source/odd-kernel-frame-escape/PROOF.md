# Sharp frame bounds for two actual odd-rank-kernel words

For the pinned ISOLATED odd-rank-kernel words, any general Clifford-frame
retiming with the same unary holonomies, scalar ADD/common-frame topology
and literal physical boundary conditions has native rank mass at least 66f
(q=2) or 120f (q=3). These bounds equal their source rank invoices. They are
sharp in that mathematical retiming model. No new caller is synthesized.

| q | Banks | Ambient axes per f | Parent native arity per f | Path ranks per f | Floor = source rank bill |
| --- | ---: | ---: | ---: | --- | ---: |
| 2 | 6 | 12 | 11 | 12,11,10,11,11,11 | 66 |
| 3 | 8 | 16 | 15 | 15,15,15,15,15,15,15,15 | 120 |

The actual response J has native arity one per tensor coordinate and satisfies
J_f^2=-I with its whole-field Gaussian scalar normalization retained. There
is no even-rank assumption. The parent is the actual F_k J, whose rank is
(m-1)f. Ambient axes are not discarded, and the target is not silently
replaced by an mf-native Fourier transform.

## Fixed-graph distance argument

This instantiates the metric proof in the frozen predecessor
`../pauli-caller-retiming/TRAJECTORY-PROOF.md`. In the full 2mf-dimensional
binary symplectic space let Z be the coordinate-Z Lagrangian, and set

    d(U,V)=mf-dim(U intersect V).

This is an isometry-invariant metric on mf-dimensional subspaces. A Clifford
G has native B-rank d(Z,GZ). Contract each ADD to a common-frame node; both
its incoming and outgoing operand frames have one Lagrangian L_v. Unary
segments form graph edges. The physical input and output gauges are fixed,
or physical monomials preserving Z, so every boundary has L=Z. The target
F_k J occurs inside the fixed source word and is not a free endpoint gauge.

An edge e=(u,v,G_e) has relaxed tariff d(L_v,G_e L_u). For actual Clifford
frame representatives this is the B-rank of the conjugated segment. Any
further split into native children has at least that total rank by
subadditivity. All scalar operations still require their physical scans;
this proof only accounts for native rank mass.

At an ADD, pair the two incoming and two outgoing strands either straight
or crossed. All four ends have the same L_v, so either pairing is legitimate
for a distance proof. This does not swap independent values. Literal
BANK_SWAP events separately transport the physical strand labels. Time
strictly advances, so the chosen pairings partition all graph edges into
exactly n boundary-to-boundary paths without an internal directed cycle.
For a path with chronological edge products G_l ... G_1, triangle inequality
gives

    sum_path d(L_v,G_e L_u) >= d(Z,G_l ... G_1 Z).

The paths cover each edge exactly once. Summing gives the displayed floors.
This argument permits arbitrary Clifford gauges on all mf coordinates,
including gauges mixing tensor coordinates. Only the fixed source
holonomies have the tensor family form needed to scale their exact ranks
by f.

The source rank bills attain these lower bounds. That proves sharpness of
rank retiming of these words; it does not newly admit the source's changed
ISOLATED native operator as a selected recursive child. The source explicitly
leaves that selected-lowering gate open.

## Exact finite certificates and phases

`ODD-FRAME-CERTIFICATES.json` pins the actual source event arrays, their
chronological ADD ordinals, one pairing bit per ADD, every graph edge and
path, physical endpoint bank labels, each full coordinate circuit and signed
Pauli tableau, and all-f scalar phase corrections. The q2 witness has 90
edges and four crossed ADDs among 42; q3 has 132 edges and 17 crossed ADDs
among 62. Discovery stopped after 6 and 64 exact rank proposals. These are
witness-discovery counts, not exhaustive search claims. No frame optimizer
or annealing ran after the witnesses reached the source bill.

A second chronological traversal checks each crossed strand's literal circuit
order, endpoint and phase vector independently of the graph partition. The
literal inverse circuits and negative scalar phase vectors are saved, and
both signed-tableau inverse orders are checked. Every distinct primitive's
inverse is additionally checked with an independent exact Gaussian zero
column in both orders, so the composed literal inverse retains the global
phase. A scalar-i mutant has identity signed tableau but the wrong Gaussian
column and is rejected. These controls do not claim a new complete caller
function proof: the source complete word is an immutable input here.

The all-straight pairings give only 62 and 116, so they do not certify stock.
Deleting a path edge fails exact coverage. Omitting an actual BANK_SWAP
changes the literal physical trajectory and fails the replay. Normal Python
and optimized Python reproduce the same receipt; essential checks use
explicit exceptions.

## Exact covered domain and open gates

The statement is all positive f for the two finite q fixtures, not all q.
The rank bound concerns the same-volume, full-bank query model. A native
moment conclusion would additionally need the stated equal-volume full-bank
normalization and its complete recurrence; no heterogeneous-volume or
striped-query moment bound is inferred. Parent arities 11/15 remain distinct
from ambient 12/16. Borrowed spectator-axis embedding, owner assignment,
proper-child admission, source access, precision, storage and physical
controller costs are separate obligations.

Changed scalar/native chronology, edited unary responses or holonomies,
new helper coupling, nonlocal scalar rewrites across native sites, or changed
physical input/output and owner contracts require a new graph. This is not
a lower bound for every implementation of the same overall function. No
positive moment, compatible BIT supplier, improved kappa or formal-kernel
proof is claimed.
