# Fixed-plane exposure partitions imply the all-subset bound

The statement below is valid for the original R438 helper set and prescribed
causal promotion model. It is a combinatorial rank inequality. No selective
supplier, native compiler, owner allocation or multiplication exponent follows
from it. Substantial OpenAI Codex assistance; Apache-2.0.

## Model and fields

Let H={222,...,659}, so |H|=438. Let D be the 111-by-438 binary matrix of
helper-to-target dirt in the pinned old CLEAN R438 word with its initial
compensation omitted. Its columns must be reconstructed from circuit semantics
and compared with the literal initial compensation, not inferred from counts
of gate incidences. The B10 independent review established this semantic
equality and rank(D)=111 for the same raw R438 source. B11's independent
computational checker separately owns that binding for its packaged inputs.

Fix one rational plane E of dimension r. The finite family comprises all 120
distinct root lines in the pinned full E8 geometry and all 153 distinct
rank-two spans represented by frames of the R438 word. Thus r is 1 or 2.
Plane dimension and containment are over Q; kernel and independence of D are
over F2. The inequality is not an assertion about native implementations in
every finite ADDRESS field.

For each helper h, let M_E(h) be its subset of 120 exposure resources:
111 original target caps and nine original copied-total sources. Masks are
defined by the following fixed chronological join rule. After initial ZERO
compensation and a prospective common-E helper basis setup, the chosen helper
set S is marked promoted. This includes chosen pivot helpers that are lifted
to E as well as candidate kernel entrances. A promotion means that the
current old frame f is replaced by span(f,E).

- At an ordinary ADD whose old common frame f does not contain E, promotion
  of either actor forces both actors to the joined frame. Their Boolean flags
  become their OR. This is a requirement of this common-frame algorithm,
  not ordinary one-way data flow of the scalar ADD.
- At a MOVE into a frame containing E, promotion ceases to distinguish the
  new frame from its original frame. The flag resets. An ADD at a frame
  containing E likewise has no distinct promoted frame.
- A reached final target cap not containing E marks that target resource.
- At each original COPY cut, a reached source frame not containing E marks
  that COPY resource. The private field stays at ZERO; promotion does not
  propagate through its scatter ADDs.

The PRIVATE ZERO rule is compatible with these helper seeds in this word:
the initial D phase is compensation, A has no target incidences, and all nine
copied scatters precede B. Therefore targets are still at ZERO throughout
these scatters. This is not a statement about starting with promoted targets
or changing the COPY chronology. The original copied source is immutable
between COPY and ERASE.

All 111 final target caps and all nine original copied-total source frames
have rank seven. Joining such a frame with E either changes nothing or
produces FULL, of rank eight. Each marked resource therefore represents one
additional rank under this model. Sources finish at FULL, which already
contains E; their altered intermediate paths are not exposure resources.
Those paths can still change the query histogram and must not be treated as
having no analytic cost or benefit.

The flag transitions use only OR and reset. Hence the resource set produced
from a set S of helper seeds is exactly

    exposure_E(S) = union_(h in S) M_E(h).

Backward propagation of resource labels is the transpose of this Boolean
dependency process: copy labels across persistent MOVEs, discard them at a
reset, union the two labels across a below-E ADD, and add the COPY resource
at its actual source cut. The fresh checker should rebind these masks using
the actual word; calling the same propagation function twice is not an
independent verification of this model.

## Partition certificate

The argument applies more generally to any matrix D, any resource masks,
positive integer r and positive integer capacity lambda. Make r colored
copies (c,h) of every helper, 0<=c<r. A certificate partitions some of these
copies into the following disjoint classes:

1. For each color c, one class I_c of that color's copies whose D columns are
   independent.
2. For each resource t, a class J_t of at most lambda copies, each incident
   to t, meaning t belongs to M_E(h).
3. A set U of unassigned copies, the exact complement of the assigned copies.

Every node must be a valid colored helper, must have at most one owner, and
must obey its class's color/incidence/capacity rule. These are verifiable
properties of the emitted partition. They do not depend on an augmentation
algorithm being correct or complete.

Let g=|U| and fix any S subset H. There are exactly r|S| colored copies with
helper in S. The intersection I_c with these copies is an independent set
of columns from D_S, so it contains at most rank_F2(D_S) elements. A resource
class can contain such a copy only when its resource belongs to
exposure_E(S), and each resource class contributes at most lambda elements.
At most g copies of S are unassigned. Counting this disjoint partition gives

    r|S| <= r rank_F2(D_S) + lambda |exposure_E(S)| + g.

Consequently, simultaneously for every S,

    r nullity_F2(D_S) - lambda |exposure_E(S)| <= g.             (1)

The proof quantifies over every subset of the fixed helper set. It does not
require an enumeration of its 2^438 subsets, a single-cohort restriction, an
optimality theorem for matroid union, or correctness of the producer's
reachable-set search.

For lambda=8, each saved root-line certificate assigns all 438 copies and
each rank-two certificate assigns all 876 copies. If these assignments pass
the source-binding and certificate checks, then g=0 and (1) proves

    dim(E) nullity_F2(D_S) <= 8 |exposure_E(S)|

for every S and each of the 273 listed E planes. The empty subset has
objective zero, so the optimum is exactly zero. In fact all saved lambda-8
selected cuts are empty. A nontrivial matching cut and residual augmentation
search are unnecessary for this particular zero-optimum conclusion.

For a nonzero-gap certificate, an actual subset of whole helpers with objective
equal to g certifies matching lower and upper bounds. “Whole-helper cut” means
a subset of helpers rather than a subset of colored copies; it does not mean
that all 438 helpers must be selected.

## What the finite receipts can and cannot certify

A complete receipt can certify all subsets if an independent checker binds
the exact D, helper order, plane E, every mask, and the complete partition.
The finite plane enumeration must be exact: no omitted or repeated plane,
and every rank-two frame included. The written counting proof then turns
these finite certificates into the universal subset statement for each E.
This is a finite source-bound theorem with a general written lemma, not a
formal-kernel proof or an all-parameter supplier theorem.

The coefficient 8 is an auxiliary resource weight/capacity. It is not the
physical native tariff of a marked target or COPY, which is one here. Thus
the inequality alone neither makes nullity no larger than exposure nor
rejects an actual rank-mass saving. For example, r nullity=8 and exposure=1
satisfies this inequality while r nullity-exposure=7 is positive. In addition,
changing helper residual widths changes owner stock credits, and promoted
pivots or source paths can change moments even with nullity zero. A full
rate conclusion needs an independent complete benefit bound and invoice.

The kernel is the full D_S kernel. Removing cold target rows changes that
kernel and invalidates the stored D-independent classes. As a minimal
countermodel to that transfer, a one-column matrix D=[1] with an empty
exposure mask has nullity zero and a complete independent-class certificate.
Deleting its only target row gives nullity one and the same empty exposure,
which violates the proposed transferred inequality. This is an abstract
countermodel to broadening the theorem, not a defect in the actual fixture.

Fixed-E certificates also do not compose automatically for mixed planes with
shared exposure resources. For example, take 16 zero columns and two resources.
In one plane assign the first eight helpers only to resource a and the other
eight only to b; swap these assignments in a second plane. Each plane obeys
|S|<=8|exposure(S)| for every S. Choosing the first group under the first plane
and the second group under the second plane gives 16 selected directions but
only resource a if mixed costs are charged once. A real mixed construction
may incur further costs; these individual certificates do not decide them.

Likewise, new COPY/private cuts (especially the global-E private-at-E model),
retiming, alternate frame adapters, new observations, operator-valued kernels
or changed scalar words require new source binding and certificates. No
literal selective joined word, native owner, rounded-error proof or physical
source/tape compiler is supplied by this partition theorem.
