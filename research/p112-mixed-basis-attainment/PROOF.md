# Exact floor attainment with different orthonormal block bases

## Contract and theorem

Let three disjoint indexed groups A,B,C be nonempty. Their binary labels lie in
an orthogonal direct sum of nondegenerate blocks V_h. Every block admits a
Gram-I basis. In a block of dimension d_h, each group contains either one whole
Gram-I basis or no labels. The bases may differ between groups, and dimensions
may be odd. Every label lies in one block. Partition each group into arbitrary
nonempty cells, possibly crossing blocks. Choose one representative per cell.
The scalar vectors a,b,c are the unit indicators of their representatives.
Ambient indices have cells disjoint from the target groups.

For scalar vectors u,q, close their supports by whole cells and charge

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The target scalar operator is aa^T+bb^T+cc^T. Over any coefficient field of
characteristic different from two, fix the queries in this order:

    VVV: a+b, a+c, b+c, a+b+c
    MMM: a+b-c, a-b+c, -a+b+c, a+b+c.

Readers may be arbitrary ambient vectors. Let n_k be the sum of dimensions of
blocks present in k groups. The original bill is D=n_1+2n_2+3n_3.

Make a graph on cells. Join cells from different groups when some pair of their
labels in the same block has binary dot product one. Mark a cell as pinned
when it contains a label in a block present in only one group. Let P be the
union of graph components containing a pin. For a cell c, let m_h(c) count its
labels in block h. Counts include distinct indexed copies across groups.

**The attainment criterion.** The VVV minimum equals

    L = n_1+3n_2+3n_3

if and only if there is a set N of unpinned cells in P satisfying both:

1. N is an independent set in the cell graph.
2. For every triply shared block h,

       sum_{c in N} m_h(c) = sum_{c in P, group(c)=A} m_h(c).

Thus equality is a finite weighted independent-set feasibility problem with
one integer equation per triple block. It needs no rank calculation once the
cell graph and integer weights have been formed. A proposed N is checked by
pairings and counts. No polynomial-time decision algorithm or hardness result
is asserted.

An attaining reader is explicit: give cells in N parameter -1, cells in P\N
parameter +1, and every other cell parameter zero, in the VVV formulas below.
For the same general geometry, MMM always attains

    2n_1+3n_2+3n_3.

These are support tariffs. The theorem supplies no physical COPY program,
supplier admission, exponent improvement or selected-frontier update.

## Support reduction and the lower bounds

Comparing the three independent query coefficients gives every reader solution,
with arbitrary ambient parameter w or v:

    VVV 2u: a+b-c-w, a-b+c-w, -a+b+c-w, 2w
    MMM 2u: a+b-v, a+c-v, b+c-v, v.

Direct multiplication gives twice the target in each case. These are all
solutions because the four fixed queries have rank three. Outside the
representatives every reader is a multiple of the parameter, so setting that
parameter to zero only removes support. At a representative, a VVV value outside
{0,+1,-1}, or an MMM value outside {0,1}, makes all four coefficients nonzero.
Replacing it by zero only removes support. These exceptional values remain
distinct in every permitted characteristic. Exactness remains true by the
formulas; closure inclusion and submatrix rank are monotone. The minimum is
therefore attained among one ternary VVV or binary MMM value per cell. This
reduction makes no reader-span assumption.

In a block with k>=2 present groups every query closure spans the block. If K_i
is the annihilator of reader labels in term i, the block charge is d_h-dim K_i.
For two present groups renamed A,B, split their orthonormal bases according to
cell values. Write A_0,A_+,A_- for the spans of these disjoint subsets, and
similarly B. The four annihilators in VVV are contained respectively in

    A_+ intersect B_+, A_+ intersect B_-,
    A_- intersect B_+, A_0 intersect B_0.

For MMM the four analogous pairs are A_1/B_1, A_1/B_0, A_0/B_1,
A_0/B_0. Distinct joint intersections are mutually orthogonal and form a direct
sum: project any relation to one A summand, then to one B summand. Hence the
sum of the four annihilator dimensions is at most d_h. A third group only adds
constraints. Both block bills are at least 3d_h.

For a singleton block the basis is orthonormal. Each VVV label costs 1,2,3
when its cell value is +1,0,-1, respectively. Each MMM label costs two. Actual
rectangular Gram ranks add across orthogonal blocks, even when cells correlate
their choices. Summing proves the VVV and MMM lower bounds for every global
choice. Taking v=0 makes MMM readers the three pairwise unions and zero.
Each singleton block then costs 2d_h and each multiple block 3d_h, proving
universal MMM attainment without a cell-locality or common-basis assumption.

## Equality inside one multiple block

The following exact local test is useful independently of the global graph.
A reduced VVV choice attains a multiple block's 3d floor if and only if:

- Every cross-group pair of labels having dot product one agrees on whether
  its value is zero, and never has both values negative.
- In a triple block, the total number of negative labels plus the number of
  zero labels in any one group is d.

To prove this, first take a double block A,B. Its four annihilators are exactly
the four displayed intersections. They are mutually orthogonal. Equality of
the dimension sum to d is equivalent to their direct sum being all of V.
Projecting that equality to A_0 and B_0 forces

    A_0 = B_0 = K_4 = Z.

It also forces A_-=K_3 and B_-=K_2, so these negative subspaces are orthogonal.
Conversely, assume the zero subspaces agree and A_- is orthogonal to B_-.
Inside Z-perp, the two negative subspaces are nondegenerate and orthogonal.
Their orthogonal complement is A_+ intersect B_+. Therefore V decomposes into

    A_- direct-sum B_- direct-sum (A_+ intersect B_+) direct-sum Z.

These are K_3,K_2,K_1,K_4, so equality follows.

For a triple block the exact annihilators are

    K_1 = A_+ intersect B_+ intersect C_-,
    K_2 = A_+ intersect B_- intersect C_+,
    K_3 = A_- intersect B_+ intersect C_+,
    K_4 = A_0 intersect B_0 intersect C_0.

If their sum fills V, projection to each group's summands gives a common zero
subspace Z and A_-=K_3, B_-=K_2, C_-=K_1. The three negative subspaces are
orthogonal and fill Z-perp. Conversely, those conditions make the displayed
K_i sum to all of V. All negative labels together are an orthonormal set, so
they fill Z-perp exactly when their number is d-dim Z.

Finally, graph conditions express precisely these subspace conditions.
Agreement of zero status on odd pairings says each group's zero labels are
orthogonal to every nonzero label of every other group. Expansion in the other
group's full orthonormal basis gives inclusion of zero spans, in both
directions. Their spans therefore agree. Forbidding a negative-negative odd
pairing gives orthogonality of negative subspaces. The zero count in a group
is dim Z. This proves the local test with arbitrary different bases.

Singleton blocks attain their floors exactly when all their cells have value
+1. Since every block excess is nonnegative, attaining L globally is equivalent
to this singleton rule and the local test in every multiple block.

## Removing unpinned components

The local test forces zero/nonzero status to be constant on a connected cell
graph component. A pin forces that component to be nonzero. It remains to show
that every unpinned component can be set to zero without losing equality.

Within one multiple block, form the finer graph on its indexed labels, joining
cross-group pairs with dot product one. For a component H, the span of its
labels from one group equals the span from every other present group. Indeed,
a label in H is orthogonal to all other-group labels outside H, so its expansion
in that whole orthonormal basis uses only labels in H. Reverse the inclusion.
Each group therefore supplies a whole orthonormal basis of one common
nondegenerate subspace W_H. Different H give orthogonal subspaces.

A cell component contains whole such H, possibly from several blocks. In a
floor-attaining assignment, an active triple H has its negative labels forming
an orthonormal basis of W_H by the local test. Deactivating an unpinned cell
component removes exactly dim W_H negative labels and adds exactly dim W_H
zero labels in the reference group. Its triple count equation stays true.
Double-block orthogonality stays true as well. There are no singleton labels
in an unpinned component. Setting all its cells to zero preserves every floor.

Consequently an attaining assignment exists exactly when one exists with
nonzero cells precisely P. Its negative cells form N. The no-negative-edge rule
is graph independence, singleton pins exclude N, and the local triple count
becomes the integer equation in the theorem. The explicit assignment from N
satisfies every local test. This proves both directions of the criterion.

## A basis change that destroys equality

Use three private orthogonal lines p_A,p_B,p_C and a common four-dimensional
block with basis e_0,e_1,e_2,e_3. A and C use this coordinate basis. B uses
f_j=sum_{i!=j} e_i. These four f_j form a Gram-I basis over F2: self products
are 3 mod 2 and distinct products 2 mod 2.

Take five cells:

    A_pin: p_A,e_2,e_3       A_free: e_0,e_1
    B_pin: p_B,f_0,f_1       B_free: f_2,f_3
    C_pin: p_C,e_0,e_1,e_2,e_3.

Here n_1=3,n_3=4 and L=15. All cells lie in pinned components. Only A_free and
B_free can be negative. The triple equation needs four negative labels, so
both must be negative. But e_0 dot f_2=1, violating independence. The floor is
unattainable. Replacing B's f_j by e_j removes that conflict; N consisting of
the two free cells attains 15. Dimensions, multiplicities, cells and private
pins stay the same. Thus dimension/count data alone cannot decide equality.

The exact finite certificate additionally measures mixed-basis minimum 17,
coordinate-control minimum 15 and MMM minimum 18 for both, over every reduced
choice. These numerical minima are corroborated by the two implementations;
the analytic nonattainment and equality conclusions above do not depend on
that exhaustive calculation.

## Sources and unrun obligations

Every used mathematical statement is proved here. COMPARISONS retains exact
PR3569 and PR3579 proof bytes solely to identify the handoff and comparison.
They are not used proof premises or runtime dependencies. SOURCES.json pins
catalogue/selected-record provenance only. Scientific replay needs only this
package and CPython3.12, without Git objects or network.

Credit retains Nick Petalas/PR3579/3569/3560/3549/3538, Philippe Van Velzen and
Arham Tahir's expanded-identity method, Tekalign/PR3370 and the retained
P112/E8/native/compiler lineage. Author-written proof completion is distinct
from independent human or formal proof-kernel acceptance.

Nonreducing spans, partial block bases, arbitrary scalar representatives,
closures mixing groups, characteristic two, arbitrary queries and five-term
classification are outside scope. Acquisition, coefficients, frames, dirty
restoration, hosting, precision, stock, compiler/all-size supplier admission,
complete callers/consumers and outer multiplication transfer remain unrun.
