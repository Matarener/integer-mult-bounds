<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eight rational three-total lines have a five-line box witness

## Statement and the directed box contract

Let `P,Q` be rational matrices with eight rows and three columns, let
`M=P Q^T`, and assume `M_ii != 0` on every line. Let `A_i,B_i` be the
canonical binary anchors and suppose every tied set `A_i intersect B_i`
is nonempty. Then **box(M)>=5** for the directed sub-anchor definition.
No sharpness claim is made.

The proof uses only the following abstract hypotheses: `M` is a real
eight-by-eight matrix of rank at most three with nonzero diagonal;
`A_i,B_i` are binary support sets with nonempty intersection; and

    M_ij=0  implies  A_i dot B_j=0 over F_2.                 (SG)

A witness keeps some lines in an order and assigns labels
`a_i subset A_i`, `b_i subset B_i`, with `a_i dot b_i=1`. Its off-diagonal
requirements are only

    i precedes j and M_ij=0  implies  a_i dot b_j=0.

Thus the abstract statement is stronger than the rational canonical case,
but it does not replace the directed constraint by an unordered condition.

For completeness, canonical normalization supplies SG as follows. Remove
degenerate product columns, which do not affect M, and put

    m_j=min_i nu_2(P_ij),  n_j=min_i nu_2(Q_ij),
    gamma=min_j(m_j+n_j),
    p_ij=2^(-m_j) P_ij,    q_ij=2^(m_j-gamma) Q_ij.

Zero entries have valuation infinity. The normalized entries are rational
numbers with odd denominator, and `p q^T=2^(-gamma)M`. Their reductions
modulo two have supports `A_i,B_i`, so every actual zero reduces to the
zero binary dot product in SG. Nonempty ties are the stated hypothesis.
This is an algebraic normalization using actual rational valuations, not a
claim about unbounded inputs to a predecessor's finite valuation sentinel.

## Two ordered blocks give a box witness

Suppose disjoint sets F and L each have an ordering in which every forward
off-diagonal entry of M is nonzero. Choose a tied coordinate c_i for every
line in their union. On F use

    a_i=A_i,    b_i=e_(c_i),

and on L use

    a_i=e_(c_i),    b_i=B_i.

Order all of F first, then all of L, respecting the two given orders.
Every diagonal dot is one and every label is a sub-anchor. Within each
block there are no forward zero entries to constrain. Between the blocks,
the forward dot is the original `A_i dot B_j`, so SG supplies every required
zero. This is a witness on all of F union L.

We shall find a three-line F and a disjoint two-line L. In particular the
argument permits asymmetric labels: it does not restrict both sides to
the same tied unit vector.

## Rank three forces a transitive nonzero triple

Call distinct indices `(i,j,k)` a transitive nonzero triple if

    M_ij != 0,    M_ik != 0,    M_jk != 0.

We prove that such a triple exists. Suppose otherwise. Let G be the simple
undirected graph whose edge `{i,j}` means at least one of `M_ij,M_ji` is
nonzero. An independent set has a diagonal principal matrix with nonzero
diagonal; hence G has no independent set of size four.

First suppose G has an independent triple I. Its principal matrix
`D=M[I,I]` is diagonal and invertible. Since `rank(M)<=3`, its Schur
complement is zero. For any two indices u,v outside I,

    M_uv = sum_(i in I) M_ui M_ii^(-1) M_iv.

If `u!=v` and `M_uv!=0`, some summand is nonzero. The indices `(u,i,v)`
then form a transitive nonzero triple, a contradiction. Therefore the
principal matrix on the five vertices outside I is diagonal with nonzero
diagonal. Its rank is five, again a contradiction.

It remains that G has no independent triple. For a vertex v, its
out-neighbors in the directed nonzero graph form an independent set in G:
an edge between two out-neighbors would give a transitive triple starting
at v. Its in-neighbors are independent for the same reason. Each set
therefore has size at most two, and the undirected degree of v is at most
four.

The nonneighbors of v form a clique in G, since two nonadjacent ones
together with v would form an independent triple. G has no clique of size
four: choose one nonzero direction of each edge in such a clique, obtaining
a tournament on four vertices; some vertex has two in-neighbors or two
out-neighbors, and the edge between those two completes a transitive
triple. Thus v has at most three nonneighbors. On eight vertices its
undirected degree is at least `8-1-3=4`.

The degree bounds are equalities. The in-neighbor and out-neighbor sets
must each have size two and be disjoint, or their union would have size
less than four. Consequently

    M_ij M_ji=0 whenever i!=j.                            (1)

Choose a real rank factorization `M_ij=u_i^T v_j` with vectors in R^3,
padding unused dimensions by zero if needed, and form the three-by-three
matrices `T_i=v_i u_i^T`. The trace identity and (1) give

    tr(T_i T_j)=M_ij M_ji=0  for i!=j,
    tr(T_i^2)=M_ii^2>0.

The symmetric three-by-three real matrices have dimension six. Therefore
the eight symmetric parts `(T_i+T_i^T)/2` have a nontrivial real linear
dependence. For its coefficients c_i, not all zero, the matrix
`T=sum_i c_i T_i` is skew-symmetric, yet

    tr(T^2)=sum_i c_i^2 M_ii^2>0.

A real skew-symmetric matrix instead satisfies

    tr(T^2)=-sum_(a,b) T_ab^2<=0.

This contradiction finishes the proof that a transitive nonzero triple
exists. Positivity over the reals is used explicitly; the argument does
not assert the same matrix lemma over an arbitrary field.

## Completion of the five-line witness

Use a transitive nonzero triple as F in its defining order. Among the
remaining five vertices there is an edge of G, since otherwise their
principal matrix would be diagonal of rank five. Orient that edge in a
nonzero direction and use its two vertices as L. The two-block construction
keeps `3+2=5` lines and proves the theorem.

## The six-line consequence of the same construction

With six lines, the nonzero graph G has two disjoint edges. Otherwise its
edges pairwise intersect, so it is a star, a triangle with isolated vertices,
or empty; each possibility has an independent set of four and therefore a
diagonal rank-four principal matrix. Orient the two disjoint edges in nonzero
directions and use them as the two blocks. The same construction gives
`box(M)>=4`. Thus the transfer argument also gives a short proof of PR3393's
six-line result, without its anchor-type case analysis.

## Scope

The proof is analytic and has no finite-census premise. It proves the scoped
box bound, not a complete multiplication theorem, a new selected frontier,
or a physical supplier/controller invoice. It does not prove `box>=6` at nine lines or an upper bound of five at eight lines.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
New work is Apache-2.0. The directed box definition, canonical normalization,
and SG implication retain the Aaron Wang/navinor predecessor attribution.
