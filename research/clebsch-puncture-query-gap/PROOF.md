# A sharp induced-subset threshold for the fixed Clebsch query matrix

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and claim

Work over F2. Vertices are the four-bit integers 0,...,15. Distinct vertices
x,y are adjacent when x XOR y belongs to {1,2,4,8,15}. For a vertex subset S,
let B_S be the principal restriction of I+A, where A is this graph's adjacency
matrix. Thus B_S has diagonal one and zero at every forbidden ordered pair.
The minimum intermediate binary dimension among linear factorizations B_S=DE
equals rank(B_S). Allowed edge entries may vanish in the general fitting
model, but this package fixes all of them to one.

The complete finite certificate proves the following statement.

- A strict improvement of rank(B_S) over integral edge/private-coordinate
  sharing occurs exactly when |S| is 13, 14, 15 or 16.
- For sizes 13 and 14 the rank is six and the sharing optimum is seven.
  For sizes 15 and 16 the rank is six and the sharing optimum is eight.
- Therefore 13 is the smallest support size in this fixed-matrix induced
  family. There are 560 attaining subsets of size 13, all such subsets.

The written argument below also proves rank(B_S)=6 whenever |S|>=11, without
using the induced-subset census. Neither assertion minimizes over all fitting
matrices on a given graph. In particular, the six-coordinate construction does
not exclude an unrestricted five-coordinate construction.

## Why this is a triangle-free extension of the cycle interface

The generating differences have weights one or four. The XOR of two distinct
generators has weight two or three, so it is not a generator. Hence the graph
has no triangles, and neither does an induced subgraph. Integral coordinate
sharing therefore permits only an edge or one private vertex per coordinate.

For unit payload at every vertex, a collection of shared coordinates is exactly
a matching. If nu(S) is the largest matching size of the induced graph, its
optimal coordinate bill is

    c(S) = |S| - nu(S).

A matched edge saves one coordinate compared with two private coordinates.
Conversely, no vertex can use two distinct shared coordinates with unit
payload. This proves the bill without restricting a general fitting matrix
to symmetric blocks or to rank-one edge pieces.

JoyboyBrian's #5023 proves that edge/private-coordinate sharing attains the
general fitting optimum on every unequal odd cycle, over every field. This
package takes its explicitly open overlapping-cycle question. The full
16-vertex binary Clebsch code is classical and is credited below. The new
finite step determines the exact induced-subset threshold for this fixed code.

## A quadratic factorization and deletion robustness

For x in F2^4 define Q(x)=sum_(i<j) x_i x_j. For a vector of Hamming weight w,
Q(x)=binomial(w,2) mod 2. Thus

    (I+A)_(x,y) = 1 + Q(x+y).

Let u(x)=(1,x_1,x_2,x_3,x_4,Q(x)). With rows u(x), form the 16-by-6 matrix U.
Let K have entries K_00=K_05=K_50=1, K_ij=1 for distinct i,j in {1,2,3,4},
and all other entries zero. Expanding the quadratic expression gives

    I+A = U K U^T.

The {0,5} block of K is [[1,1],[1,0]], of determinant one. Its remaining
block is J_4+I_4, whose square is I_4 in characteristic two. Hence K is
invertible.

Every nonzero linear combination of U's columns has at least six nonzero
evaluations. Here is a direct proof. A nonconstant affine linear function has
weight eight; the nonzero constant has weight sixteen. The polar form of Q
has matrix J_4+I_4, so each linear functional ell has a unique representation
ell(x)=Q(x+a)+Q(x)+Q(a). Consequently Q(x)+ell(x)+c is a translate of Q plus
a constant. Q has weight ten, since binomial(w,2) is odd at weights two and
three, which occur 6+4 times. Its complement has weight six. No nonzero
combination is the zero function. This also proves U has column rank six.

Removing at most five vertices cannot annihilate a nonzero column combination
of U. Therefore U_S still has column rank six whenever |S|>=11. The map
U_S^T is surjective, K is invertible, and U_S is injective, so

    rank(U_S K U_S^T)=6.

This proves the claimed deletion robustness. The same argument gives the
row-code weight distribution 1+16z^6+30z^8+16z^10+z^16, which the verifier
also enumerates directly over its 64 coefficient choices. These elementary
quadratic-code facts and the known full code are not claimed as discoveries.

## Exhaustive finite threshold certificate

The verifier visits every integer mask from zero through 65535. This is a
bijection with all vertex subsets, including the empty subset. It computes
rank(B_S) twice, by pivot elimination and by enumerating the whole row span.
The latter never has more than 64 elements.

The matching recurrence uses the least vertex v of each nonempty subset.
A matching either leaves v unmatched, or pairs it with one of its present
neighbors w. Thus

    nu(S)=max(nu(S-v), max_(w adjacent to v in S) 1+nu(S-v-w)).

Both smaller subsets have smaller integer masks. Starting with nu(empty)=0,
this recurrence constructs and prices a matching by induction. A second
method certifies its optimality through odd-component upper bounds. For
every T subset S, at least odd(G[S\T])-|T| vertices must remain unmatched:
each odd component needs an unmatched vertex or an edge to a distinct vertex
of T. Thus

    2 nu(S) <= |S|+|T|-odd(G[S\T]).

The checker independently computes odd-component counts for every induced
graph. A subset maximum transform computes

    score(S)=max_(R subset S) (odd(G[R])+|R|).

It verifies equality between the constructed matching and the best such
upper bound for every S. Only the elementary upper-bound argument is needed;
the converse part of the Tutte-Berge theorem is not assumed by the check.

The complete strict-saving census is

    (support size, saving, number of subsets)
    (13, 1, 560), (14, 1, 120), (15, 2, 16), (16, 2, 1).

Every other subset has c(S)<=rank(B_S). This last assertion concerns the
fixed full-parity matrix, not the minimum rank among all permitted fitting
matrices. The receipt contains the full joint rank/bill histogram and a digest
over all ordered per-subset triples, rather than only the positive outcomes.

## Literal six-coordinate witness

Take S={0,...,12}. The generated receipt selects six independent rows of B_S
as query masks. It gives a six-bit decoder mask for each of the thirteen
rows. XORing those selected queries reproduces the entire required row,
including every forbidden zero and diagonal one. The verifier checks every
matrix entry and all 8192 binary inputs. With each vertex's neighbor inputs
available, its decoded parity plus the neighbor parity recovers its own bit.
This interpretation is only a linear-query identity; neighbor access has no
physical cost assigned here.

The matching certificate gives nu(S)=6, so every integral sharing solution
needs 13-6=7 coordinates. Six queries suffice. Tensoring this explicit binary
factorization with I_d gives 6d coordinates for uniform width d, while an
edge/private-coordinate construction needs at least ceil(13d/2). This is a
consequence of the fixed construction, not an asserted exact block optimum.

The five vertices {0,5,6,11,12} are independent. Every fitting matrix therefore
contains their identity principal submatrix and has rank at least five. This
justifies the open unrestricted alternatives five and six for this witness.

## Attribution and limits

Credit JoyboyBrian #5023 for the query contract and open question; Tekalign
#3362, Sagar Thakrar #2484, ywz65 #2471, Nick Petalas #4909, Cinna Davis,
Adam Gall, ctoth, Philippe Van Velzen and the retained P112/native lineage.
Credit the classical Clebsch full-parity storage construction, documented in
Alexander Barg and Gilles Zemor, *High-rate storage codes on triangle-free
graphs*, Section 2, https://arxiv.org/abs/2110.02378. That known rank-six full
code and its separation from clique sharing are not new results here. No
literature-priority claim is made for the puncturing observation.

This is a finite certificate plus an informal scoped proof. Independent human
and formal proof-kernel review are unclaimed. General fitting optimality,
nonbinary fields, nonlinear queries, actual recursive callers, native calls,
data access, coefficient preparation, dirty restoration, owned lifetimes,
frames, stock, precision, tape movement and the complete outer bill are not
supplied. No new kappa or selected-frontier change follows.
