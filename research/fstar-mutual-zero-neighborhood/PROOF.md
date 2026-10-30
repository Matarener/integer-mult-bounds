<!-- SPDX-License-Identifier: Apache-2.0 -->

# Correct classification of mutual-zero neighborhoods

Let M be a matrix over any field K with rank at most three and nonzero
diagonal. Define its mutual-zero graph G_0 on the matrix indices by

    {i,j} is an edge iff i!=j and M_ij=M_ji=0.

For a vertex t, let N(t) be its open neighborhood in G_0.

**Theorem.** Every induced graph G_0[N(t)] is a disjoint union of
complete bipartite components and isolated vertices. In particular,
every such neighborhood is bipartite and contains no odd cycle.

There is no parallelism assumption on the factors of the center.

## Rank-two classification

First consider any matrix B of rank at most two with nonzero diagonal.
Factor B_ij=u_i^T v_j with u_i,v_i in K^2, padding a rank-one
factorization if needed. Every factor vector is nonzero by the
diagonal condition. Let alpha_i be the projective direction of v_i,
and let beta_i be the projective direction of the one-dimensional
kernel of the nonzero functional u_i^T. The diagonal condition says

    alpha_i != beta_i.

A mutual-zero edge between i and j is equivalent to

    alpha_j=beta_i and alpha_i=beta_j.

Group vertices by their ordered type (alpha,beta). A vertex of type
(a,b) can have neighbors only of type (b,a), and every vertex of the
first type is adjacent to every vertex of the reciprocal type. Since
a!=b, there are no edges inside either type. Distinct unordered pairs
{a,b} give disjoint components. If both reciprocal types occur, they
give one complete bipartite component; if only one occurs, all its
vertices are isolated. This proves the classification for B.

The argument is valid in every characteristic. Rank one needs no
exception beyond the two-dimensional embedding; its mutual-zero graph
is edgeless. An empty index set is immediate.

## Apply the classification to a neighborhood

Choose a rank factorization M_ij=p_i^T q_j in K^3. The nonzero center
diagonal ensures p_t is nonzero. Every i in N(t) satisfies
p_t^T q_i=0, so all q_i on N(t) lie in the two-dimensional plane
ker(p_t^T). Hence the principal matrix M[N(t),N(t)] has rank at most
two and still has nonzero diagonal. Its mutual-zero graph is exactly
G_0[N(t)]. The preceding classification proves the theorem.

An odd wheel would have its odd rim cycle entirely inside the open
neighborhood of its hub. A bipartite neighborhood cannot contain that
cycle, even as a non-induced subgraph. Thus the no-odd-wheel conclusion
of the predecessor's Lemma C4 remains valid, now for every odd rim length.

## The error in the retained C5 case split

The source being corrected is Aaron Wang/navinor's PR2890, head
`08a44355403604c346f8d907811edce992382cc4`,
`research/fstar-chi4-zero-digraph-seed73765f29/README.md`, Lemma C5
(lines 100--118 in the retained bytes). The retained README has Git blob
`acbea2b0ffc66a87573bcd53bfcd24d3e5a17956` and SHA256
`87e1de6007d5f4770048153f188561bb2f68720fddaf45938da134f02654e931`.

Its nonparallel branch asserts that the neighborhood has no edges.
The proposed normalization q_t=e_1, p_t=e_2 would instead force
M_tt=p_t^T q_t=0, contrary to the standing diagonal hypothesis.
The parallel branch's same-type clique option also disappears when
the nonzero diagonal is enforced: the reciprocal type (a,a) is
forbidden. The uniform classification above avoids this case split.

For clarity, the coordinate changes preserving a factorization are
dual changes. For any invertible S,

    q_i -> S q_i,       p_i -> S^(-T) p_i

leave every entry p_i^T q_j unchanged. Parallelism between p_t and q_t
is not invariant under these changes. In fact, since p_t^T q_t=d!=0,
choose a basis beginning with q_t and completed by a basis of ker(p_t^T).
The resulting dual coordinates give q_t=e_1 and p_t=d e_1. Every
admitted center permits this normalization, regardless of whether its
original factor vectors were parallel.

## Minimal admitted rational counterexample

Take the three-row rational factors

    P = [[1,1,0], [1,0,1], [0,1,1]],
    Q = [[1,1,-1], [1,-1,1], [-1,1,1]].

Their product is M=P Q^T=2 I_3. The center 0 has nonparallel factors
p_0=(1,1,0), q_0=(1,1,-1). Its mutual-zero neighborhood consists of
vertices 1 and 2, which are adjacent. This contradicts the asserted
empty nonparallel neighborhood. Three vertices are minimal for an
edge inside an open neighborhood: one center and two distinct neighbors
are necessary.

All three factor columns are active. Their 2-adic column minima and
the global normalization exponent gamma are zero. The canonical binary
anchor masks are A=(3,5,6), B=(7,7,7); every tie has size two. Thus the
counterexample also lies in the admitted all-even rational anchor domain.

Four copies of each paired factor row give twelve rows and
M=2 diag(J_4,J_4,J_4). A center's neighborhood is K_(4,4). Giving the
three groups the respective unit-label masks 1,4,2 gives a full
twelve-line box witness: each unit belongs to its group's tie, and
different groups have zero binary dots. This is a counterexample to
the published C5 branch, not to the twelve-line box-eight target.

## Scope and attribution

The corrected classification and odd-wheel consequence are analytic
over arbitrary fields. The explicit counterexample and its canonical
anchor admission are over Q. No predecessor engine or census is needed
for this correction, and no changed census result is asserted. This
does not prove F-star, close the twelve-line bound, or change the selected
multiplication frontier.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
New work is Apache-2.0. The predecessor C3/C4/C5 statements and F-star
context retain Aaron Wang/navinor's attribution. The exact retained
README is the source identified above.
