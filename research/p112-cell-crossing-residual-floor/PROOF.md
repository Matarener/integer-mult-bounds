# Residual tariffs with closure cells crossing orthogonal blocks

## Contract and result

Let a finite binary bilinear label space contain three disjoint indexed groups
A,B,C. Repeated binary labels across different groups are allowed. Their binary
spans have an orthogonal direct-sum refinement into nondegenerate blocks V_h.
Each block has a Gram-I basis. In each block, a group contains either a complete
Gram-I basis of that block or no labels. Every group is nonempty. Block
dimensions may be odd. Different groups may choose different bases in a block.
Each indexed label belongs to one block. Labels mixing blocks and partial block
bases are excluded.

Partition each group into arbitrary nonempty closure cells. Cells may cross
blocks and have any positive size. Select one representative index per cell.
Let a,b,c be scalar vectors that are 1 at their own group's representatives and
0 elsewhere. Their scalar supports are disjoint. Closure cl(x) includes every
index in every cell meeting the scalar support of x. Any extra ambient indices
have their own closure cells, disjoint from these three groups.

Charge a scalar outer-product term by the actual rectangular binary tariff

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Let n_k be the sum of block dimensions for blocks present in exactly k groups.
The three original terms aa^T,bb^T,cc^T have total charge

    D = n_1 + 2n_2 + 3n_3.

Over any coefficient field of characteristic different from two, consider the
following two fixed four-query factorizations, with arbitrary ambient readers:

    VVV queries: a+b, a+c, b+c, a+b+c
    MMM queries: a+b-c, a-b+c, -a+b+c, a+b+c.

The target is aa^T+bb^T+cc^T. The theorem is

    VVV total charge >= n_1 + 3n_2 + 3n_3 = D+n_2,
    MMM total charge >= 2n_1 + 3n_2 + 3n_3 = D+n_1+n_2.

Cells need not stay inside one block. The bounds are best possible in this
class, but need not be attained for a particular partition. An exact crossing
example below has VVV minimum 7 although its displayed bound is 6. MMM has
minimum 9 there. These are lower bounds for the two stated residual families.
An arbitrary-query four-term classification, characteristic two and physical
implementation are outside this theorem.

## Every reader and its support reduction

The four queries have scalar rank three. Comparing coefficients of the three
independent vectors a,b,c in the target equation gives all solutions, with an
arbitrary ambient parameter w or v:

    VVV 2u: a+b-c-w, a-b+c-w, -a+b+c-w, 2w
    MMM 2u: a+b-v, a+c-v, b+c-v, v.

These formulas also follow by direct multiplication. No reader is required to
lie in the scalar target span. Division by two is valid in the stated fields.
Multiplying a term's query by a nonzero scalar and its reader by the inverse
scalar leaves exactness and both supports unchanged.

Outside the representatives, set the parameter to zero. At such an index every
reader coefficient is a scalar multiple of that parameter, so this only removes
support. At a representative, a VVV parameter outside {0,1,-1} makes all four
readers nonzero. Replace it by zero. An MMM parameter outside {0,1} likewise
makes all four readers nonzero and may be replaced by zero. The exceptional
values stay distinct in every allowed characteristic, including three.
These replacements preserve exactness by the formulas and shrink each reader's
support. Closure and rectangular submatrix rank preserve that inequality.
Thus it suffices to prove the tariff bounds for one ternary or binary parameter
choice per cell. Every label of a cell inherits its representative's choice.
This is the step that permits cells to cross blocks.

## Blocks separate ranks, without separating choices

Every query closure is the union of all labels of its selected groups. Every
reduced reader closure is a union of whole cells. Within a block, its labels
form a subset of each present group's complete orthonormal basis. Pairings
between different blocks vanish. After row and column permutations, each
actual rectangular Gram matrix is block diagonal. Its rank is the sum of the
block ranks, even when one cell contributes labels to several blocks.

Parameter choices can be correlated across blocks by a crossing cell. We never
minimize the blocks independently. We prove a lower bound on each block for
every global choice, then sum those bounds. Correlation can only obstruct
attainment of the sum.

Fix a block of dimension d and multiplicity k. For k=1 rename the sole group A.
In VVV the A reader supports in term order 1,2,3,4 are

    w=0: 1110;   w=1: 0011;   w=-1: 1101.

The query meets this block in terms 1,2,4. Thus each basis label contributes to
at least one charge. The sum of the four block charges is at least d. In MMM,
each basis label occurs in exactly two readers, and all queries meet the block.
The sum is 2d. Renaming groups just permutes the first three terms.

For k>=2 choose two present groups and call them A,B. Each of the four queries
contains at least one of them, hence spans the whole block. A term's block
charge equals d-dim(K_i), where K_i is the annihilator of its reader labels in
this nondegenerate block.

The labels of each group's orthonormal basis partition according to their
inherited parameter value. Write A_0,A_1 and B_0,B_1 for MMM, and A_0,A_+,A_-
and B_0,B_+,B_- for VVV. These are orthogonal coordinate decompositions of the
whole block, including zero summands. A crossing cell merely ties choices
across these decompositions; it does not change their direct-sum property.
The support patterns force the following necessary inclusions:

| Family | K_1 | K_2 | K_3 | K_4 |
| --- | --- | --- | --- | --- |
| MMM | A_1 intersect B_1 | A_1 intersect B_0 | A_0 intersect B_1 | A_0 intersect B_0 |
| VVV | A_+ intersect B_+ | A_+ intersect B_- | A_- intersect B_+ | A_0 intersect B_0 |

Any third group only adds annihilator constraints. For two direct-sum
decompositions V=sum_r A_r=sum_s B_s, distinct joint subspaces A_r intersect
B_s form a direct sum. Indeed, project a relation onto a fixed A_r and then
project the resulting zero relation onto a fixed B_s. Exactly the term in that
pair remains, so it is zero. The two projection families need not commute.

The four listed pairs are distinct. Therefore sum_i dim(K_i)<=d, and the total
block charge is at least 4d-d=3d. Summing the k=1 and k>=2 contributions proves
both inequalities. The proof does not require even block dimensions, paired
cells, local cells or the same bases across groups.

## Exact strict crossing example

Use four orthogonal binary coordinate lines e_A,e_B,e_C,e_T. Group A has the
basis e_A,e_T, group B has e_B,e_T, and group C has e_C,e_T, with distinct
indexed copies of e_T. Each entire two-label group is one closure cell, with
its unique e_A,e_B,e_C index as representative. Thus a,b,c select the three
unique coordinates, while each selected plane crosses two blocks.

Here n_1=3,n_2=0,n_3=1 and D=6. The VVV bound gives 6. A unique-coordinate block
contributes exactly one only when its parameter is +1. Any other reduced choice
contributes at least two. If all three unique blocks contribute one, all three
parameters are +1, and the common e_T block is present in all four readers,
costing four. If any unique block contributes more, the common block costs at
least three by the theorem. Either way the total is at least seven. All +1
attains seven, so the exact VVV minimum is 7 over every stated field, for all
ambient readers. In MMM the theorem gives 9, attained by v=0 in all three cells.

This example explains why deleting the old cell-locality restriction does not
justify independently optimizing blocks or claiming universal attainment.
For sharpness of the general inequalities, use coincident block bases and
singleton cells. For multiplicities 1,2,3 the attained per-dimension VVV costs
are 1,3,3 and MMM costs are 2,3,3. The local scalar cases are also checked in the
finite fixtures; no larger bound holds for this entire class.

## Evidence, provenance and limits

Two implementations compare all four charges, the full ordered charge-stream
hash, every histogram and a minimizing assignment for 6,660 assignments in ten
fixtures. They cover odd blocks/groups, crossing two-port planes, cells of size
one/three/four, unequal nested spans, pairwise overlaps, all seven memberships,
different within-block bases and a non-coordinate block decomposition. The
second implementation also checks 15,584 integer or gauged F3/F5/F7 actual
operator entries, including two external scalar coordinates and generic dirty
parameters. These finite checks corroborate the code; the argument above
supplies the all-size quantifiers.

The proof is self-contained. No seven-point classification, selective transfer
map, expanded-identity theorem or inherited runtime is a mathematical premise.
COMPARISONS retains PR3560's exact proof solely to document the changed
hypothesis and its open handoff. It is not a canonical ancestry pin or replay
input. Credit remains with Nick Petalas/PR3560 and PR3549/3538, Philippe Van
Velzen and Arham Tahir's expanded-identity method, and Tekalign/PR3370 with its
P112/E8/native/compiler lineage. None of those broader results is recertified.

General nonreducing spans, partial block bases, arbitrary scalar representatives,
closures mixing target groups, characteristic two and arbitrary-query/five-term
classification remain outside scope. Native acquisition, coefficient delivery,
frames, dirty restoration, hosting, precision, stock, compiler/all-size supplier
admission, complete consumers and outer multiplication transfer are unrun and
unclaimed. No cheaper decoder, kappa improvement or selected-frontier change is
asserted. Independent human and formal proof-kernel review are unclaimed.
