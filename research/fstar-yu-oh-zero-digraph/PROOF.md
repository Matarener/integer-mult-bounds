# The Yu–Oh rays as a rational zero-digraph fixture

The thirteen rays below are the established Yu–Oh configuration, not a new
graph construction. This note admits them into the repository's rational
three-total model and proves three different values for the same instance:

\[
\operatorname{rank}M=3,\qquad
\chi(Z)=4,\qquad
\operatorname{MP}(M)=12<\operatorname{box}(M)=13.
\]

Here `MP` is the matched-unit-pivot value, and `box` uses the complete directed
anchor-label definition. The distinction is essential: this coloring
obstruction does not obstruct a full thirteen-row box witness.

## 1. Exact rational input and anchors

Take the rows of both factors `P = Q` to be the following integer vectors:

| Names | Vectors |
|---|---|
| `z1,z2,z3` | `(1,0,0),(0,1,0),(0,0,1)` |
| `y1+,y1−` | `(0,1,1),(0,1,−1)` |
| `y2+,y2−` | `(1,0,1),(1,0,−1)` |
| `y3+,y3−` | `(1,1,0),(1,−1,0)` |
| `h++,h+−,h−+,h−−` | `(1,1,1),(1,1,−1),(1,−1,1),(1,−1,−1)` |

Set `M = P Qᵀ` over the rationals. Its diagonal entries are respectively
`1,2,3` on axes, faces and bodies; they are nonzero. Its axis principal
submatrix is `I3`, so its rank is exactly three.

Every factor column contains a unit. Therefore the actual canonical
2-adic column minima are all zero, `γ = 0`, and both anchor supports `A_i,B_i`
are exactly the nonzero coordinates of row `i`. This uses the mathematical
valuation `ν₂(0)=∞`, with no finite sentinel approximation. No zero-product
column needs to be deleted. The common-anchor cardinalities are

\[
\tau_i=|A_i\cap B_i|=
\begin{cases}1&\text{on the three axes},\\
2&\text{on the six faces},\\
3&\text{on the four bodies}.
\end{cases}
\]

In particular every tied set is nonempty. Reducing the exact integer
identity `M_ij=0` modulo two gives the source zero-arc implication
`A_i·B_j=0` over `F2`.

The zero digraph has both arcs on each orthogonal pair, because `M` is
symmetric. Such a digraph is acyclic on a vertex subset precisely when that
subset contains no orthogonal pair: any pair already gives a directed
two-cycle. Thus its dichromatic number equals the ordinary chromatic number
of the orthogonality graph. The latter has exactly 24 edges: three among
the axes, six axis–face edges, three within face pairs, and twelve
face–body edges. Faces from different pairs are not orthogonal, and no
body is orthogonal to an axis or another body.

## 2. An eight-case proof that `χ(Z) = 4`

In any proper three-coloring the mutually adjacent axes have different
colors; rename them so `z1,z2,z3` have colors `0,1,2`. The two faces `yi±`
are adjacent to each other and to `zi`. Hence they receive the two colors
other than the color of `zi`, in either order. These are the only eight
remaining choices before coloring the bodies.

Let bit `b_i` select the color of `yi+` from the increasing list of the
two available colors, and give `yi−` the other color. The body neighbors
among the faces are exactly

\[
\begin{array}{c|c}
h_{++}&y1^-,y2^-,y3^-\\
h_{+-}&y1^+,y2^+,y3^-\\
h_{-+}&y1^+,y2^-,y3^+\\
h_{--}&y1^-,y2^+,y3^+
\end{array}
\]

The following table identifies a body whose neighbors receive all three
colors; substitution in the preceding four rows checks every case.

| `(b1,b2,b3)` | Body blocked from all three colors |
|---|---|
| `000` | `h−+` |
| `001` | `h−−` |
| `010` | `h++` |
| `011` | `h+−` |
| `100` | `h+−` |
| `101` | `h++` |
| `110` | `h−−` |
| `111` | `h−+` |

Consequently three colors do not suffice. Conversely, use any of the eight
colorings on the axes and faces and give all four bodies a fourth color.
There are no body–body edges, so this is a proper four-coloring. Therefore
`χ(Z)=4`, including its directed, dichromatic meaning.

## 3. The matched-unit-pivot value is exactly twelve

A matched canonical unit pivot chooses a coordinate `c_i ∈ A_i∩B_i` and
uses `a_i=b_i=e_(c_i)` on each retained line. Since every zero edge here is
bidirected, a retained pivot class must be independent, regardless of its
order. If all thirteen rows could be retained, the three coordinates would
therefore give a proper three-coloring, contradicting Section 2. Thus
`MP(M)≤12`.

For the reverse inequality, take orientation `000`, omit `h−+`, and use
the following colors (coordinate number is color plus one):

\[
\begin{array}{c|c}
(z1,z2,z3)&(0,1,2)\\
(y1^+,y1^-,y2^+,y2^-,y3^+,y3^-)&(1,2,0,2,0,1)\\
(h_{++},h_{+-},h_{--})&(0,2,1).
\end{array}
\]

Each color is in its row's tied support, and each color class is
independent. This supplies twelve valid unit labels, proving `MP(M)=12`.
An exhaustive pivot census can independently check this value, but is not
needed for the upper or lower bound.

## 4. All thirteen rows satisfy the full directed box constraints

Recall the constraints: for a retained ordered subset choose binary labels
`a_i ⊆ A_i`, `b_i ⊆ B_i` with `a_i·b_i=1`; whenever `i` precedes `j` and
`M_ij=0`, require `a_i·b_j=0`. Only this forward ordered constraint is
imposed, not its reverse with the labels exchanged.

Order all rows in three consecutive blocks:

\[
F=(y1^+,y2^+,y3^+),\qquad
O=(z1,z2,z3,h_{++},h_{+-},h_{-+},h_{--}),\qquad
L=(y1^-,y2^-,y3^-).
\]

For a face in either outer block choose any coordinate `c_i` in its
two-element support, and assign

\[
(a_i,b_i)=
\begin{cases}
(A_i,e_{c_i})&i\in F,\\
(A_i,B_i)&i\in O,\\
(e_{c_i},B_i)&i\in L.
\end{cases}
\]

These labels lie in the anchors. The outer-block diagonal products are
one, and the middle-block products are one because every middle row has
odd `τ`. Within either outer block there are no actual zero arcs: two
different face planes have dot product `±1`. Within the middle block,
and from any earlier block to any later block, the two labels involved
in a forward constraint are the full anchors `A_i,B_j`. Every such zero
arc is therefore satisfied by the modulo-two implication in Section 1.
This verifies every directed constraint and keeps all thirteen rows.
As no box can retain more rows than the input has, `box(M)=13`.

## Attribution and scope

The ray configuration is from Sixia Yu and C. H. Oh,
[*State-independent proof of Kochen–Specker theorem with 13 rays*,
arXiv:1109.4396v1](https://arxiv.org/pdf/1109.4396v1), visible equation (1)
on PDF page 2; its journal version is
[*Physical Review Letters* 108, 030402 (2012)](https://doi.org/10.1103/PhysRevLett.108.030402).
Their ray `h1=(-1,1,1)` is represented here by its negative `(1,-1,-1)`;
this does not change any orthogonality relation. The other representatives
are the same up to naming and order. No quantum-contextuality claim is
needed for the arguments above.

The repository question and distinction between dichromatic number and
`D(t)`-compatible matched pivots come from Aaron Wang (navinor),
[PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890),
head `08a44355403604c346f8d907811edce992382cc4`,
`research/fstar-chi4-zero-digraph-seed73765f29/README.md`. This package
supplies a concrete admitted fixture for its open `χ(Z)≥4` question and
separates its pivot value from the complete directed anchor box. It claims
neither a smallest fixture, a new graph, a general coloring bound, nor a
general F-star theorem or counterexample.

Copyright 2026 Sagar Thakrar. Written with substantial OpenAI Codex
assistance. Licensed under the Apache License, Version 2.0.
