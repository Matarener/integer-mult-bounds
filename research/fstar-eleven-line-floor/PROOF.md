<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eleven rational three-total lines have a seven-line box witness

## Statements

An ordered nonzero block of a matrix M is a sequence of distinct indices
such that M_ij is nonzero whenever i precedes j in the sequence. A block
of size three is called a transitive nonzero triple.

We prove over an arbitrary field K:

> Every eleven-by-eleven matrix of rank at most three with nonzero
> diagonal contains an ordered nonzero block of size four.

Its seven-row complement contains a transitive nonzero triple by the
preceding seven-row matrix lemma. Thus there are disjoint ordered blocks
of sizes four and three.

Consequently, if rational P,Q have eleven rows and three columns,
M=P Q^T has nonzero diagonal, and every canonical tied set is nonempty,
then the directed sub-anchor box satisfies **box(M)>=7**. This proof does
not claim sharpness of the seven-line floor.

## Two preliminary matrix lemmas

**Rank-two half-size lemma.** A matrix of rank at most two with nonzero
diagonal has an ordered nonzero block of size at least ceil(n/2).

Write M_ij=p_i^T q_j with nonzero vectors p_i,q_i in K^2, and partition
the q_j into projective directions, meaning nonzero proportionality
classes. The zeros in row i consist of at most one complete class:
the kernel of the nonzero functional p_i^T has only one projective
direction. This forbidden class, if present, differs from i's own
class because M_ii is nonzero.

Choose a uniformly random order of the finitely many classes. Retain
row i when its forbidden class is earlier than its own class, retaining
every row without a forbidden class. Order retained indices by their
classes, with arbitrary order inside each class. Every zero from a
retained row points to an earlier class; all entries within a class
are nonzero by the diagonal condition. The retained order is therefore
an ordered nonzero block. Each row is retained with probability at least
one half, so some order retains at least ceil(n/2) rows.

**Seven-row triple lemma.** A seven-by-seven matrix of rank at most three
with nonzero diagonal has a transitive nonzero triple. This is the
arbitrary-field lemma proved in PR3420; we recall its argument here.

Suppose no triple exists. Let G join distinct indices when at least one
of the two corresponding matrix entries is nonzero. If G has an
independent triple I, its principal matrix D is diagonal and invertible.
Rank reconstruction gives, for all u,v,

    M_uv = M[u,I] D^(-1) M[I,v].                          (1)

A nonzero entry M_uv with distinct u,v outside I has a nonzero summand
through some i in I, giving the transitive order (u,i,v). Hence the four
outside vertices are independent, contradicting rank at most three.

Otherwise G has no independent triple. The elementary Ramsey fact
R(3,3)=6 gives a triangle. To recall that fact, among the other five
vertices of a six-vertex graph some vertex has either three neighbors
or three nonneighbors; inspecting edges among those three produces a
triangle or an independent triple. A triangle with no transitive
nonzero triple has exactly the arcs of a directed three-cycle. Its
principal matrix can be written

    A = [[a,x,0], [0,b,y], [z,0,c]],

with all six displayed entries nonzero. Every outside vertex has at
most one outgoing and at most one incoming neighbor in this triangle;
two such neighbors would give a transitive triple.

If A is invertible, every entry of its inverse is nonzero: its adjugate
is [[bc,-xc,xy], [yz,ac,-ay], [-bz,xz,ab]]. Rank reconstruction through A
and the nonzero outside diagonals force each outside row and column
against A to have exactly one nonzero entry. Every entry between outside
vertices is then nonzero, supplying a transitive triple.

If A is singular, its rank is two. Factor the whole matrix as
M_ij=p_i^T q_j in K^3. At least one of the three-by-three cycle factors
P_A,Q_A has rank two. Suppose it is P_A. Its row dependence spans the
left kernel of A, whose nonzero vectors have all three coordinates
nonzero, as follows directly from the cycle equations. Every outside
column into A has at most one nonzero entry and satisfies that dependence,
so the entire column is zero. All outside q-vectors lie in the same
one-dimensional annihilator of the rows of P_A. They are nonzero by
the diagonal condition, hence are nonzero scalar multiples of each
other. Every entry between outside vertices is therefore nonzero,
again giving a triple. If Q_A has rank two, transpose the argument.
This proves the seven-row lemma without an order or positivity
assumption on the field.

## Repeated factor directions are impossible in an obstruction

Suppose, for contradiction, that an eleven-row matrix as in the theorem
has no ordered four-block. The half-size lemma rules out rank at most
two. Fix a rank-three factorization M_ij=p_i^T q_j with vectors in K^3.

We first exclude three proportional p-rows. Such rows form a fully
nonzero three-block, since each diagonal is nonzero. Any outside column
is either zero on all three rows or nonzero on all three. The latter
would extend their block to four. Thus all eight outside q-vectors lie
in the common two-dimensional annihilator of that p-direction. Their
principal matrix has rank at most two, so the half-size lemma gives a
four-block. This is impossible. Transposition excludes three
proportional q-rows as well.

Suppose now that two p-rows a,b are proportional. They form a fully
nonzero pair. Among the other nine indices let S be those whose
q-vectors are not annihilated by that common p-direction, and Z the
rest. Any nonzero edge within S, preceded by (a,b), would make a
four-block. Thus S is independent and |S|<=3. The q-vectors on Z lie
in a plane, so M[Z,Z] has rank at most two and the half-size lemma
implies |Z|<=6. Equality is forced in both bounds:

    |S|=3,             |Z|=6.

Use the independent S triple as a rank basis. An invertible change of
factor coordinates and individual nonzero row and column scalings
preserve all zero patterns and allow the normalization

    p_s=q_s=e_s for s=1,2,3 in S,
    p_a=p_b=(1,1,1).

For clarity, first change factor coordinates so that P_S is the identity;
then Q_S is diagonal, and column scalings make Q_S the identity too.
Every coordinate of the common p-direction is nonzero since it is
nonzero on every q_s. A diagonal coordinate change makes that direction
(1,1,1), and row and column scalings on S restore p_s=q_s=e_s.

Every q_z is a nonzero vector in the plane

    H = { (x_1,x_2,x_3) : x_1+x_2+x_3=0 }.

Each s in S has at most four outgoing neighbors in Z: five such
neighbors have a rank-at-most-two principal matrix, hence an ordered
triple by the half-size lemma, which s could precede. Each coordinate
therefore vanishes on at least two of the six q_z. A nonzero vector in
H has at most one zero coordinate. Counting forces exactly two q_z
in each of the three distinct projective directions

    H intersect {x_1=0}, H intersect {x_2=0}, H intersect {x_3=0}.

Fix one of these proportional q-pairs U={u,v}, whose zero coordinate
is i, and let j,k be the other coordinates. All rows outside U with
nonzero entries into U must be independent: otherwise their nonzero
edge followed by (u,v) gives a four-block. Those rows include s_j,s_k.
If any z in Z outside U had a nonzero entry into U, independence would
force M[z,s_j]=M[z,s_k]=0. Since q_s=e_s, its p_z would then be supported
only on coordinate i. This would give p_z^T q_u=0, a contradiction.

Thus every row in Z outside U has zero entries into U. Applying this
to all three q-pairs makes M[Z,Z] block diagonal with three two-by-two
blocks. Each block has proportional columns and nonzero diagonal, hence
rank exactly one. The resulting rank three contradicts rank(M[Z,Z])<=2.
This excludes any repeated p-direction. By transposition, the q-directions
are also all distinct.

## The projective incidence contradiction

For each vertex v, its nonzero out-neighborhood has no transitive triple,
since prefixing v would give a four-block. The seven-row lemma therefore
bounds this neighborhood by six. Of the ten off-diagonal entries in
row v, at least four are zero.

The eleven distinct q-directions are eleven projective points. The
eleven distinct p-directions define eleven distinct zero lines, where
the line for p_i consists of the directions annihilated by p_i. Each
such line contains at least four of the eleven points. Two distinct
lines cannot contain the same pair of distinct points: two distinct
q-directions span a plane whose annihilator has only one projective
direction. Counting unordered point pairs on the lines gives

    66 = 11 * binom(4,2)
       <= sum_i binom(number of points on line i,2)
       <= binom(11,2) = 55.

This contradiction proves the ordered-four-block theorem over K.

## Transfer to the directed rational box

Take an ordered four-block F from the theorem. Its seven-row complement
has an ordered triple L by the seven-row lemma. We use the asymmetric
two-block transfer retained from PR3409 and PR3420.

The binary anchor hypotheses are nonempty ties A_i intersect B_i and

    M_ij=0 implies A_i dot B_j=0 over F_2.                (SG)

Choose c_i in A_i intersect B_i on every retained line. On F use
(a_i,b_i)=(A_i,e_(c_i)); on L use (a_i,b_i)=(e_(c_i),B_i). Order F
before L, keeping their internal orders. All labels are sub-anchors
and every diagonal dot is one. Inside each block there is no forward
zero entry. Across the blocks the forward dot is exactly A_i dot B_j,
so SG enforces every required zero. This is a seven-line witness under
the directed contract, which imposes constraints only when i precedes j
and the actual matrix entry M_ij is zero.

For canonical rational anchors, SG follows from actual 2-adic
normalization. Delete product columns for which an entire factor column
is zero, and set

    m_j=min_i nu_2(P_ij),   n_j=min_i nu_2(Q_ij),
    gamma=min_j(m_j+n_j),
    p_ij=2^(-m_j)P_ij,      q_ij=2^(m_j-gamma)Q_ij.

Zero entries have valuation infinity. The normalized entries have odd
denominator and p q^T=2^(-gamma)M. Their reductions modulo two define
A_i,B_i, so an actual zero entry gives SG. Nonempty ties remain an
explicit hypothesis. This uses actual rational valuations, not a finite
valuation sentinel in an archived implementation.

## Scope and attribution

The matrix theorem is analytic over arbitrary fields. The canonical
box corollary is for rational three-total factorizations with the stated
nonzero-diagonal and nonempty-tie hypotheses. No eleven-line example
attaining exactly seven is claimed: the README's (4,4,3) duplicate-core
control has box eight. The next unresolved floor threshold is twelve
lines and box at least eight. This is not a complete multiplication
theorem, a new selected frontier, or a physical supplier/controller invoice.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
New work is Apache-2.0. The directed box definition, canonical normalization,
and SG implication retain the Aaron Wang/navinor predecessor attribution.
The seven-row matrix lemma is retained from PR3420 at head
e2d39da9c7109f361d6cff677cf9f8eba51f3dd6; the asymmetric two-block
transfer is retained from PR3409 and PR3420.
