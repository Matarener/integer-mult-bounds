# A simultaneous lift for functional decoder pairings

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped proof, with finite exact corroboration.

## Statement

Let B be a v-by-v binary matrix with B_ii=1. Suppose each row has at most
one off-diagonal one. There is an integer matrix S with the same support,
diagonal one, and all nonzero entries in {1,-1}, such that every square
minor of S is 0, 1 or -1. Consequently, for every pair of row and column
sets R,A and every field K,

    rank_K S[R,A] = rank_F2 B[R,A].

The same conclusion holds when the column condition replaces the row
condition. One signing works simultaneously for all rectangular blocks.
No support sets need to be supplied to the construction.

For any field K, let p_t,q_t belong to K^T, with finite T, and suppose

    p_t dot q_t != 0,
    p_t dot q_s = 0 whenever t != s and B_ts = 1.

Put R_j={t:p_tj != 0}, A_j={t:q_tj != 0}. Then

    sum_j rank_F2 B[R_j,A_j] >= v.

For each B in the stated class the bound is attained if the number of
totals is unrestricted. This does not assert attainment with T=3.

## Constructing the signing

Write f(i)=j for the off-diagonal one in row i, leaving f(i) undefined
when there is none. Its directed cycles have distinct vertices and length
k>=2. Distinct cycles are vertex-disjoint because each vertex has at most
one successor.

Start with S=B over the integers. On each directed cycle of length k,
choose its least-indexed vertex i and replace S_i,f(i) by (-1)^k.
All other supported entries remain one. In particular, even cycles need
no change; odd cycles receive one minus sign. The cycle-edge product is
always (-1)^k.

The implementation first removes vertices of indegree zero, then walks
the remaining cycles. Each vertex enters the removal queue at most once,
and each remaining vertex is walked once. Given successor lists this is
linear work and storage in v. Reading and returning a dense matrix takes
O(v^2) work and storage. The implementation caps v at 256; the written
theorem has no such bound.

## Every minor is zero or a unit

Consider any square submatrix. If it has a zero row or column its
determinant is zero. If a row or column has just one nonzero, expand along
it. The multiplier is 1 or -1. Repeat, reducing the order each time.
The empty determinant is one.

If a nonempty square core remains with every row and column of degree at
least two, each row has exactly two nonzeros, since every original row
had at most two. Counting entries shows that each column also has degree
exactly two. Both supported entries of every remaining row are present,
including its original diagonal. Thus the remaining row set is contained
in the remaining column set. Equal cardinalities make those sets equal.
The remaining successor map is a permutation without fixed points.
Its components are complete directed cycles from the original f.

For a cycle of length k, the corresponding block has precisely two
nonzero determinant terms: the diagonal product 1 and the cycle product
with permutation sign (-1)^(k-1). Its determinant is

    1 + (-1)^(k-1) (-1)^k = 0.

After simultaneous row and column reordering the core is a nonempty
block diagonal union of such blocks, so its determinant is zero.
Undoing the leaf expansions proves that every minor is 0, 1 or -1.

This is an elementary total-unimodularity argument. No historical novelty
is claimed for total unimodularity or the leaf-expansion method. The new
decoder reduction is the simultaneous functional-pairing lift and its
all-T consequence in the retained cost model.

## Field-independent ranks

Reduction of S modulo two is B. A nonzero integer minor of S is 1 or -1,
which stays nonzero in every field. A zero minor stays zero. The largest
nonzero minor therefore has the same order over every field, including
F2. Apply this separately to every rectangular submatrix. The empty-row
and empty-column cases have rank zero. Transposition proves the column
version without a new signing argument.

## The decoder cost floor

This step is the Hadamard/lift rank argument credited to #1590 and #2111.
It is included to state exactly what the new sufficient lift permits.
Let M_ts=p_t dot q_s. The matrix M Hadamard S is diagonal with nonzero
diagonal, hence has rank v over K. It is also

    sum_j diag(p_:j) S diag(q_:j).

The j-th summand has rank rank_K S[R_j,A_j]: removing its zero rows and
columns leaves invertible diagonal rescalings. Rank subadditivity and
the simultaneous rank identity give

    v <= sum_j rank_K S[R_j,A_j]
      = sum_j rank_F2 B[R_j,A_j].

For tightness with unrestricted T, choose T=v and p_t=q_t=e_t. Then
M=I is compatible with every unit-diagonal B, and each of the v terms
has binary block rank one. This only establishes tightness of the bound
over the union of all finite-T decoder classes.

## Scope and consequences

The theorem excludes every pairing in this sparse class from beating v,
including three-total configurations with full-support points, arbitrary
coefficients and repeated geometric points or lines. It strengthens the
available list of sufficient reductions; it does not solve #2111's
general lift problem or claim a new theorem for arbitrary pairings.

The condition is on the chosen pairing B, not just a selected subset of
its incidences. A configuration whose entire allowed off-diagonal pattern
has outdegree at most one inherits the bound for every admissible B.
Otherwise, excluding its functional pairings alone need not exclude a
cheaper nonfunctional pairing. No decoder, native word, paid supplier,
physical restoration, recursive invoice or improvement to kappa follows.

The full multiplication theorem's native, ownership, compiler,
precision/tape and analytic assumptions are not discharged. No formal
proof-kernel or independent human review is claimed.
