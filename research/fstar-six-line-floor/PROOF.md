<!-- SPDX-License-Identifier: Apache-2.0 -->

# Six rational three-total lines have a four-line box witness

This is a self-contained analytic proof for the canonical anchor model of the
[retained PR 2914 engine](inputs/pr2914-engine.py). It uses the engine's directed, ordered definition of a
box witness, not a stronger block-diagonal or unordered condition. The finite
searches used during discovery are not premises of the proof.

## Statement and canonical normalization

Let `P,Q` be rational matrices with six rows and three columns, let
`M=P Q^T`, and suppose `M_ii != 0` for every line `i`. For a rational number,
write `nu` for its 2-adic valuation, with `nu(0)=infinity`. Delete any product
column for which one whole factor column is zero; this does not change `M`.
Such columns may be restored as identically zero coordinates, so the coordinate
universe remains a subset of `{1,2,3}`. For each remaining column put

```
m_j = min_i nu(P_ij),       n_j = min_i nu(Q_ij),
gamma = min_j (m_j+n_j),
p_ij = 2^(-m_j) P_ij,       q_ij = 2^(m_j-gamma) Q_ij.
```

All entries of `p,q` lie in the ring of rational numbers with odd denominator,
and `p q^T = 2^(-gamma) M`. Let `A_i,B_i` be the supports of their reductions
modulo two. Equivalently, these are the canonical anchors
`[nu(P_ij)=m_j]` and `[nu(Q_ij)=gamma-m_j]`. Assume the tied set
`T_i=A_i intersect B_i` is nonempty for every line, and write `tau_i=|T_i|`.

A box witness consists of a kept subset, an order on it, and binary labels
`a_i subset A_i`, `b_i subset B_i` satisfying `a_i dot b_i=1`. Its only
off-diagonal constraints are

```
i before j and M_ij=0  implies  a_i dot b_j=0.
```

Then there is a witness keeping at least four lines. Thus `box(M)>=4` under
these canonical hypotheses. The proof is valid for arbitrary rational entries,
including zero and negative entries. This algebraic normalization uses actual
valuations; it makes no claim that the predecessor's finite integer sentinel is
an implementation for unbounded rational input.

Three elementary consequences will be used:

1. **SG.** If `M_ij=0`, then `A_i dot B_j=0` over `F_2`, by reducing
   `p_i dot q_j=0` modulo two.
2. **Independence lifts.** Two linearly independent binary anchor rows imply
   two linearly independent rational factor rows. A nonzero binary minor is an
   odd rational minor and is therefore nonzero.
3. **Parallel primitive rows have equal anchors.** Every row of both `p` and
   `q` has a unit entry because `T_i` is nonempty. If two such rational rows
   are proportional, the proportionality scalar has valuation zero. Its
   reduction is the sole nonzero element of `F_2`, so the two anchor rows are
   equal. In particular, if two lines have proportional `p` rows and also
   proportional `q` rows, their tied sets coincide.

## Graph and ordering tools

Let `G` be the simple undirected graph on the six lines in which `{i,j}` is an
edge precisely when at least one of `M_ij,M_ji` is nonzero. An independent set
of four vertices would give a diagonal four-by-four principal submatrix with
nonzero diagonal. Since `rank(M)<=3`, there is no such independent set.

Choosing a color `c in T_i` means using unit labels `a_i=b_i=e_c`. Different
colors are orthogonal in both directions. A same-color pair is admissible
whenever it is an edge of `G`: order it in a direction whose matrix entry is
nonzero. Consequently each of the following gives a four-line witness:

* two disjoint edges assigned two distinct common colors (**2+2**);
* one edge assigned a common color, and two other vertices assigned the other
  two distinct colors (**2+1+1**).

For 2+2, order the vertices within each pair in an allowed direction and
concatenate the pairs. Cross-pair dots are zero. The same reasoning handles
2+1+1. Thus there is no hidden assumption about orienting all edges of `G`.

A simple graph whose edges pairwise intersect is a star, a triangle with
isolated vertices, or an empty graph. Indeed, if two edges `uv,uw` exist,
every edge not incident to `u` must be `vw`; any edge meeting all three edges
of that triangle lies within the triangle. A pairwise-intersecting graph on
six vertices therefore has an independent set of at least four.

An odd line, meaning `tau_i` odd, can use its full anchors `a_i=A_i,b_i=B_i`.
Any set of odd lines is a witness in any order: its diagonals have odd dot
product and SG supplies every required forward zero. Four odd lines settle
the theorem immediately.

We may therefore assume at most three odd lines. The only even possibility is
`tau_i=2`. A line with `tau_i=3` may be restricted to any chosen two-element
tied list for a unit-label argument. Let a **singleton** mean a line with
`tau_i=1`; every other line will receive a two-element list contained in its
tied set. There are only zero, one, two, or three singletons to consider.

## No singleton

Choose a two-element list `L_i subset T_i` for every line. Suppose no unit
four-witness exists. Fix an edge `uv` and a shared color `c`. Write `d,e` for
the other two colors. No two of the other four vertices can respectively
supply `d,e`, since that would be a 2+1+1 witness. Every two-element list meets
`{d,e}`. If one meets both, it can be paired with any other list to supply
both. Otherwise two different singleton intersections also supply both.
Therefore all four outside lists equal `{c,d}`, or all equal `{c,e}`.

If `L_u=L_v`, apply this observation to both common colors: all six lists are
equal. If `L_u!=L_v`, their intersection is a single color, and the outside
four equal one of the endpoint lists. Thus five lists equal a pair `R`, and
one equals a different pair `S`.

In the five-plus-one case, an edge among the five `R` vertices could use the
color in `R\S`, a third `R` vertex the color in `R intersect S`, and the
exceptional vertex the color in `S\R`. Hence the five `R` vertices must be
independent, a contradiction. In the uniform case, any two disjoint edges
could use the two colors of `R`. The whole graph has pairwise-intersecting
edges and therefore an independent four, again a contradiction. An edge
exists because an edgeless graph itself has an independent four.

## One singleton

Let its tied color be `c`, and assign two-element lists to the other five
vertices. Their induced graph has an edge, or it has an independent four.
For an ordinary edge with shared color `d!=c`, the remaining three ordinary
lists must all be `{c,d}`: any of them containing the third color would form
a 2+1+1 witness with that edge and the singleton. If the shared color is
`c`, the remaining three lists must be a common pair containing `c`, by the
same two-color selection argument as above.

These conclusions imply that the five ordinary lists are either uniform in a
pair `R`, or consist of four copies of `R` and one different pair, with
`c in R` in both alternatives. To see this without a case omission, identical endpoint lists can be
tested using both common colors; a pair not containing `c` gives inconsistent
requirements on the outside lists, while a pair containing `c` makes them
equal to that pair. Distinct endpoint lists have one common color. If it is
`c`, the outside pair equals one of the endpoint pairs. If it is not `c`, the
outside pair `{c,d}` again equals one endpoint pair.

In the four-plus-one case any edge among the four `R` vertices uses the
color in `R\{c}`, together with the singleton color `c` and the exceptional
vertex's color outside `R`, to give 2+1+1. Those four vertices are therefore
independent. In the uniform case, any two disjoint edges of the full graph
can be given different colors: at most one edge meets the singleton, so give
that edge color `c` and the ordinary edge the other color. The graph has
pairwise-intersecting edges and hence an independent four. Both alternatives
contradict the rank bound.

## Two singletons with distinct colors

Let their tied colors be `c,d`, and let `e` be the third color. Put
`R={c,d}` and count how many of the four ordinary lists contain `e`.

If at least two do, every ordinary edge gives a four-witness. An edge sharing
`e` uses the two singleton colors. Otherwise choose its shared color, say
`c`: if an outside ordinary vertex supplies `e`, use that vertex and the
`d` singleton. If neither outside vertex supplies `e`, both endpoints must
supply it and the edge shares `e` after all. Thus the four ordinary vertices
are independent.

If exactly one ordinary list contains `e`, the other three are `R`. There
can be no edge between two of those three, using one singleton and the
exceptional color to complete 2+1+1. There can also be no edge from either
singleton to those three: use its tied color on that pair, the other singleton
color, and the exceptional color. The three `R` vertices and either singleton
are independent.

It remains that all four ordinary lists are `R`. Their induced graph has an
edge. No two of its edges are disjoint, since they could use colors `c,d`.
Every edge from a singleton to an ordinary vertex must meet every ordinary
edge: otherwise use the singleton color on its edge and the other color on
the disjoint ordinary edge. Thus the ordinary graph is a star or a triangle.

If it is a star with at least two edges, every singleton-to-ordinary edge
must meet all star edges and can only end at the center. The other three
ordinary vertices and either singleton are independent. If it is a single
edge, let `x,y` be the two remaining ordinary vertices. If it is a triangle,
let `x` be the fourth ordinary vertex and `y` any triangle vertex; neither
singleton can have any ordinary neighbor in this case. In both remaining
cases, `x,y` are mutually zero in both matrix directions and each is mutually
zero with both singletons.

The nonzero diagonal two-by-two submatrix on `x,y` makes `p_x,p_y` independent
and `q_x,q_y` independent. Both singleton `p` rows lie in the one-dimensional
annihilator of the span of `q_x,q_y` in the three-dimensional factor space.
They are nonzero and hence proportional. The same argument makes their `q`
rows proportional. The primitive-row consequence of canonical normalization
then makes both anchors identical, contradicting the distinct tied colors.

## Two singletons with the same color

Let their tied color be `c`; call the other colors `d,e`, and write
`R={c,d}`, `S={c,e}`, `T={d,e}`. Suppose there is no unit four-witness. The
ordinary graph has an edge, since there are four ordinary vertices.

An `R-R` edge forces all four ordinary lists to be `R`: color that edge by
`d`, use a singleton color `c`, and any exceptional list supplies `e`.
An `S-S` edge similarly forces uniform `S`. A `T-T` edge is impossible:
either remaining ordinary list has at least one of `d,e`; choose the other
color on the pair and add that list and a singleton. An `R-T` edge, colored
`d`, forces both other lists to be `R`, and `S-T` is symmetric. Finally an
`R-S` edge, colored `c`, forces the two remaining lists to be a common pair
containing `c`; otherwise those two vertices supply `d,e`. Therefore the
ordinary multiset is uniform in `R` or `S`, or consists of three copies of
one such pair and one different pair. Rename `d,e` to use `R` for the
majority pair.

In the three-plus-one case, the three `R` vertices have no mutual edges:
color such an edge by `d` and use a singleton and the exceptional color `e`.
Neither singleton has an edge to an `R` vertex either: use color `c` on that
pair, a different `R` vertex with color `d`, and the exception with color
`e`. Thus the three `R` vertices and either singleton are independent.

In the uniform case every vertex can use color `c`, and every ordinary
vertex can also use `d`. Every ordinary edge must meet **every edge of the
full graph**, since disjoint edges could use `d` on the ordinary edge and
`c` on the other. The ordinary graph has pairwise-intersecting edges. If it
is a single edge, its two outside ordinary vertices and the two singletons
are independent. If it is a star with at least two edges, its three
noncentral ordinary vertices and either singleton are independent. If it is
a triangle, the remaining ordinary vertex, any triangle vertex, and both
singletons are independent: no full edge involving a singleton can meet
all three triangle edges. Every alternative contradicts rank at most three.

## Three singletons

There are no `tau=3` lines now, since otherwise four odd lines already form
a witness. The remaining three lines have `tau=2`.

We first record an insertion test. Use the full anchors on the three odd
lines, and unit labels `e_c` on an even line. An odd line `o` with
`M_oe=0` and `c in A_o` requires the even line to precede it; one with
`M_eo=0` and `c in B_o` requires the odd line to precede the even line.
These ordering requirements are compatible unless the same odd line
requires both. If compatible, put all lines requiring precedence first,
then the even line, then the remaining lines; SG handles every odd-to-odd
constraint. Thus insertion fails only if an odd line has both reciprocal
zeros with the even line and its tied singleton is `c`.

Write `U={1,2,3}`. For a two-element subset `r`, the only even anchor types
with tied set `r` are

```
D_r=(r,r),       R_r=(r,U),       L_r=(U,r).
```

For a tied color `c in r`, a singleton odd line that is reciprocally zero
to `D_r` would have both anchors containing both elements of `r`, by SG,
contradicting its singleton tie. For `R_r`, let `k` be the coordinate outside
`r`. The unique possible blocking odd type is `({c,k},r)`. Indeed SG says
its first anchor has even cardinality and its second anchor meets `r` evenly;
both contain `c`, and their intersection must be exactly `{c}`. These facts
force the displayed type. For `L_r` the blocker is its transpose
`(r,{c,k})`.

If no four-witness exists, both tied colors of each even line must be blocked.
Consequently there are no `D_r` lines. Let `r,s,t` be the three two-element
subsets of `U`. An `R_r` line requires the two distinct odd types
`(s,r),(t,r)`; an `L_r` line requires `(r,s),(r,t)`.

Two distinct `R` types require four different blockers, as do two distinct
`L` types. Types `R_r,L_r` also have disjoint blocker pairs. The only way two
different even types can share the three available odd lines is `R_r,L_s`
with `r!=s`; their common blocker is `(s,r)`. Hence either all three even
lines have one type, or there are exactly two types `R_r,L_s` with
`r!=s`, of multiplicities two and one.

Suppose first that all three are `R_r`. If one required blocker type is
duplicated among the three odd lines, write its two occurrences as `O_1,O_2`
of type `(s,r)`, and the unique other blocker as `O_3` of type `(t,r)`.
Let `c` be the coordinate in `s intersect r` and `d` the other coordinate
of `r`. SG makes both entries between `O_1,O_2` nonzero, since their common
anchor type has odd diagonal dot product. An edge between any two even
lines, colored `d`, together with the odd pair colored `c`, is a 2+2
witness. If no such even edge exists, the three even lines are mutually
zero in both directions. Each must be reciprocally zero to the unique
`O_3`, since only that odd line can block its color `d`. Those four lines
then give a diagonal rank-four principal minor, a contradiction. This
argument does not assume that different even lines choose the same
occurrence of the duplicated blocker type.

Otherwise the required types `(s,r)` and `(t,r)` each occur exactly once.
Their first anchors `s,t` are independent over `F_2`, so their rational `p`
rows are independent. Every even line must be reciprocally zero to both of
these specific odd lines. Its `q` row therefore annihilates their common
two-dimensional span, so all three even `q` rows are proportional in a
one-dimensional space. Since their diagonal entries are nonzero, every
entry between these even lines is nonzero. Select the blocker `(s,r)`, let
`c` be the coordinate in `s intersect r`, and let `d` be the coordinate in
`r\s`. Use its full anchors on the blocker and unit labels `e_d` on all
three even lines. Put the blocker first. Its forward dot to any even line
is zero because `d notin s`, and all forward entries among the even lines
are nonzero. This is a four-witness. The case of three `L_r` follows by
swapping the already normalized factors `p,q`, swapping the anchors, and
reversing the witness order. SG, primitive rows, and rational independence
are symmetric under this swap; no new canonical normalization is needed.

Finally suppose there are two `R_r` lines and one `L_s`, with `r!=s`.
Their blocker union consists of three distinct types, so each type has
exactly one occurrence among the three odd lines. The same annihilator
argument therefore makes every cross-entry between the two
`R_r` lines nonzero. Give that pair the color in `r\s`, give the `L_s`
line the color in `s\r`, and give their shared odd blocker `(s,r)` the
color in `r intersect s`. This is a 2+1+1 witness. Multiplicities one and
two follow by the same factor swap and order reversal.

All cases are exhausted, proving the stated four-line lower bound.

## Scope

The conclusion concerns the ordered anchor-box quantity of the three-total
rational factorization model. It uses canonical factor normalization in the
two distinct-singleton and three-singleton cases; an arbitrary collection of
binary anchor pairs satisfying SG alone is not substituted for that model.
It does not assert a new multiplication exponent, a selected-frontier change,
or a controller/physical-cost theorem. Any larger instance with canonical
anchors and six selected lines satisfying these same primitive-row and SG
properties inherits the four-line witness by restriction. This last sentence
does not renormalize those six lines independently.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance. New work is
licensed under Apache-2.0; predecessor definitions and source attribution are
retained in [README.md](README.md#attribution).
