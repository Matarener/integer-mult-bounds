# Dependent queries with three projective directions keep the reader floor

## Statement and scope

Use Tekalign's PR3370 partition of the 112 selected P112 port labels into
sixteen even orthonormal groups. Consecutive ports in each group define binary
Gram-I2 planes. Each alternating half of each group defines an indicator v_c.
The literal fitting matrix is K = sum_c v_c v_c^T. There are 32 indicators.

For a scalar vector v over a coefficient field F, let cl(v) contain both
ports of each complete plane touched by its nonzero entries. The actual-reader
tariff is

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Coefficient arithmetic in F and the binary tariff arithmetic are different.
No ordered-field, characteristic, integrality or sign assumption is made.

Choose two distinct indicators a,b, whose scalar supports are disjoint, from
groups of sizes m_A,m_B. The two groups may coincide. Suppose a finite list
of queries q_i and arbitrary actual readers u_i satisfies

    aa^T + bb^T = sum_i u_i q_i^T

over F. Suppose every query belongs to span_F(a,b), and the nonzero queries
occupy at most three distinct projective directions in that two-dimensional
space. Then

    sum_i C(u_i,q_i) >= m_A + m_B.

This lower bound is sharp, attained by the original two indicator terms.
The number of queries, their scalar multipliers and all reader values are
unrestricted. In particular, readers may cancel outside supp(a) union supp(b).
The theorem includes every dependent list of at most three queries realizing
this target. It does not include an independent three-query list; the completed
PR3414 written theorem supplies that separate case.

The new step is a support-dominated binary replacement. It does not reduce
the original field's coefficients modulo two. Such reduction would not make
sense for an arbitrary field or arbitrary coefficients.

## Three projective directions can be represented in the binary plane

Write q_i = x_i a + y_i b. A zero query contributes zero to both the target
and the tariff, so discard it. Partition the remaining indices into classes
D_j according to proportional nonzero pairs (x_i,y_i). There are at most
three classes. Any realization has query rank at least two, since the target
has rank two; therefore at least two distinct directions occur.

Map the distinct directions injectively to the three nonzero binary pairs

    (1,0), (0,1), (1,1),

fixing (1,0) and (0,1) whenever the corresponding axis occurs in the old
direction set. This is always possible: fix the occurring axes first, then
assign the remaining directions to distinct unused pairs. A direction off
both axes has both coefficients nonzero, so any binary image has coordinate
support contained in that old direction. Axis images preserve the same property.
Call the image d_j and set q'_j = d_j1 a + d_j2 b over F2. Then

    cl(q'_j) subset S_j,

where S_j is the common source closure of every old query in D_j. This
inclusion is why an old nonaxis direction is allowed to become an axis.

## Construct each binary reader separately at each port

At port p the original matrix identity says

    sum_i u_i(p) (x_i,y_i) = (a(p),b(p)).

Define a direction class to be active at p when at least one of its original
readers is nonzero at p. The target vector is either zero or a coordinate
axis. Outside both supports, choose every new reader value to be zero.

For a nonzero target there must be an active direction. If there is only one,
that old direction must equal the target axis. Its binary image equals that
axis, so its new reader value can be one. If at least two distinct directions
are active, their binary images are distinct nonzero pairs and hence span
F2 squared. Choose binary coefficients on those active classes giving the
target. Set the other reader values to zero. The construction can be repeated
independently at each port, yielding binary readers u'_j such that

    aa^T + bb^T = sum_j u'_j (q'_j)^T                 over F2,
    cl(u'_j) subset union_{i in D_j} cl(u_i).

No support assumption on old readers was used. Even if several proportional
readers cancel within a class, the union of their supports is an allowed
upper bound. The construction can use that class or omit it.

## The binary replacement cannot cost more

For binary Gram matrices, deleting source rows or reader columns cannot
increase rank. Also, for a fixed source set S and reader sets T_i,

    rank Gram(S, union_i T_i) <= sum_i rank Gram(S,T_i).

The latter inequality follows by horizontally concatenating the matrices;
duplicate columns in the concatenation do not change its rank. Apply these
facts within each projective class, using the identical old source closure S_j:

    C(u'_j,q'_j)
      <= rank Gram(S_j, union_{i in D_j} cl(u_i))
      <= sum_{i in D_j} C(u_i,q_i).

Summing proves that the new binary realization costs no more than the old
F-valued realization. This is a comparison of binary support tariffs; it does
not assert that the old coefficients admit a field homomorphism to F2.

## The retained expanded-identity lower bound

This is the integral/binary argument of Philippe Van Velzen and PR3345,
also used in PR3398 and PR3414. It is included here to make the proof complete
for the new dependent-query theorem.

Expand each scalar port to its complete plane's two coordinates. For any
binary 112-by-112 scalar matrix M, replace entry M_pq by M_pq times the
2-by-2 Gram block of the planes at p and q. This expansion is linear.

The expansion of the literal K is I224. Diagonal scalar entries contribute
I2. An off-diagonal nonzero entry of K joins two different planes within
one orthonormal group, so its Gram block vanishes. The two ports of one
plane belong to different alternating halves, so their off-diagonal K
entries are zero. These exhaust the possible entries.

The expansion of a binary term u q^T factors through the Gram matrix between
cl(q) and cl(u), up to transposition. To see this, repeat the relevant source
plane's columns at each source port and scale by q's binary value; repeat
reader rows and scale by u's value. Thus the expanded term has binary rank
at most C(u,q). Rank subadditivity implies that every binary factorization of
the entire literal K has total tariff at least rank(I224) = 224.

Add every untouched literal indicator term to the binary pair replacement.
Their total tariff is 224 - m_A - m_B, since an alternating half touches every
plane of its orthonormal group, whose Gram rank is the group's size. The pair
replacement therefore costs at least m_A + m_B. The preceding tariff comparison
proves the same lower bound for the original F-valued list. The original a,b
terms attain equality, proving sharpness.

## Consequence for three queries

The target's row space is span_F(a,b). It is contained in the query row space.
Consequently a dependent list of three queries realizing the target has query
rank exactly two, and that row space equals span_F(a,b). At most three
projective directions occur, so the new theorem applies. Zero queries and
proportional repetitions are included.

Together with PR3414's independent-three-query theorem at exact head
7b698dc958695d0a788327ddf8866b10a59e4c37, this completes the sharp pair tariff
floor for all lists of at most three queries over every field. That combined
statement inherits the predecessor's independent-query proof. This package
does not independently replay or formally verify that predecessor theorem.
Disjoint replacements of these kinds cannot lower the literal total of 224.

## Why four directions require another argument

The universal binary-map method has a concrete limitation. Take the four
rational directions (1,1), (1,2), (1,3), (1,4). At twelve abstract reader sites,
ask each of the six direction pairs to deliver each of the two coordinate
axes, using only that pair. Every rational request is possible with both
reader coefficients nonzero because the two slopes differ and neither is an
axis. A support-dominated binary replacement would require every pair of
binary images to span both axes. Four pairwise distinct nonzero binary
directions do not exist. Allowing zero images cannot help.

This twelve-site example is outside the literal two-indicator P112 fixture
and has no tariff comparison. It proves only that the per-port binary-map
lemma cannot extend to arbitrary four-direction support data. It is not a
lower-cost P112 witness or an exclusion of four-query replacements. The
separate checker exhausts all 256 binary assignments, including zero images.

## Evidence and remaining obligations

The universal theorem is the written argument above. Finite replay checks
96 rational literal P112 realizations, including duplicated directions, zero
queries and globally cancelling readers. It checks both original rational
and replacement binary operators and their actual-reader tariffs. A separate
implementation tests the pointwise lemma over F2,F3,F5,F7, reconstructs every
entry of expanded I224 and checks the abstract four-direction limitation.
These computations are author evidence, not independent human or proof-kernel
acceptance.

Four or more projective directions, external query dimensions, changed
fitting matrices, shared native operations and changed readout contracts
remain open. Native acquisition, coefficient execution, restoration, frames,
hosting, stock, precision, all-size/compiler obligations, both supplier
admissions and the outer multiplication transfer are not supplied. No new
kappa or selected-frontier change follows.
