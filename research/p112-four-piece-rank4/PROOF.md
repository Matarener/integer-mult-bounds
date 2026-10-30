# A literal rank-four P112 counterexample

On the literal 112 doubled E8 root lines P, use the source's leading-one
nine-bit labels ell(r). For a characteristic-zero field K, define

    C = {c_h=(r dot h)_(r in P) : h in K^8},
    w(q) = rank_F2 {ell(r) : q(r) != 0}.

There are four independent pieces q0,q1,q2,q3 with

    (w(q0),w(q1),w(q2),w(q3)) = (4,5,6,6),
    (|supp q0|,|supp q1|,|supp q2|,|supp q3|) = (6,12,20,18),
    q0+q1+q2+q3 = c_h != 0,
    dim_K(C intersect span_K(q0,q1,q2,q3)) = 1.

This disproves the proposed extension of PR3418's four-piece exclusion from
first-piece rank three to four. The counterexample is unconditional over
characteristic zero. It does not use the predecessor's Weyl-chamber theorem,
capacity censuses, live-normal exclusions or any unmerged Git dependency.

## Literal construction

Take the removed-frame root a=(0,0,0,0,0,0,2,-2) and h=a/4. For a live doubled
root r,

    c_h(r) = (r[6]-r[7])/2 in {-1,0,1}.

Its support E has 56 sites. WITNESS.json partitions E into four disjoint sets
S0,S1,S2,S3. Each piece is c_h restricted to its set and zero elsewhere. Thus
their sum is c_h on all 112 coordinates. Every piece is nonzero; disjointness
makes the four pieces independent.

The witness uses zero-based indices into the source's sorted live-root list.
It supplies all 56 indices, their exact labels and signed coefficients. It
also supplies the corresponding 120-root masks and an explicit binary basis
for each piece. The bases have lengths 4,5,6,6. The primary verifies their
independence and that they span every label on the corresponding support.
It recomputes the support ranks directly. No numerical or finite-field test
is used as a substitute for the characteristic-zero coefficient identity.

The six-site small support has live indices 2,3,6,7,12,13, labels
421,269,293,397,357,461, and values -1,1,-1,1,-1,1. Its binary basis is
40,104,168,421. Its rank is four despite occupying six sites. PR3418's
four-site cardinality theorem does not exclude this support.

## Exact code intersection

Let A be the 112-by-8 integer matrix whose rows are the live doubled roots,
and Q the 112-by-4 matrix of the four pieces. The live-root Gram identity is
A^T A=112 I, so A has rank eight over every characteristic-zero field. The
disjoint nonzero pieces give rank Q=4.

The literal coefficient identity gives the joint-column relation

    A[:,6] - A[:,7] - 2*(Q[:,0]+Q[:,1]+Q[:,2]+Q[:,3]) = 0.

Consequently rank[A|Q]<=11. The witness lists an 11-by-11 minor on the following
zero-based rows and columns, using A columns first and Q columns last:

    rows = [36,24,16,8,4,3,6,7,5,54,18]
    columns = [0,1,2,3,4,5,6,7,8,9,10]
    determinant = -512.

The primary checks that determinant by rational elimination. The separate
implementation checks it by fraction-free Bareiss elimination and separately
computes the full code, piece and joint ranks as 8,4,11. A nonzero rational
minor stays nonzero in every characteristic-zero extension. Thus

    dim(C intersect im Q) = 8+4-11 = 1.

Since c_h is nonzero, the intersection is exactly its line.

## Source and verification boundaries

The primary reconstructs E8 roots and simple-root labels from the authenticated
canonical geometry, then compares every live root and label with the literal
main-branch data. The separate implementation reconstructs the root inventory
itself and reads the literal labels directly, without importing the geometry
module, primary support-rank code, primary witness checker or primary
determinant. It uses low-pivot binary elimination, a full rational row basis
and fraction-free integer determinants. The implementations share source
bytes, authentication, JSON reading, the literal witness and this proof. Their
agreement is internal computational corroboration, not human or formal
proof-kernel review.

The controls change the normal, one signed coefficient, a label, the claimed
small support basis, minor determinant, piece combination and index domain.
They also test duplicate sites, a singular matrix and a binary dependency.
Actual optimized CLI runs accept the canonical witness and reject all seven
mutants. These checks do not rely on Python assertions.

## Context, limitations and next step

PR3418 conditionally excluded arbitrary four-piece ranks 3,5,6,6 and left
rank four open. Its theorem remains contextual predecessor evidence here;
its heavy replay and mathematical premise are not invoked by this witness.
Taken together under that predecessor's stated premise, the first-rank
boundary is three versus four. This package alone proves the rank-four
counterexample and its exact one-dimensional intersection.

The discovery attempt checked both live-normal types before finding this
frame-normal cover. Those partial exclusions are not claims of this package;
its acceptance needs only the explicit witness. The original failed global
exclusion draft and logs remain in the session evidence, labelled failed.
No exhaustive classification or minimum six-site claim is made.

No full C5, C(P112)>=64, ten-piece caller, native decoder, preparation,
restoration, hosting, precision, paid consumer invoice, supplier admission,
new kappa or selected-frontier update follows. Human/formal proof-kernel
review, Lean, Docker and the selected cold replay are unrun.

An actual caller would need its precise quotient relations and enough
independent code directions. This witness supplies one direction only. Test
that contract before treating it as a complete decoder or starting another
construction search.

Credit Nick Petalas/PR3418 for the exact open rank-four question and prior
rank-three theorem; PR3397 for its preceding four-piece boundary; PR3405 for
the distinct literal caller result; PR3161/3162 and the root-simplex geometry;
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage. New work is
Apache-2.0.
