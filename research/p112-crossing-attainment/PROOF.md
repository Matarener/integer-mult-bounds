# Exact residual tariffs for coordinate-aligned crossing cells

## Contract

Work in a finite binary label space with an orthonormal coordinate basis e_h.
Three disjoint indexed groups A,B,C contain at most one copy of each e_h per
group. Each used coordinate occurs in one, two or three groups. Partition each
group into nonempty cells, with one representative index per cell. Cells may
cross arbitrarily many coordinates. Let a,b,c be the scalar unit-indicator
vectors of the respective representatives. Extra ambient indices are allowed,
with closure cells disjoint from the target groups. Closure includes a whole
cell when its scalar support meets that cell. A term u q^T costs

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The target operator is aa^T+bb^T+cc^T, over any coefficient field of
characteristic different from two. Only the following fixed query lists are
studied, in displayed order:

    VVV: a+b, a+c, b+c, a+b+c
    MMM: a+b-c, a-b+c, -a+b+c, a+b+c.

Readers may be arbitrary ambient vectors. Let n_k count coordinates occurring
in k groups. The original three-term tariff is D=n_1+2n_2+3n_3. Coordinates
are distinguished even when they have the same cell incidence. Repetition is
therefore an integer weight, not duplicate indexed copies inside one group.

Unlike PR3569's full-basis block theorem, different bases inside a shared block
are excluded here. The gain is an exact optimum and an attainment criterion,
rather than a stronger universal lower bound.

## The exact energy theorem

Give each cell a value x in {0,+1,-1}. Define a nonnegative integer energy E(x)
by adding these contributions over the used binary coordinates:

- A coordinate present once contributes 0,1,2 when its cell has value +1,0,-1.
- A coordinate present twice contributes zero if its two cell values are both
  zero, or are both nonzero with at most one value -1. It contributes one otherwise.
- A coordinate present three times contributes zero if its three values are
  all zero, or are all nonzero with exactly one value -1. It contributes one
  otherwise.

Then the exact minima, including arbitrary ambient readers, are

    VVV_min = n_1+3n_2+3n_3 + min_x E(x),
    MMM_min = 2n_1+3n_2+3n_3.

These are support tariffs, not a physical execution bill.

### All readers reduce to finite cell choices

The scalar vectors a,b,c are independent because they are nonzero with disjoint
supports. Coefficient comparison gives every exact reader solution:

    VVV 2u: a+b-c-w, a-b+c-w, -a+b+c-w, 2w;
    MMM 2u: a+b-v, a+c-v, b+c-v, v.

Here w or v is an arbitrary ambient vector. Direct multiplication verifies the
formulas and the target identity. Conversely, comparison in each of a,b,c
solves the three equations in four reader coordinates with that one free vector.
Thus no reader-span assumption is hidden in the parametrization.

Set the parameter to zero outside the representatives. There, every reader
coefficient is a scalar multiple of that parameter, so no support grows. At a
representative, replacing a VVV value outside {0,1,-1} by zero only removes
support, since all four coefficients were nonzero before replacement. For MMM
the corresponding set is {0,1}. These values remain distinct in every allowed
characteristic. Each modified solution is still exact by the displayed formulas.
Removing support cannot enlarge a closure or the rank of a rectangular submatrix.
The minimum therefore occurs with one ternary or binary choice per cell.

### Count the actual rectangular ranks

Every label is one coordinate vector. Each coordinate occurring on both sides
of a rectangular Gram matrix gives a nonzero all-ones block, of binary rank one.
Different coordinates pair to zero. Repeated copies from different groups do
not change that rank. Hence a term costs exactly the number of coordinates
present in both its query closure and its reader closure.

For VVV, at an A representative the four reader support masks are

    x=0: 1110; x=+1: 0011; x=-1: 1101.

For B and C, respectively, the +1 masks are 0101 and 1001, and the -1 masks
are 1011 and 0111. Their zero masks are also 1110. A coordinate present once
meets three query closures. Its total charge is 1,2,3 for +1,0,-1. A coordinate
present at least twice meets all four query closures. Its charge is the number
of nonempty reader positions in the union of its cell masks.

For two masks that union has size three exactly in the two-value cases listed
in E, and size four otherwise. For three masks it has size three exactly for
000, -++, +-+, ++-, and size four otherwise. This proves the VVV formula for
every reduced choice. Each choice is an actual exact reader solution, so
minimizing E gives both a lower bound and an attaining construction.

For MMM, each coordinate present once has exactly two nonzero reader positions.
For two groups the respective zero-choice masks are 1100,1010,0110. Allowing
binary parameter values, the union of two or three masks always has at least
three positions. For completeness, a missing position for A,B requires one
of the four distinct value pairs 11,10,01,00; two distinct positions cannot be
missing at once. Adding C only adds support. Thus each multiple coordinate
costs at least three. Setting every v to zero attains two for a singleton and
three for every multiple coordinate, even with crossing cells. This proves
MMM's exact formula.

## A componentwise exact-cover criterion

Make a finite incidence hypergraph whose vertices are cells. A coordinate
present in two or three groups gives an edge of size two or three. Singleton
coordinates pin their cell to +1. Multiplicities of an edge are immaterial to
zero energy. Connectivity means a chain of these edges; isolated cells are
components too.

The VVV block bound n_1+3n_2+3n_3 is attained if and only if, in each component
containing a pin, there exists a set N of unpinned cells such that

    every three-edge meets N exactly once,
    every two-edge meets N at most once.

Components without pins impose no condition.

Proof: zero energy forces every pinned cell to +1. In a zero-energy edge,
either every value is zero or every value is nonzero. Zero/nonzero status
therefore propagates across a connected component. A pinned component has no
zero values. The energy table then says its negative cells form exactly the
set N above. Conversely, given N, assign -1 to N and +1 to all other cells in
each pinned component, and assign zero throughout every unpinned component.
Every energy contribution is zero. Isolated pinned cells receive +1.

This is a finite exact-cover-with-conflicts criterion, with an explicit reader
construction. No polynomial-time complexity claim or NP-completeness claim is
made. It separates a global cell-consistency obstruction from a blockwise rank
bound. The theorem does not independently choose a minimizer for each coordinate.

## A sharp unbounded family and its optimal-reader transition

Take one cell per group. Group G contains s_G distinct private coordinates and
m common coordinates, with s_A,s_B,s_C,m positive integers. The common
coordinates have distinct indexed copies in all three groups. Write
S=s_A+s_B+s_C and s=min(s_A,s_B,s_C). Then

    D = S+3m,
    VVV_min = S+3m+min(m,2s),
    MMM_min = 2S+3m.

To prove the VVV excess, all +1 has energy m. A nonzero assignment with exactly
one negative cell has energy 2s_G, minimized at 2s. All zero has energy S>=3s.
Any other assignment containing a zero has a bad common triple and positive
private penalties, so costs at least m. Any other all-nonzero assignment also
has a bad common triple and nonnegative private penalties, so costs at least m.
These cases exhaust all 27 choices and prove the formula.

For m<2s, all +1 is optimal; for m>2s, negating a smallest private group is
optimal. At m=2s both constructions attain the minimum. The previous four-line
example is s_A=s_B=s_C=m=1, with VVV minimum 7 and MMM minimum 9. The family
s_A=s_B=s_C=t, m=2t has exact VVV excess 2t in one connected three-cell
component. Thus crossing-cell excess is unbounded, even in this restricted
coordinate-aligned model. This is an additive support penalty, not an improved
multiplication exponent.

## Provenance and limits

The proof is self-contained. COMPARISONS retains PR3569's exact proof solely as
the source of the changed question and earlier 7/9 example. No predecessor
classification, support-transfer theorem, proof or runtime is an input premise.
Credit retains Nick Petalas/PR3569/3560/3549/3538, Philippe Van Velzen and Arham
Tahir's expanded-identity method, Tekalign/PR3370 and the P112/E8/native/compiler
lineage. Finite replay corroborates the formulas; this written argument supplies
the unbounded quantifiers. Author-written proof completion does not claim
independent human or formal proof-kernel acceptance.

Different shared-block bases, nonreducing spans, partial block bases, arbitrary
scalar representatives, closures mixing target groups, characteristic two,
arbitrary queries and five-term classifications are outside scope. Native
acquisition, coefficient execution, frames, dirty restoration, hosting,
precision, stock, compiler/all-size admission, complete suppliers/consumers and
outer multiplication transfer are unrun. No supplier, kappa improvement or
selected-frontier change is claimed.
