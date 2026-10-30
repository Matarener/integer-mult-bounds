# An encoded-width constructor for theta(2,3,3)

This scoped proof and constructor were produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Contract and new result

Use vertex order `(u,v,a,b,c,d,e)` and edge order
`(ua,av,ub,bc,cv,ud,de,ev)`. A width vector `d` consists of seven arbitrary
nonnegative integers. Put `S=sum(d)` and

```
nu(d) = max sum_e x_e
        over integer x_e >= 0 with sum_(e incident v) x_e <= d_v.
```

JoyboyBrian's [PR #5218](https://github.com/CrocSwap/integer-mult-bounds/pull/5218),
retained in `research/theta-query-capacity`, proves that the exact fitting
rank is `S-nu(d)` over every field. Its contract has identity diagonal blocks,
zeros on both ordered nonedge blocks, and arbitrary directed rectangular
edge blocks. We cite that theorem. We do not replay its proof or verifier.
Its attaining residual-state dynamic program has a stated bound
`product_v(d_v+1)` on its states.

The new result is an optimal compressed constructor whose number of integer
arithmetic operations is bounded independently of `d`. If
`B=max(1,bit_length(max(d)))`, its bit complexity and working storage are
`O(B)` for this fixed graph. Output consists of eight shared-coordinate
counts, seven private counts, seven half-cover coefficients, and the rank.
No payload coordinates need to be expanded. This is a theoretical encoded-width
improvement, not a measured runtime comparison or a new fitting-rank theorem.

Define the fixed set

```
Y = { y in {0,1,2}^7 : y_u+y_v >= 2 for every edge uv }.
```

An additional explicit value formula is

```
nu(d) = floor( min_(y in Y) sum_v d_v*y_v / 2 ).             (1)
minimum fitting rank = S - floor(min_(y in Y) d dot y / 2). (2)
```

There are 267 vectors in `Y`, enumerated by the verifier. Neither (1) nor the
constructor requires the predecessor's residual-state table. The classical
ingredients are LP strong duality, incidence-matrix basis enumeration and
half-integral matching/vertex-cover structure. Their application here is the
new compressed implementation and certificate, not a claim to invent them.
For classical context see Alexander Schrijver's *Combinatorial Optimization*,
sections 30.2 and 31, in the author's
[official contents](https://homepages.cwi.nl/~lex/files/book.pdf).
The structural arguments needed here follow below.

## Fractional matching structure

Let `A` be the seven-by-eight unsigned vertex-edge incidence matrix and
consider the bounded nonempty polytope `P={x>=0: Ax<=d}`. Choose any extreme
point and let `F` be its positive edge support. Restrict `A` to rows whose
capacity inequalities are tight and columns in `F`. These columns are
independent. Otherwise a nonzero null vector on `F` could be added and
subtracted with sufficiently small magnitude. Positive edges remain positive,
tight equations remain equalities and all slack inequalities remain valid,
contradicting extremality.

Consequently every connected support component has at most as many edges
as vertices. It is a tree or is unicyclic. In a tree on `n` vertices there
are `n-1` columns, so at least `n-1` vertex rows must be tight. Root at the
possibly slack vertex, or any vertex if all are tight. Eliminate leaves
toward the root. Each eliminated edge equals an integer capacity minus
previous integer edge values, so every tree edge is integral.

A unicyclic component has as many edges as vertices and therefore every
vertex row is tight. Remove its attached trees by the same leaf elimination.
An even cycle has an alternating column dependence, so the remaining cycle
must be odd. On that cycle, consecutive edge sums are integers. Solving the
odd cyclic system shows that all edge values are half-integers, and their
fractional parts are either all zero or all one half. Thus the nonintegral
edges of any extreme point are a vertex-disjoint union of odd cycles.

The only odd cycles in this theta graph are
`u-a-v-c-b-u` and `u-a-v-e-d-u`. They share `u,a,v`, so at most one can occur
in the nonintegral support of an extreme point. The other simple cycle has
length six. This statement follows by taking two of the three internally
disjoint u-v paths. A simple cycle cannot use three paths without revisiting
an endpoint.

## Rounding is exact for the objective

Choose an extreme point maximizing `sum(x)`, with value `L`. If it is integral,
it already gives an integral optimum. Otherwise exactly one odd cycle has
half-integer edge values, while every other edge is integral. Round alternately
down and up along the cycle, starting and ending with down. At every cycle
vertex the incident total remains unchanged except at the meeting point of
the two down edges, where it decreases by one. All capacity inequalities and
nonnegativity are preserved. The objective decreases by exactly one half.
Since the cycle has odd length, `L` itself is then an integer plus one half.
In both cases the rounded integer matching has value `floor(L)`. Conversely
every integer matching has value at most `floor(L)`. Hence

```
nu(d) = floor(L).                                          (3)
```

Zero widths, disconnected positive supports and `d=0` are included. No
positive-width or nondegeneracy assumption enters the rounding argument.

## A fixed cover formula and small optimality certificate

The fractional matching LP has dual

```
min sum_v d_v*z_v, with z_v>=0 and z_u+z_v>=1 on each edge.
```

Truncate every `z_v` at one. Feasibility remains valid and the objective
does not increase, since capacities are nonnegative. There is therefore an
optimum in the compact polytope with `0<=z_v<=1`. Its vertices are half-integral.
To see this, inspect the graph of active edge equalities between fractional
coordinates. An active edge to an integral coordinate would force its other
coordinate to be integral. In a bipartite fractional component, alternating
small plus/minus perturbations preserve every active equality, all box bounds
and every slack inequality, contradicting extremality. Every fractional
component must therefore contain an odd cycle, whose alternating equations
force all its coordinates to one half. All coordinates belong to `{0,1/2,1}`.

LP strong duality now gives `L=min_(y in Y) d dot y / 2` and (3) proves (1).
The constructor returns an integral matching `x`, private counts
`p_v=d_v-sum_(e incident v)x_e`, and a vector `y in Y` satisfying

```
x_e,p_v >= 0;  p_v + sum_(e incident v)x_e = d_v;
sum_e x_e = floor(d dot y / 2).                            (4)
```

These are independently checkable optimality certificates. Indeed every
integer matching `w` satisfies
`2 sum(w) <= sum_e w_e*(y_u+y_v) <= sum_v d_v*y_v`.
Thus (4) proves optimality using only integer sums, even if the constructor
were replaced by an untrusted program. The all-field fitting-rank conclusion
then uses the cited #5218 theorem. The certificate alone is a matching result.

## Enumerating a fractional optimum without width expansion

For an extreme point with `k` positive edges, column independence supplies
`k` tight rows forming a nonsingular square incidence submatrix `C`. In
particular `k<=7`. Enumerate all choices of `k` edges and `k` vertices,
for `1<=k<=7`. For each nonsingular `C`, precompute `2*C^-1`. Its entries
are integers. One direct justification is to solve each connected component
of this square restricted incidence system. A component with as many columns
as rows is a tree with one omitted vertex equation, or an odd unicyclic
component with every vertex equation retained; leaf elimination and the odd
cycle equation give denominators dividing two. An even cycle is singular.
Equivalently these are the tree/odd-cycle bases of an unsigned incidence matrix.

Evaluate that fixed linear template at the corresponding widths. Put zero
on edges outside its chosen support and reject negative or over-capacity
values. Include the all-zero point explicitly. The list contains every
extreme point and hence an optimum. The implementation compares doubled
integer objective values and then rounds the sole fractional cycle as above.
It enumerates `Y` independently and checks equality of the fractional primal
and dual objectives before accepting. Finally it checks (4).

There are fewer than 6,435 square submatrix candidates and exactly 1,583
nonsingular templates for this graph. Initialization uses only fixed small
rational matrices of order at most seven. Evaluating a template, checking its
capacities, comparing objectives and checking a cover use a fixed number of
additions, comparisons and multiplications by fixed integers. All intermediate
integers have `B+O(1)` bits. Division by two is a shift. Thus the constructor
and its optimality certificate require `O(B)` bit operations and `O(B)`
working bits, with constants depending on this seven-vertex graph.
Parsing/printing and coordinate expansion are separate interfaces. In
particular a full fitting matrix has `S^2` entries and is not claimed to be
produced in encoded-width time.

## Evidence and limitations

The verifier independently computes optimal copy matchings on all 2,187
width vectors in `{0,1,2}^7`, including every zero-width support. It compares
the new constructor's certificates on all of them. It checks 130 explicitly
expanded attaining matrices in three characteristics, giving 390 rank
calculations, and checks all 2,109 matrix entries against the fitting contract.
There are 76 half-integer fractional optima in this domain. Nine additional
fixtures use widths up to 4,099 bits without coordinate expansion. Fourteen
controls reject malformed inputs, damaged certificates and a missing basis
family. These finite checks corroborate the written all-width proof.

The source theorem and its proof remain cited premises, rather than new
results or independently revalidated claims. Physical copies, coefficient
delivery, frames, restoration, owner lifetimes, precision, fixed tapes,
compiler/supplier admission and a complete multiplication theorem are outside
scope. No new kappa or selected-frontier change is claimed. We stop at this
constructor and do not start a larger graph or physical implementation search.
