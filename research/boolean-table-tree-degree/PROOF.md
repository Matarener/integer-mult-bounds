# A sharp degree obstruction for tree table splitting

produced by Nick Petalas. Apache-2.0.

## Contract

Let F be a field of characteristic zero, or F_101. A table T has d>=1
external Boolean indices and entries in F. An exact tree realization has
a finite nonempty tree of tensor vertices. Each external index attaches
to exactly one vertex. An internal tree edge carries k_e Boolean wires,
where k_e is a nonnegative integer. Contracting their indices produces T
on every external input. Internal tensor coefficients are unrestricted
elements of F. The degree of a vertex is its number of external wires
plus the sum of k_e over its incident edges. Parallel wires count
separately. A bundle of zero wires has dimension one.

The tree is the graph after replacing parallel internal wires by one
edge. Vertex count, topology and bundle widths have no imposed upper
bound. Every realization is finite. External indices cannot be copied
to multiple vertices without including the corresponding copy tensors
and wires in this graph.

## General lemma

Suppose every nonempty proper bipartition A | A-complement of the d
external indices has matrix rank 2^min(|A|,d-|A|). Then the minimum
possible maximum vertex degree in this contract is exactly d.

Remove an internal tree edge e. If its two components have a and d-a
external indices, contracting each component first expresses the
corresponding flattening as a product of matrices with inner dimension
2^k_e. Consequently, when 0<a<d,

```text
2^min(a,d-a) = rank(T_A) <= 2^k_e,
k_e >= min(a,d-a).
```

For a=0 or a=d, the same final inequality is just k_e>=0.
This is the classical tensor flattening cut bound. It holds over the
stated field regardless of signs, zero coefficients or cancellations.

Give each tree vertex weight equal to its number of attached external
indices. A weighted centroid v has at most d/2 weight in every component
of the tree after v is removed. Such a vertex exists. Orient an edge
toward a component of weight greater than d/2 whenever one exists. An
edge cannot be oriented both ways. In a finite tree, following outgoing
edges cannot form a cycle, so there is a vertex with no outgoing edge.
This vertex is a weighted centroid. If no edge is oriented, any vertex
works.

Write a_v for its external degree and b_1,...,b_t for the external weights
of its incident components. They partition the external indices, so
a_v+sum(b_i)=d, and b_i<=d/2. The edge inequalities give

```text
degree(v) = a_v + sum(k_i)
          >= a_v + sum(min(b_i,d-b_i))
           = a_v + sum(b_i) = d.
```

The original table stored at one vertex has degree d and attains the
bound. This proves the lemma for all finite trees, rather than only
for enumerated topologies.

## The explicit Boolean table

Take d=8 and the 32 bytes encoded in TABLE.json. For an input x in
{0,1}^8 set i=sum(x_j 2^j), with j starting at zero. T(x) is bit i%8 of
byte i//8, with the low bit numbered zero. This specifies all 256 values;
121 are one. The hex string is a literal witness, not a hash-only
description of an unknown table.

The finite certificate checks every unordered nontrivial bipartition.
Choose its representative mask m with 1<=m<128; complementation gives
the other member. For each cut choose the smaller side as rows. The
complete census is

```text
smaller side size       1   2   3   4
number of cuts          8  28  56  35
certified matrix rank   2   4   8  16
```

The verifier finds pivot columns by elimination modulo the prime 101.
It then reconstructs the selected square minor separately by scanning
all complete input words, and computes its integer determinant using
fraction-free elimination. All 127 determinants are nonzero modulo 101.
Thus each determinant is nonzero over F_101 and over every field of
characteristic zero. The number of rows is already an upper bound on
rank, proving equality on every cut.

Apply the general lemma. Every exact tree realization of this Boolean
membership table has a vertex of degree at least eight. One vertex
holding T attains eight. No tree replacement with maximum degree seven
exists, even with unbounded vertex count, arbitrary internal coefficients
and arbitrarily wide Boolean bundles.

This explicit table and its application to the table-splitting question
are the new result. The flattening method and weighted centroid argument
are standard. No claim of literature priority for those methods is made.

## Why the graph hypothesis matters

The verifier contracts a four-site cycle as a boundary control. Each
vertex has one external Boolean index and two internal Boolean indices,
hence degree three. Site i has the two 2-by-2 matrix slices written
literally in cycle_boundary(). Its external table is

```text
42 62 52 48 26 36 30 32 16 24 16 16 12 16 12 16.
```

All seven nontrivial bipartitions of that four-index table have full rank,
certified by exact integer minors. Thus full flattening ranks alone do
not give degree at least d for cyclic networks. This is a contract control,
not a Boolean membership-table construction for the open cyclic case.

## Relation to the question and limits

Jacob Sussman's PR #5817 asks whether vector tables can be split into
low-degree tensor vertices while keeping the total wire count small.
The present result excludes exact acyclic replacements as a universal
degree-reducing method for arbitrary tables. It needs neither a wire-count
cap nor a particular tensor-contraction algorithm. Its proof does not
assume any unreviewed complexity-theoretic claim from that source.

The explicit Boolean table has eight axes. There is no claim here that
Boolean tables with the same full-cut-rank property exist at every larger
dimension, or that the degree cap of a particular asymptotic contraction
theorem is violated by this fixed-size instance. Cyclic networks,
approximations, structured table families, duplicated external inputs
with a different contract and non-Boolean internal alphabets require
their own analysis. In particular this is not a general Orthogonal
Vectors lower bound, an impossibility of all vector-table splitting,
a new multiplication exponent or a complete multiplication theorem.

The universal tree implication is a written proof. The table-rank claim
is a finite exact computation. Independent human and formal proof-kernel
review are unclaimed.
