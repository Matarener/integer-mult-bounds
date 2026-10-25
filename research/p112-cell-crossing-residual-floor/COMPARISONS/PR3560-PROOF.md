# Triple-reader floors under an orthogonal block refinement

## Exact hypotheses and claim

Work with a finite indexed binary label collection and its binary bilinear Gram
pairing. Three **distinct indexed groups** G_A,G_B,G_C have positive even sizes
and Gram matrices I. Every group is partitioned into complete two-port planes.
Let a,b,c be one alternating-half scalar indicator from each group; their
scalar supports are disjoint. For a scalar vector x, cl(x) contains both ports
of every plane meeting its support. Charge a term by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Assume an orthogonal direct-sum decomposition of the union of these group spans:

    span(G_A,G_B,G_C) = perpendicular_sum_alpha V_alpha.

Every block V_alpha is positive even dimensional and nondegenerate. For each
j in {A,B,C} and block alpha, the labels of G_j in that block are either absent
or a **complete Gram-I basis of V_alpha**. Their union is all of G_j. Every
complete plane stays in one block. Bases, orderings and plane pairings in a
shared block may differ between groups. Partial bases, a label mixing blocks,
and planes crossing blocks do not satisfy the hypotheses. Other ambient groups
need not respect this decomposition.

Let n_k be the sum of dimensions of blocks present in exactly k of the three
target groups. The original three indicator terms cost

    D = |G_A|+|G_B|+|G_C| = n_1+2n_2+3n_3.

**Theorem.** Over every coefficient field F, every exact factorization

    aa^T+bb^T+cc^T = sum_(i=1)^t u_i q_i^T,     t <= 4,

has total tariff at least D. The factors may have arbitrary ambient values,
external directions, repeated rays, zero terms and cancellations. The original
three terms attain D. This extends the common-span hypothesis of PR3549 to
unequal and different group spans admitting the stated complete-plane block
refinement. It does not cover general different spans.

The new residual bounds, after the inherited normalisation below, are

    VVV: total tariff >= n_1+3n_2+3n_3 = D+n_2,
    MMM: total tariff >= 2n_1+3n_2+3n_3 = D+n_1+n_2.

Both residual bounds are attained by some bases and support choices under this
contract: take coincident bases in each shared block. Attainment for every
choice of differing bases is not asserted. The theorem and residual bounds are
author-checked; independent human and formal proof-kernel review are unclaimed.

## The inherited four-term reduction

The exact PR3538 and PR3549 proof bytes are retained in this package. Their
projective normalisation and three-mark selective maps are retained pending
proof premises. The seven-point classification and general support-transfer
premises are canonical pinned inputs. The predecessors' literal finite
geometric censuses are not used as proof premises here.

For a rank-three target and t<=4, rank(U)+rank(Q)<=t+3<=7. Transposition preserves
the tariff and gives a rank-three query side spanning a,b,c. The at-most-seven
point rank-three classification has 22 characteristic-two representable types
and the non-Fano type. The two middle non-Fano marked-triple orbits also admit
the selective source-zero/target-span transfer in the retained proofs. For all
these cases, support-shrinking transfer followed by the characteristic-two
expanded-identity rank bound gives D, with arbitrary original ambient factors.
The registered replay reruns both complete canonical classification checks.

The two residual marked orbits, in every characteristic other than two, have
these projectively normalised exact forms:

    VVV queries: a+b, a+c, b+c, a+b+c
    2u: a+b-c-w, a-b+c-w, -a+b+c-w, 2w

    MMM queries: a+b-c, a-b+c, -a+b+c, a+b+c
    2u: a+b-v, a+c-v, b+c-v, v.

Direct multiplication proves each identity. Solving the three target-coordinate
equations gives every reader, with arbitrary ambient parameter vector w or v.
Target and query scalings leave supports unchanged, as detailed in the retained
proof. These reductions use no common-span or block-refinement hypothesis.

At each selected target port, VVV may replace w by 0,+1,-1 and MMM may replace
v by 0,1, shrinking all reader supports termwise. Every other value activates
all four readers and can be replaced by zero. Outside the three targets set
the parameter to zero, again shrinking supports. Exactness is preserved by the
affine formulas. Plane closure and binary submatrix rank preserve this tariff
inequality. Thus the reduced readers and queries only use the three groups.

## Orthogonal blocks separate the actual tariff

After this shrinking, each reader closure is a union of complete planes inside
the blocks. A query closure contains a complete basis of any block touched by
one of its selected groups. Pairing entries between different blocks are zero.
After row and column permutations the actual rectangular Gram matrix is block
diagonal, so its binary rank is the sum of its block ranks. Repeated indexed
labels in different groups do not change this statement.

We may therefore bound the sum of four charges on each block separately.
Let d=dim(V_alpha) and let k be its group multiplicity.

For k=1, use symmetry to call its group A. In MMM, every query contains V_alpha.
Each A plane occurs in exactly two readers, and the Gram-I basis planes are
orthogonal. Summing their ranks gives exactly 2d. In VVV, the A reader-support
patterns in term order 1,2,3,4 are

    w=0: 1110;   w=+1: 0011;   w=-1: 1101.

The queries meet A in terms 1,2,4. Consequently each A plane contributes at
least its dimension 2, giving d. Permuting target names permutes the first
three terms, so the same argument applies to B and C.

For k>=2, choose two present groups and rename them A,B. All four queries in
either residual family contain V_alpha, because each query touches at least
one of these two groups. The parameter choices partition each complete basis
into orthogonal coordinate summands. For MMM write

    V_alpha = A_0 perpendicular_sum A_1 = B_0 perpendicular_sum B_1.

For VVV write A_0,A_+,A_- and B_0,B_+,B_-. Empty summands are allowed. The
complete-plane condition is exactly what makes these full orthogonal coordinate
decompositions. For reader i let K_i be the subspace of V_alpha orthogonal to
every label in its reader closure on this block. Its block charge is d-dim(K_i).
The two groups' support patterns force these necessary inclusions:

| Family | K_1 | K_2 | K_3 | K_4 |
| --- | --- | --- | --- | --- |
| MMM | A_1 intersect B_1 | A_1 intersect B_0 | A_0 intersect B_1 | A_0 intersect B_0 |
| VVV | A_+ intersect B_+ | A_+ intersect B_- | A_- intersect B_+ | A_0 intersect B_0 |

A third present group only imposes additional orthogonality conditions. No
assumption on the relation between the two bases inside the block is used.

For any two direct-sum decompositions V=sum_r A_r=sum_s B_s, distinct joint
atoms A_r intersect B_s form a direct sum. To prove it, take a relation among
these atoms, project onto each A_r, then project each resulting relation onto
each B_s. Distinct pairs leave only one term, which must vanish. The projection
families need not commute on all of V.

The four pairs in each row are distinct, so sum_i dim(K_i)<=d. Hence the sum
of block charges is at least 4d-d=3d. This argument also applies when exactly
two groups occur in the block; the absent third group adds no constraint.

Summing the k=1 and k>=2 bounds over all blocks proves both residual inequalities.
Since each is at least D, the inherited reduction proves the full theorem.

## Sharpness, evidence and limits

When all bases in a shared block coincide, taking one parameter choice per
target group uniformly on that block makes every binary coordinate independent.
The complete local tables in RESULT.json have minima:

| Block multiplicity k | VVV charge per binary dimension | MMM charge per binary dimension |
| --- | --- | --- |
| 1 | 1 | 2 |
| 2 | 3 | 3 |
| 3 | 3 | 3 |

The tables enumerate all 7 nonempty memberships and all 2- or 3-valued choices;
they prove attainability. Choices can be made independently in each block,
because complete planes stay in blocks. Thus both displayed lower bounds are
sharp as bounds under this contract, without asserting universal attainability
for differing bases. The three-term theorem is sharp for every allowed basis.

Two separate implementations agree on every four-charge stream and histogram
for 11,856 assignments in eight fixtures. The examples include unequal nested
spans, pairwise overlaps with no equal spans, disjoint spans, a larger third
group, non-coordinate orthogonal blocks, and differing bases within a common
block. The primary uses packed projected-column elimination; the separate
implementation derives support from integer coefficients and uses raw binary
Gram elimination. It also checks the exact coefficient identities over the
integers and 135 gauged entries over F3,F5,F7. These checks validate code and
finite examples. The blockwise argument supplies the unbounded quantifiers.

The 60 random general-span fixtures in the session directory are exploratory
corroboration only. They supply no general theorem or new search exclusion.
General spans without this refinement, block-crossing planes, partial block
bases, complementary indicators of one indexed group, five terms and different
tariffs remain outside this theorem. Native acquisition, coefficients, frames,
dirty restoration, physical sharing, hosting, precision, stock, compiler/all-size
admission, complete suppliers and outer multiplication transfer are unrun and
unclaimed. No kappa improvement or selected-frontier change is asserted.

Credit retains Nick Petalas/PR3549, PR3538, PR3513, PR3505 and their predecessor
chain; Philippe Van Velzen and Arham Tahir/PR3345 for expanded identity; and
Tekalign/PR3370 with the P112/E8/native/compiler attribution in the pinned
sources. No frozen predecessor or canonical source is edited.
