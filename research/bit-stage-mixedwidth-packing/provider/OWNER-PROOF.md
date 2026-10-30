# Mixed-terminal owner and controller admission

This is a written exact-stream proof with a complete finite allocation
certificate. It admits the terminal boundary shared by PR4183 and its frozen
five-terminal comparator to the nine-stage, 32-replica controller. It does not
supply an efficient physical recursive caller, a formal-kernel proof, or a new
integer-multiplication exponent.

The source constructions retain their premises and credit. Sagar Thakrar's
PR2423 supplies the R438 allocation and stage demands; Ali Romman supplies the
R438 source word; commdata2338's PR2653 supplies the pending-projector census.
The PR589 whole-call hosting proof, alephnan's PR1627, and the selected
local-ring packet proof, PR2234, supply the common-label, retained-dirty-state
and complete-packet arguments. Eumemic's PR490 is an earlier whole-owner
local-ring argument. The terminal charts and their unit-coordinate lowering
come from the frozen `bit-five-rank4-terminals/admission` supplement. The
selected PR442/386/589/555/545 geometry and controller lineage remains credited.
All consumed input bytes are pinned by this package.

## 1. The exact interface

There are 111 source roles, 111 target roles and 438 independently dirty helper
roles. Helper numbering in this proof is the absolute local register number:

| Helpers | Entrance | Terminal projector | Residual width |
| --- | --- | --- | --- |
| 462, 463, 464 | 0 | frame 506 | 4 |
| 467 | 0 | frame 508 | 4 |
| 470 | 0 | frame 509 | 4 |
| Other 433 helpers | 0 | full local eight-space | 8 |

Thus the ordered residual-width sum is 3484 per call. The verifier reads this
ordered registry from `WORD.final`, with `WORD.start` checked zero on every
helper. The older geometry object's full helper endpoints are not substituted
for those endpoints.

The local premise is the complete PR4183 literal-word endpoint, in either
orientation: decoded source and helper values are restored, decoded targets
receive the stipulated source XOR, and the private COPY row returns to zero.
The physical helper endpoint is the swap on its terminal projector, not
identity. Both comparator and candidate have the same ordered endpoints.
Their local endpoint proof is a separate input to this owner proof.

The global controller is exactly the pinned K=4 recipe. It has nine local
cover sweeps, eighteen bridge shears, ten idle children including the zero
child, and the final exchange. There are 29 controller records because each
bridge record denotes its two opposite-side shears. Stages are executed in
order, with replicas 0 through 31 in order within each stage. There are 288
local-call descriptors. Each descriptor denotes a whole cover sweep, not one
individual cover-class invocation.

## 2. A literal chronological fill

For a port vector q with q^T q=4, choose one fixed dyadic orthogonal family
chart A_q whose first column is q/2; it is the identity on the 56 exterior
coordinates. In this chart, an idle child advancing a family pair from level
a to level b has the ordered pending axes

    [1, 8+7b)       when a = -1,
    [8+7a, 8+7b)    when a >= 0.

The first expression contains all seven q-perpendicular axes and the
appropriate exterior blocks. These are the actual source pending projectors,
independently of which orthonormal completion was used in the data routes.

`owner.py` independently reconstructs the 29-record chronology and compares
its literal recipe with the authenticated source function. At every local
stage the active pair is at level s-1; at every bridge the two pairs have
equal levels; the final exchange starts with every pair at level eight.

For each child, let L be the last preceding local or bridge touch of its
physical pair, and let U be the child's position. Its host-stage window is
strictly L < position(stage) < U. Other idle operations on that family are
allowed between these positions only because their pending axes are disjoint.
The complete windows are regenerated from the actual events:

| Child | Pair | Rank | Allowed stages |
| --- | --- | --- | --- |
| 0 | 1 | 14 | 0, 1 |
| 1 | 1 | 7 | 2 |
| 2 | 2 | 28 | 0, 1, 2, 3 |
| 3 | 2 | 7 | 4 |
| 4 | 3 | 42 | 0, 1, 2, 3, 4, 5 |
| 5 | 3 | 7 | 6 |
| 6 | 0 | 42 | 3, 4, 5, 6, 7, 8 |
| 7 | 1 | 28 | 5, 6, 7, 8 |
| 8 | 2 | 14 | 7, 8 |
| 9 | 3 | 0 | none |

The inherited PR2423 selection expands to 3942 width-eight slots per replica.
Its complete slot-list digest is checked against the source receipt.
For each `(child, copy)` bin, keep the inherited ordered sequence of
`(stage, helper)` roles. Replace each helper's old width by its actual ordered
terminal width, then reset offsets to cumulative width sums in that same
sequence. No helper changes child, copy, stage, replica or physical family.
Every occupied interval remains a contiguous prefix of its pending axes; its
idle remainder is exactly the suffix.

This deterministic construction assigns every helper occurrence once, checks
all widths, capacities and windows, and checks disjointness across both a
single child and different children of the same physical family. The complete
`FILL` has 126144 rows. It uses the physical family

    replica*888 + (2*pair + side)*111 + port,

where `copy=side*111+port`. The helper's pair is always inactive during its
whole local sweep.

All three certificates are available through `owner.py --emit NEW_DIRECTORY`:
`ORDER.json`, `FILL.json.gz`, and `DISPATCH.json.gz`. The latter contains all
660 ordinary owners for every one of the 288 call descriptors. The verifier
checks those emitted descriptors separately against the reconstructed slots,
data-family formula, chart supports, replica index and private-family rule.
`OWNERS.json` records deterministic digests, rather than trusting the
digests in place of the enumeration.

## 3. Actual partial-terminal charts and owner separation

Let E_h be the local terminal projector of helper h, of rank k in {4,8}.
Use the pinned orthogonal matrix Q_h with

    Q_h diag(I_k,0) Q_h^T = E_h.

For a full-width helper Q_h=I_8. The three rank-four matrices have entries
in {0, 1, -1, 1/2, -1/2}. The checker reconstructs E_h from the actual root
lines and checks this identity and orthogonality exactly.

For a helper slice S of size k, define pi_S by sending the first k local axes
to S in order, and the remaining axes to the unused ambient axes in increasing
order. Use the 64-dimensional owner chart

    sigma_h = A_q pi_S diag(Q_h^T, I_56).

Then

    sigma_h E_h sigma_h^-1 = A_q E_S A_q^-1.

In particular, partial slices may split q-perp. This is permitted because
their exact A_q-dependent projectors, and the matching remainder, are now
specified. Rank counts alone would not specify these operators.

At common invocation d, the physical helper owner is `(family, d sigma_h^-1)`.
All roles therefore align by `g sigma_h=d`. The data owners retain their
source data charts and the 222 distinct active families.

Several helpers may use one family. Different physical *families* are not
required by this source interface: physical storage is indexed by family
and cover class. Merely giving routes different names would also be
insufficient. Because E_h can differ between two partial helpers, even
disjoint final supports alone do not prove that their sigma matrices differ.

The certificate checks the actual matrices. A common A_q cancels for every
same-family pair, so it compares

    pi_S diag(Q_h^T,I_56).

For every pair within every stage/family it computes the gcd of all nonzero
numerators of the entrywise difference. The gcd is a power of two. Thus no
odd prime makes the two matrices equal, and their reductions are distinct
over every odd residue ring. Replicas use disjoint physical-family ranges;
the same comparison covers all 32 replicas. This proves injective owners at
each fixed common invocation. Here all 5648 pair comparisons per replica
actually have gcd one, covering 180736 pairs over all replicas. There are
28096 occupied physical families, with at most five helpers in a family at
one call.

The private owner uses family `28416+stage` and common class d. These nine
families are outside the live stock. The complete local word restores the
private packet after each COPY/ERASE episode. Replicas therefore reuse it
sequentially, with no reset of arbitrary dirty payloads and no reduction of
the inherited nine-family reserve.

## 4. Complete local-ring packets

We use PR2234's packet interface explicitly, rather than inferring it from
point-owner injectivity. Fix an odd prime q, w>=1 and R=Z/q^w. Payloads are
arbitrary Boolean functions of the complete address blocks and spectators;
R is the address ring, while payload XOR is over F2.

For each invertible low matrix d0 define the full high fibre

    F_d0 = {d0 + q G : G ranges over [q^(w-1)]^(64*64)}.

Every chart is invertible over R. Right multiplication gives a bijection

    F_d0 sigma^-1 = F_(d0 sigma_bar^-1),

including the carries in low/high coordinates. The actual chart-separation
check above makes these low classes different for every same-family helper
pair. Their complete high packets are consequently disjoint. Pointwise
injectivity at one d would not have been enough for this conclusion.

Execute the entire local word for one low class on its complete high packet
before proceeding to the next low class. Address callees must preserve all
spectators, restore row coordinates and close their work before returning.
Under these explicit premises, the local common-label induction applies to
each high coordinate and hence the complete packet. Correlated helper
contents are allowed. Later low invocations may revisit a packet in a
different role; the complete endpoint theorem uses its current dirty value.

The gauges may include a fixed ancestor-dependent diagonal unit matrix A,
provided it is independent of this node's family, cover coordinates and
unused descendant row field. With the retained tail reversal C, use

    D_C(P) = [[I-P, PC], [CP, I-CPC]],
    Q_A = diag(A,I),   Q_d = diag(d,CdC).

The projector is conjugated by `d P d^-1`; a transpose of d is incorrect for
a general GL matrix. The projector, nested-difference and common-label
identities are dyadic identities and specialize to R. Image/kernel columns
independent modulo q lift to an invertible basis over R, proving the actual
split ranks even when q divides the rank. For f-atom blocks tensor with I_f
and retain every specified spectator and the source reversal convention.

This proves an exact owner interface for arbitrary q and w under the stated
whole-packet callee contracts. It does not implement those contracts at
sublinear recursive exponent, or bound physical scans, address generation,
packet routing, work erasure or tape movement merely by counting matrix
entries.

## 5. Chronological restoration

In the forward word a helper changes gauge from the zero local frame to E_h;
its physical residual is the swap D_C(E_h). In the reflected reversed word
the initial helper gauge is the complement of E_h and the final gauge is
the full local block. Their relative map is again D_C(E_h). The reflected
helper does not start at the old zero/complement-full boundary.

Apply the complete arbitrary-dirty local endpoint before commuting any
operation. A full cover sweep sends `d -> d sigma_h^-1` bijectively through
the full cover, so that slot's residual occurs once at each physical class.
Between its host stage and nominated child, every completed call or bridge
on other pairs has an endpoint independent of this helper family.
Intervening hosted and idle residuals on this family occupy disjoint
pending axes.

For a fixed family and cover element g, the physical factors are

    g A_q E_S A_q^-1 g^-1.

These idempotents commute and have zero pairwise products. Their exact
remainder is the complementary axis set in the same fixed A_q chart.
Consequently their partial swaps multiply to the original pending child.
This is an operator identity on arbitrary retained payloads, not an
argument that fresh helper inputs can be supplied at each occurrence.

At every deadline the helper slices plus remainder partition all pending
axes. The global source controller can therefore be reduced to the original
unhosted controller, with its actual bridge and exchange order. No inner
MOVE is commuted across a dirty ADD or a COPY episode. PR4183's local retiming
is entirely internal to a complete call, so none of these source windows
changes.

## 6. Complete idle and coordinate bills

The old full-width R438 fill and the admitted mixed-terminal fill have these
nonzero idle profiles per replica:

    old: {2:433, 4:444, 6:444, 7:666, 34:1, 42:10}
    new: {2:420, 4:435, 6:444, 7:666, 8:6, 10:9,
          14:4, 16:3, 34:1, 42:10}.

Each also has 222 zero remainders. The mixed-terminal idle rank mass is
10602 per replica, an increase of 180=9*5*4, or 5760 globally. These returned
pieces are paid. There remain 1998 positive idle children per replica,
28416 live families, nine reserved private families, and zero banks.

The global paid profile is `288*local_profile + 32*new_idle_profile`.
Its mass is `288*5101 + 32*10602 = 1808352`, leaving the unchanged deficit
`64*28416 - 1808352 = 10272`. Because both frozen mixed-terminal words use
this identical fill, PR4183's local delta `e7-e6-e1` survives here as
`288*(e7-e6-e1)`. The comparison with the older all-full-terminal R438 word
must also include the changed idle profile above.

Coordinate lowering is explicit and separately priced. A_q uses a signed
four-coordinate Hadamard/2 butterfly followed by a permutation, or just a
signed permutation for a coordinate root. The elementary alphabet is unit
signed ADD, NEGATE, DOUBLE, HALF and SWAP. The terminal Q_h programs retain
their predecessor's counts 24,70,70 and are replayed here exactly, including
their inverses. pi_S is a literal swap program.

Across all 55 relative charts and 111 ports, sigma_h needs at most 151
coordinate primitives in either direction. On both head and tail blocks the
bound is 302, and the chart followed by its inverse costs at most 604.
No scratch field element is used by these coordinate programs. The forward
prefix infinity-norm bound is 8, the inverse bound is 16, and the prefix
denominator bound is 4. These are exact arithmetic bounds, not permission
to round.

For the retained finite selector expression we conservatively use

    G = 240 + 144 + 604 + 2 + 63 + 64 = 1117.

The 240 bounds the retained 15-coordinate data-chart Gaussian factors;
144,2,63,64 are retained legacy terms. The additional 604 charges the complete
new helper chart on both address halves in both directions. The inherited
outer factor two is also retained, so no restoration cost is removed by
this bound. `routing_invoice` exposes every term. Its use in a physical
payload invoice remains conditional on the retained selector/callee
implementation contract; coordinate operations alone do not prove an
O(V) physical route. The old rational Gaussian lowering retains its source
admissible-prime exclusions, if any; the all-odd-ring owner theorem uses the
dyadic matrices themselves. The new A_q, Q_h and permutation programs use
only dyadic unit primitives over every odd ring.

## 7. Coverage and remaining obligations

The finite checker authenticates the five inputs, derives the ordered widths,
all charts, every owner, every source window, complete pending factorizations,
literal dispatch, coordinate programs and the full idle bill. Its defects
include missing/duplicate helpers, a host outside its strict window, an
incorrect terminal width, overlapping slices, identical same-family charts,
a wrong replica, private/live aliasing and an equal-rank wrong projector.
Assertions are not used as acceptance gates, so the check also runs under
`python -O`.

The arbitrary-q/w packet extension and retained-state chronological argument
are written proofs, not exhaustive enumeration of all q,w or a proof-kernel
replay. The finite matrix/owner calculations cover the complete fixed
64-dimensional construction. They do not themselves complete rounded-child
cleanup, all-size physical compiler/routing, storage/tape scheduling, or
compatible joint outer-supplier hypotheses. In particular, an available
p=1 whole-packet implementation cannot be advertised as an implementation
of the stronger p<1 recursive tariff.

New material is Apache-2.0 and was prepared with substantial OpenAI Codex
assistance. No independent human review or formal-kernel certification is
claimed.
