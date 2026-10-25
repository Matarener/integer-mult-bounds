<!-- SPDX-License-Identifier: Apache-2.0 -->

# Necessary structure of a twelve-row obstruction

## Statements and limits

An ordered nonzero block is a sequence of distinct matrix indices whose
every forward off-diagonal entry is nonzero. We study the following
sufficient condition for a twelve-line box witness:

    Two disjoint ordered nonzero blocks retain at least eight indices.   (T)

The main theorem is a partial reduction, not a proof of (T) over the
rationals:

> Let M be a twelve-by-twelve matrix over any field K, of rank at most
> three and with nonzero diagonal. If (T) fails, then rank(M)=3. In a
> rank-three factorization M_ij=p_i^T q_j, no projective p-direction or
> q-direction occurs more than twice, and every row and column has at
> most five zero entries.

Here a projective direction means a nonzero proportionality class.
The diagonal condition ensures that all factor vectors are nonzero.
The conclusion holds for any rank-three factorization.

These necessary conditions imply that (T) always holds over F_2. They
have not been shown contradictory over Q or R. A rational directed box
can also have a witness that does not arise from (T), so failure of (T)
is not itself a counterexample to the rational box bound.

We use the seven-row matrix lemma from PR3420 at head
e2d39da9c7109f361d6cff677cf9f8eba51f3dd6: over any field, seven rows of
rank at most three with nonzero diagonal contain an ordered triple.
Its proof is analytic, not a finite-census premise.

## Rank two partitions into two ordered blocks

Let M have rank at most two and nonzero diagonal. Write
M_ij=p_i^T q_j with vectors in K^2, padding a smaller factorization if
necessary. Partition the nonzero q-vectors into projective classes.
The zeros in row i consist of at most one complete class: the kernel
of the nonzero functional p_i^T is one projective direction. Call this
its forbidden class, if that direction occurs among the q-vectors.
It is never i's own class because M_ii is nonzero.

Choose any order of the classes. Put i in F if its forbidden class is
earlier than its own class, and in L if its forbidden class is later.
Rows with no forbidden class, called free rows, may be put in either
block. Order F by increasing class and L by decreasing class. Every
zero from a retained row points backwards. Within a class all entries
are nonzero, since q_j is a nonzero scalar multiple of q_i and M_ii is
nonzero. Thus F,L partition all indices into ordered nonzero blocks.

Either block can be empty in this construction. If an application
requires two nonempty blocks and one block alone retains at least eight,
split its order into two nonempty blocks. In particular, rank at most
two already proves (T) at twelve rows. The partition also supplies an
ordered block of size at least ceil(n/2) on any n-row rank-two matrix.

## One or two prescribed outside prefixes

Let Z be a principal set whose q-vectors lie in a two-dimensional plane H.
Each row of its principal matrix has a nonzero restriction to H, by its
nonzero diagonal, so the preceding class construction applies on H.

Suppose an outside row a has a nonzero restriction to H. Let A be its
kernel direction on H. Put the Q_Z class A first, if present, in the
class order. Assign free rows of A to L. No other row of A goes to F,
because its forbidden class is different from A and therefore later.
Thus F avoids A, and a can precede F. Together with L this retains all
of Z and a. An absent class A is treated as a formal first class.

Suppose instead that two outside rows a,b have nonzero restrictions
with distinct kernel directions A,B. Put A first and B last. Assign
free rows of A to L and free rows of B to F, assigning other free rows
arbitrarily. Then F avoids A and L avoids B. Prefix a to F and b to L.
This gives two disjoint ordered blocks retaining |Z|+2 indices. Formal
endpoint classes also cover the case where A or B is absent.

## Consequences of failure of (T)

Assume now that (T) fails. Rank at most two has already been excluded.
An ordered five-block is also impossible: its seven-row complement
contains an ordered triple by PR3420, giving five plus three. Two
disjoint ordered four-blocks are impossible by definition.

We first prove that every factor direction occurs at most twice.

### Four proportional rows

Four proportional p-rows form a fully nonzero four-block, since their
diagonals are nonzero. Any outside q-vector is either zero on all four
rows or nonzero on all four. The latter would extend their block to five.
Consequently all eight outside q-vectors lie in the common annihilator
plane. Their rank-two principal matrix partitions into two ordered blocks
retaining eight, a contradiction. This also excludes larger multiplicity.

### Three proportional rows

Suppose three proportional p-rows form C. They give a fully nonzero
three-block. Let S be the other indices whose q-vectors are nonzero
against that common p-direction, and let Z be the remaining indices.
A nonzero edge in S could follow C to give five. Therefore S is
independent: its principal matrix is diagonal with nonzero diagonal,
so |S|<=3. All q-vectors on Z lie in a plane.

If |S|<=1, then |Z|>=8, and its rank-two partition settles (T).
If |S|=2, then |Z|=7. Its rank-two principal matrix has an ordered
four-block. The three-block C followed by either member of S is a
disjoint four-block, again settling (T). Only

    |C|=3,             |S|=3,             |Z|=6

can remain.

Use the independent S triple as a rank basis. An invertible factor
coordinate change and nonzero individual row and column scalings,
which preserve rank and all zero patterns, permit the normalization

    p_s=q_s=e_s for s=1,2,3 in S,
    p_c=(1,1,1) for c in C.

Indeed, first make P_S the identity; then Q_S is diagonal, and column
scalings make it the identity. The common p-direction has three nonzero
coordinates because it is nonzero on every q_s. A diagonal coordinate
change makes that direction (1,1,1), and row and column scalings on S
restore p_s=q_s=e_s. Scaling the rows of C makes their p-vectors equal.

Every q_z is nonzero and lies in H={x_1+x_2+x_3=0}. If some s in S has
five nonzero entries into Z, those five rank-two principal indices have
an ordered triple. Prefixing s gives four; C followed by a different
member of S gives a disjoint four. Thus each s has at most four nonzero
entries into Z. Each coordinate vanishes on at least two q_z, while a
nonzero vector in H has at most one zero coordinate. Counting forces
exactly two q_z on each of the three distinct directions

    H intersect {x_1=0}, H intersect {x_2=0}, H intersect {x_3=0}.

Fix one of these proportional q-pairs U={u,v}, whose zero coordinate
is i, and let j,k be the other coordinates. Let W consist of rows
outside U with nonzero entries into U. They have nonzero entries into
both members. The set W excludes C and contains s_j,s_k.

If W had a nonzero directed edge, that edge followed by (u,v) would
give four. It uses at most two members of S, leaving an unused member
that can follow C to give a disjoint four. Hence W is independent.
If z in Z outside U belonged to W, independence from s_j,s_k would
force p_z to have only coordinate i, contradicting its nonzero entry
into q_u, whose coordinate i is zero.

Every row of Z outside U therefore has zero entries into U. Apply this
to all three pairs: M[Z,Z] becomes block diagonal with three two-by-two
blocks. Each has proportional columns and nonzero diagonal, so each
has rank one. This gives rank three, contradicting the rank-at-most-two
construction on Z. Three proportional p-rows are impossible.

Transposition reverses the order of an ordered block and preserves (T).
The same proof therefore bounds every q-direction's multiplicity by two.

## Six zero entries in a row already settle (T)

We prove the remaining zero-degree condition under the multiplicity
bound just established. If a row has at least eight zero columns, choose
eight of them. Their q-vectors lie in a plane and the rank-two partition
settles (T).

Suppose a row v has seven zero columns Z, and let H=ker(p_v). If an
outside row has nonzero restriction to H, the one-prefix construction
retains all seven indices and that row, settling (T). Otherwise the
five outside p-vectors all annihilate H, and therefore are proportional
to p_v, contradicting the multiplicity bound.

It remains to consider six zero columns Z of row v. Let Y be the other
six indices, including v, and write U=span{p_y:y in Y}. If U has
dimension three, choose p_a,p_b among these rows so that p_v,p_a,p_b
are independent. Their restrictions to H=ker(p_v) are nonzero and
nonproportional; their kernel directions on H are distinct. The two-prefix
construction retains all six members of Z and a,b, settling (T).

If U has dimension one, the six indices in Y are fully nonzero, giving
an ordered five-block, which has already been excluded. Suppose U has
dimension two. Let q_0 span its annihilator. Since p_v belongs to U,
q_0 lies in H. Remove from Y the class C of p_v, and from Z the class
D of q_0. Each class has at most two members; D can be empty.

Every cross entry from Y\C to Z\D is nonzero. To see this, a p-vector
in U not proportional to p_v restricts to a nonzero functional on H.
Its kernel there is exactly q_0, because it annihilates q_0 and that
kernel is one-dimensional. A q-vector outside D does not lie in it.

Both remaining principal sides have rank at most two: the P-vectors
on Y\C lie in U, and the Q-vectors on Z\D lie in H. Partition each
side into two ordered blocks. Append each Z-side block to the corresponding
Y-side block. The nonzero cross entries make both concatenations valid,
and their union has size

    12-|C|-|D| >= 8.

This contradiction excludes six zero entries in a row. Transposition
gives the same result for columns. Since diagonal entries are nonzero,
these zero counts are automatically off-diagonal. The obstruction theorem
is proved over arbitrary fields.

## The finite-field corollary

Over F_2 there are exactly seven projective directions in dimension three.
Twelve q-vectors with multiplicity at most two have one of two patterns:
six doubled directions and one absent direction; or five doubled directions
and two singleton directions.

Each nonzero p-direction annihilates a three-point Fano line. A line
containing three doubled q-directions gives six zero entries and is
forbidden by the obstruction theorem. In the first pattern, every allowed
p-line must pass through the absent q-point. There are only three such
lines, allowing at most six p-rows under the multiplicity bound. In the
second pattern, every allowed line must pass through at least one of the
two singleton q-points. Their two pencils contain 3+3-1=5 distinct lines,
allowing at most ten p-rows. Both contradict twelve.

Thus every twelve-by-twelve F_2 matrix of rank at most three with nonzero
diagonal satisfies (T). This conclusion is specific to its nonzero-diagonal
finite-field hypotheses.

## What transfers to the rational directed box

For binary anchors with nonempty ties, the required scalar implication is

    M_ij=0 implies A_i dot B_j=0 over F_2.                (SG)

Given two ordered blocks F,L, choose a tied coordinate c_i on every
retained line. On F use (a_i,b_i)=(A_i,e_(c_i)); on L use
(a_i,b_i)=(e_(c_i),B_i). Order F before L. Inside a block there are no
forward zero entries. Across the blocks the forward label dot is the
original A_i dot B_j, so SG enforces every required zero. Every diagonal
dot is one. Thus (T) is a sufficient condition for box at least eight,
using the retained asymmetric two-block transfer.

Canonical rational normalization supplies SG using actual valuations.
Delete product columns for which one whole factor column is zero and put

    m_j=min_i nu_2(P_ij),   n_j=min_i nu_2(Q_ij),
    gamma=min_j(m_j+n_j),
    p_ij=2^(-m_j)P_ij,      q_ij=2^(m_j-gamma)Q_ij.

Zero entries have valuation infinity. The normalized rational entries
have odd denominator, p q^T=2^(-gamma)M, and their reductions modulo two
define A_i,B_i. An actual zero gives SG. This statement concerns actual
rational valuations, not a finite sentinel in an archived implementation.

There is also a completed rational subcase. If any tied set has odd size,
choose that row r. The other eleven rows have a four-block F and a disjoint
three-block L by PR3435 at head
0833fff0bdc9acdd3b174c7677ab1b46873b22d3. Use the preceding asymmetric
labels on F,L, and insert r between them with (a_r,b_r)=(A_r,B_r).
Its diagonal dot is one because its tie is odd. Dots from F to r, from r
to L, and from F to L are all original anchor dots, so SG supplies every
required zero. This retains eight lines. It uses the original global
anchors; no canonical normalization on a subset is asserted.

With three total coordinates, the only remaining admitted rational case
has every tie of size two. Its normalized matrix modulo two has zero
diagonal. The F_2 corollary above therefore cannot be applied to that
reduction. The rational twelve-line floor remains open here. In
particular, box less than eight would force both failure of (T) and all
the obstruction conditions, but matrices satisfying those necessary
conditions have not been proved to exist or to have small box.

## Attribution

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
New work is Apache-2.0. The directed box definition, canonical normalization,
and SG implication retain the Aaron Wang/navinor predecessor attribution.
The seven-row matrix lemma is retained from PR3420 at the head specified
above; the eleven-row four-plus-three conclusion is retained from PR3435.
The asymmetric two-block transfer is retained from PR3409 and PR3420.
