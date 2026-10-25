<!-- SPDX-License-Identifier: Apache-2.0 -->

# Sharp box floors for seven and nine rational three-total lines

## Statements

An **ordered nonzero block** of a matrix M is a sequence of distinct indices
such that every entry M_ij with i earlier than j in the sequence is nonzero.
A block of length three is also called a transitive nonzero triple.

We prove the following matrix statement over an arbitrary field K:

> Every nine-by-nine matrix of rank at most three with nonzero diagonal has
> two disjoint ordered nonzero blocks of sizes either three and three, or
> four and two.

We also prove that every seven-by-seven matrix of rank at most three with
nonzero diagonal has a transitive nonzero triple. No order, characteristic,
or positivity assumption on K is needed for either statement.

For the rational three-total application, let P,Q have nine rows and three
columns, set M=P Q^T, and assume every diagonal entry is nonzero. If the
canonical binary anchors A_i,B_i have nonempty tied sets A_i intersect B_i,
then the directed sub-anchor box satisfies **box(M)>=6**. With seven rows
under the same hypotheses, **box(M)>=5**. Both bounds are attained by
explicit rational factorizations given below.

## Rank reconstruction and the nonzero graph

Let G be the simple undirected graph with an edge {i,j} exactly when at least
one of M_ij,M_ji is nonzero. An independent set of size t gives an invertible
diagonal principal matrix of size t. Hence G has no independent set of size
four when rank(M)<=3.

If I is an independent triple, write D=M[I,I]. It is invertible and
rank(M)=3, so its Schur complement vanishes. In particular, for all indices
u,v,

    M_uv = M[u,I] D^(-1) M[I,v].                          (1)

If u,v are distinct and outside I, a nonzero M_uv forces at least one
nonzero summand M_ui D_ii^(-1) M_iv. The order (u,i,v) is then a transitive
nonzero triple. Thus, in a matrix with no such triple, the vertices outside
an independent triple are themselves independent.

## Six-row dichotomy

**Lemma.** A six-by-six matrix of rank at most three with nonzero diagonal
either has a transitive nonzero triple or has an independent triple in G.

Suppose it has neither. The elementary Ramsey fact R(3,3)=6 gives a triangle
in G. Indeed, among the other five vertices of any fixed vertex there are
either three neighbors or three nonneighbors. Three neighbors either contain
an edge, giving a triangle, or are independent. Three nonneighbors either
contain a nonedge, giving an independent triple with the fixed vertex, or
form a triangle.

A triangle without a transitive nonzero triple must have exactly the three
arcs of a directed cycle. Choosing one direction on each pair gives either
a transitive tournament or a directed cycle; in the latter case adding the
reverse of any arc would create a transitive triple. After ordering its
three vertices, its principal matrix therefore has the form

              [ a  x  0 ]
    A =       [ 0  b  y ],
              [ z  0  c ]

where a,b,c,x,y,z are all nonzero. Each outside vertex has at most one
outgoing neighbor and at most one incoming neighbor in this triangle:
two outgoing neighbors, or two incoming neighbors, together with the arc
between them would give a transitive triple.

First suppose A is invertible. Its inverse is

                  [ bc  -xc   xy ]
    A^(-1) =      [ yz   ac  -ay ] / (abc+xyz),
                  [-bz   xz   ab ]

so every entry of A^(-1) is nonzero. Rank reconstruction through A applies
to the remaining three vertices. The nonzero diagonal of an outside vertex
w forces both M[w,A] and M[A,w] to be nonzero; each has exactly one nonzero
entry by the preceding paragraph. Consequently every entry between any
two outside vertices is a product of three nonzero entries, one from each
of M[u,A], A^(-1), and M[A,v]. The three outside vertices form a transitive
nonzero triple, a contradiction.

Now suppose A is singular. Its rank is exactly two, since, for example,
the upper-left two-by-two minor has determinant ab!=0. Choose a rank
factorization of the whole matrix

    M_uv = p_u^T q_v,        p_u,q_v in K^3,

padding unused coordinates by zero. Let P_A and Q_A be the three-by-three
matrices of factor rows on the cycle. At least one of P_A,Q_A has rank two:
both have rank at least two, and if both were invertible then their product
A=P_A Q_A^T would be invertible.

Suppose first that rank(P_A)=2. Its one-dimensional space of row
dependencies equals the left kernel of A. Every coordinate of a nonzero
left nullvector lambda of A is nonzero: the three equations with nonzero
a,b,c,x,y,z propagate any one zero coordinate to all the others. For each
outside vertex w, the column M[A,w] has at most one nonzero entry. But

    lambda^T M[A,w] = lambda^T P_A q_w = 0.

Therefore that column is zero. All three outside q_w lie in the
one-dimensional annihilator of the rank-two row span of P_A. They are
nonzero because M_ww!=0. They are consequently nonzero scalar multiples
of one another, and

    M_uv = p_u^T q_v != 0

for every pair of outside vertices u,v, using M_uu!=0. This again gives a
transitive triple. If rank(Q_A)=2, apply the same argument to the transpose;
reversing an order preserves the existence of a transitive triple. Both
cases are impossible, proving the lemma.

**Seven-row consequence.** A seven-row matrix under the same rank and
diagonal assumptions has a transitive triple. Otherwise any six of its
vertices give an independent triple by the lemma. Equation (1) makes the
other four vertices independent, contradicting rank at most three.

## Exchanging across two independent triples

We next prove an exchange lemma. Suppose six vertices U of a nine-row matrix
have no transitive triple. By the six-row dichotomy they contain an
independent triple I. Equation (1) shows that J=U\I is also independent.
Both D=M[I,I] and E=M[J,J] are invertible diagonal matrices, so rank
reconstruction is available through either I or J. Denote the other three
vertices by x,y,z.

For each w in {x,y,z}, define a bipartite graph H_w on the two parts I,J.
The edge ij belongs to H_w exactly when {w,i,j} admits a transitive nonzero
ordering. We use the following exact support property:

> The vertices of I incident to H_w are precisely the neighbors of w in I
> in G. The analogous equality holds in J.

One inclusion is immediate, because a transitive triple has a nonzero
entry in at least one direction between every pair. For the other, if
M_wi!=0, reconstructing through the diagonal basis J supplies some j with
M_wj M_ji!=0. Then (w,j,i) is a transitive triple. If M_iw!=0 instead, the
same reconstruction supplies M_ij M_jw!=0, giving (i,j,w). Exchanging I,J
proves the other part. Each H_w is nonempty: reconstruction of M_ww!=0
through I gives at least one neighbor in I.

If H_w and H_v, for w!=v, contain vertex-disjoint edges, the corresponding
triples are disjoint and give the desired three-plus-three blocks. Suppose
therefore that these three nonempty bipartite edge families are pairwise
cross-intersecting: every edge of one meets every edge of either other.

### Classification of the edge families

No H_w has a matching of size three, since an edge of another family can
meet at most two edges of such a matching.

Suppose H_x contains a matching i1j1,i2j2 of size two. Every edge of H_y
and H_z must meet both matching edges. Because the graph is bipartite,
the only possibilities are the two disjoint cross edges i1j2 and i2j1.
The family H_y cannot contain both: then no edge of H_z, which is one of
those same two possibilities, could meet both. Thus H_y is a singleton.
Cross-intersection forces H_z to be the same singleton, say

    H_y = H_z = {ij}.                                     (2)

Otherwise every H_w has matching number one. Every nonempty bipartite
graph of matching number one is a star: fixing an edge, all other edges
meet it, and edges using its different endpoints would be disjoint.
If some H_w has at least two edges, every edge of either other family
contains its center. Indeed, avoiding that center would require an edge
to contain two distinct leaves, which lie in the same bipartition class.
Hence every edge in all three families contains one common center.
If all three families are singleton edges, their pairwise intersection
also forces one common center: three pairwise-intersecting edges without
a common vertex would form a triangle, impossible in a bipartite graph.

### A fully nonzero four-block

In the common-center case, suppose the center is i in I. The support
property says that each of x,y,z has only i as a neighbor in I. Its
nonzero diagonal, reconstructed through I, forces both M_wi and M_iw
to be nonzero. For all w,v in {x,y,z}, equation (1) therefore gives

    M_wv = M_wi D_ii^(-1) M_iv != 0.

Thus every off-diagonal entry on {i,x,y,z} is nonzero. A center in J is
handled identically.

In case (2), each of y,z has only i as a neighbor in I and only j as a
neighbor in J. Reconstruction of its nonzero diagonal through each basis
forces both directions to each of i,j to be nonzero. Reconstruction
through I gives nonzero entries between y,z and also

    M_yj = M_yi D_ii^(-1) M_ij,
    M_jy = M_ji D_ii^(-1) M_iy.

The left-hand sides are nonzero, so both M_ij and M_ji are nonzero.
Consequently every off-diagonal entry on {i,j,y,z} is nonzero as well.

In either case there is an ordered four-block. The five remaining vertices
contain a nonzero edge: otherwise their principal matrix would be diagonal
of rank five. Orient that edge in a nonzero direction. This supplies the
disjoint four-plus-two blocks and completes the exchange lemma.

## Completion of the nine-row matrix theorem

The seven-row consequence supplies a transitive triple among any seven of
the nine vertices. If the remaining six vertices contain another such
triple, they give the three-plus-three conclusion. Otherwise the exchange
lemma applies to those six vertices and the first triple, and gives either
three-plus-three or four-plus-two. This proves the matrix theorem.

The requirement of two triples alone would be false: diag(J_5,J_2,J_2)
has rank three, but every transitive triple lies in its five-row block.
The four-plus-two alternative is essential to this proof's conclusion.

## Transfer to the directed rational box

The directed box contract assigns retained lines an order and labels
a_i subset A_i, b_i subset B_i such that a_i dot b_i=1 over F_2. Only
forward actual zero entries impose additional equations:

    i precedes j and M_ij=0  implies  a_i dot b_j=0.

The needed scalar-to-binary implication is

    M_ij=0  implies  A_i dot B_j=0 over F_2.               (SG)

Take the two ordered blocks F,L from the matrix theorem and choose any
tied coordinate c_i in A_i intersect B_i for each retained line. Put

    (a_i,b_i)=(A_i,e_(c_i)) for i in F,
    (a_i,b_i)=(e_(c_i),B_i) for i in L.

Order F before L, keeping each internal order. All diagonal dots are one.
Within a block there is no forward zero entry. Across blocks the forward
dot is A_i dot B_j, so SG gives every required zero. This retains six
lines and proves box(M)>=6. This is the asymmetric two-block construction
from the preceding eight-line package, now combined with a stronger
matrix theorem; it is not a restriction to tied unit labels on both sides.

For canonical rational anchors, SG follows directly from actual 2-adic
normalization. Delete product columns for which one entire factor column
is zero; these do not change M. On each remaining column define

    m_j=min_i nu_2(P_ij),   n_j=min_i nu_2(Q_ij),
    gamma=min_j(m_j+n_j),
    p_ij=2^(-m_j) P_ij,     q_ij=2^(m_j-gamma) Q_ij.

Zero entries have valuation infinity. Every normalized entry has odd
denominator, and p q^T=2^(-gamma)M. Reducing modulo two gives the anchors
A_i,B_i, so every actual zero entry gives SG. Nonempty tied sets remain an
explicit hypothesis. This argument uses actual rational valuations, not
a finite valuation sentinel in an archived implementation.

## The seven-line floor and exact examples

For seven lines, take an ordered triple from the seven-row matrix
consequence. The other four vertices contain a nonzero edge, since
otherwise their principal matrix would be diagonal of rank four.
Orient that edge in a nonzero direction. The same two-block transfer
therefore proves box(M)>=5.

Both the seven- and nine-line floors are sharp. Use the retained
three-total core from PR2978:

    P_0 = [ -1 -3  0 ],       Q_0 = [ 1 -3  2 ],
          [  1 -1 -2 ]              [ 3 -1 -2 ]
          [  3  3  3 ]              [ 3 -1  2 ]

whose product P_0 Q_0^T is diag(8,8,12). Repeat corresponding factor rows
in three groups of sizes n_1,n_2,n_3. The resulting matrix is

    M = diag(8 J_(n_1), 8 J_(n_2), 12 J_(n_3)),

where J_t is the all-ones t-by-t matrix. All diagonal entries are nonzero
and the rank is three. Its canonical normalization has m=(0,0,0),
n=(0,0,1), and gamma=0. The anchors of the first two groups are
A={1,2}; those of the third group are A={1,2,3}; every B={1,2}.
All tied sets have size two.

Any witness meeting all three groups would supply three representatives
in their actual witness order. Every forward off-diagonal matrix entry
among them is zero, so the three-by-three binary matrix of their label
dots a_i dot b_j is lower triangular with diagonal ones. It has rank
three. On the other hand, all b_j are supported on the same two
coordinates, so that label-dot matrix has rank at most two. This is
impossible. A witness therefore meets at most two groups, and keeps at
most the sum of the two largest group sizes. The two-block transfer
attains that sum because each group is internally fully nonzero.

Taking (n_1,n_2,n_3)=(3,3,3) gives exactly box(M)=6 at nine lines.
Taking (3,2,2) gives exactly box(M)=5 at seven lines.

## Scope and attribution

The matrix theorem is analytic over arbitrary fields. The canonical box
corollary concerns rational three-total factorizations and uses the stated
nonzero-diagonal and nonempty-tie hypotheses. The exact examples establish
sharpness of the universal floors at seven and nine lines. The proof does
not classify every decoder, and is not a complete multiplication theorem
or a physical supplier/controller invoice.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
New work is Apache-2.0. The directed box definition, canonical normalization,
and SG implication retain the Aaron Wang/navinor predecessor attribution.
The asymmetric two-block transfer is retained from PR3409; the exact
three-total core used for sharpness is retained from PR2978.
