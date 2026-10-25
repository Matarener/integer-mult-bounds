# Common30 rank-seven span and one literal C5 caller

Fix the full 120 doubled E8 root lines R, oriented by first nonzero coordinate,
the frame F={2e_0 +/- 2e_1,...,2e_6 +/- 2e_7}, and P=R\F. The original table
orders P lexicographically. Labels are ell(r)=(1,c(r) mod2) in F2^9 for the
pinned integral simple coordinates. Binary support weight is the rank of
these labels, rather than the number of support sites.

For a characteristic-zero field K let C={c_h:h in K^8}, c_h(r)=r dot h on P,
and write Off(h) for its nonzero support.

**Theorem.** Under ONE fixed S subset P of size at most30, the normals h with
rank_F2 ell(Off(h)\S)<=7 span a K-space of dimension at most **three**.
An explicit independent triple at a common cut of size30 attains three.
Moreover, for |S|<=29 there are at most **two projective normal directions**.
These are universal common-cut statements, allowing arbitrary S and arbitrary
characteristic-zero coefficient fields.

**Literal caller.** The eleven collectively independent pieces with binary
weights 2,2,2,2,2,6,7,7,7,7,7 cannot have code-intersection dimension at least5.
This is the named historical TWOSIDE (b,t)=(5,6) profile, not the whole C5
problem, a decoder theorem, supplier admission or a selected-bound change.

## 1. Reduction to all120 root normals, including the frame

The table and simple coordinates are authenticated against canonical main.
The model checks the 56 two-coordinate and64 all-odd root-line patterns,
exact coordinate equations, signs, original112 labels, and the live Gram
matrix112I. Thus evaluation is injective over every characteristic-zero K.

The reversed-pivot RREF enumeration covers every two-dimensional annihilator
of a seven-space in F2^9 exactly once. All43,435 seven-spaces have full-root
trace at most36. A qualifying direction consequently satisfies

    |Off(h)| <= 30+36 = 66 < 70.

Here are the full-root chamber and field arguments, adapted with credit from
PR3951/3960. The eight simple reflections permute the240 signed roots; they
therefore generate a finite group, since their action on a spanning set is
faithful. Solve rationally for rho dot alpha_i=1. For a real normal v maximize
rho dot g(v) over the finite group. Any negative simple pairing would make a
simple reflection increase the functional. The maximizing normal is in the
closed chamber. Every positive root has nonnegative simple coordinates, so
its pairing vanishes exactly when its support is in the zero simple nodes.
The zero roots form the corresponding simple face. No Weyl move is assumed
to preserve the removed frame or the binary labels.

The checked faces on at most six nodes have at most36 root lines. The
seven-node face counts are42,28,22,14,16,23,37,63; the last has a root normal.
For a qualifying h in K^8, let Z be the rational span of its perpendicular
live roots. There are at least112-66=46 such roots. If rank_Q Z<=6, a generic
real normal to Z avoids every root hyperplane not forced by Z, so its zero
roots span Z. Its chamber face has rank at most6, contradicting46>36.
Therefore rank_Q Z=7: rank8 would force h=0 over K by a nonzero rational minor.
Rational elimination preserves rank under extension to any characteristic-zero
K, so h is a K-multiple of a rational generator of the one-dimensional kernel.
That real generator has at least46 perpendicular roots. Only the63-line
seven-node face can occur because46>42. Reflection transport then identifies
its normal with one of the120 root lines. This argument requires no embedding
K into R or C. Direct evaluation gives live-root support53 and frame-root
support56. The same reasoning applied to a hypothetical support below53
proves the code distance is53, attained by live root normals.

## 2. Complete completion-cut graph

For a root normal a and binary seven-space V set

    C(a,V) = Off(a) \ Lambda(V).

Normal a qualifies for S exactly when C(a,V) subset S for some V: extend its
residual label span to a seven-space. Every one of120*43,435=5,212,200 pairs
is tested. There are24,264 completion records with cut size<=30, and24,264
distinct (normal,cut) nodes. Their cut-size counts are:

| Size | Nodes |
|---:|---:|
| 21 | 336 |
| 23 | 5,376 |
| 24 | 504 |
| 25 | 3,136 |
| 27 | 10,752 |
| 28 | 1,024 |
| 29 | 3,136 |

Join two nodes of distinct normal owners exactly when their cuts have union
size<=30. Exhaustive pair comparison gives9,828 edges. A collection admitted
by the SAME S gives a clique and its total cut union has size<=30; pairwise
compatibility alone is never substituted for this total-union condition.

The primary walks increasing-index cliques while retaining the total union.
It continues a prefix only when its normals are rationally independent.
Every independent four-tuple has all its ordered prefixes independent,
so pruning dependent prefixes cannot omit a four-dimensional witness.
The full visited counts are:

| Prefix length | Union size | Rational rank | Count |
|---:|---:|---:|---:|
| 1 | as above | 1 | 24,264 |
| 2 | 22,24,25,26,28,29,30 | 2 | 9,828 |
| 3 | 30 | 2 | 896 |
| 3 | 30 | 3 | 3,584 |
| 4 | 30 | 3 | 2,688 |

There is no independent four-prefix. Thus if the qualifying directions for
an arbitrary S spanned dimension>=4, choosing four independent root normals
and one contained completion cut for each would produce a visited independent
four-prefix, a contradiction. Rational ranks of these root vectors equal
their ranks over K. This proves the common30 span bound.

Every triple of distinct root normals has an independent first pair. All
admitted triples are consequently visited, including dependent triples.
Their union size is always30. Hence |S|<=29 permits at most two projective
normal directions. The listed independent triple at30 also shows that the
cut allowance29 is maximal for a uniform span-at-most-two statement.

A separate finite-core checker imports neither primary nor predecessor
executables. It reconstructs the shell, computes integral coordinates with
Cramer's rule/Bareiss determinants, and enumerates10,795 six-spaces in F2^8
with four affine cosets each, plus255 leading-zero spaces. All flat,
completion-record, node and edge digests agree. It directly tests all
compatible quadruples with total cut union<=30, including those with a
dependent first triple, using exact Gram determinants rather than the
primary's rational-elimination/prefix-pruning algorithm. This corroboration
is within the same donor/assistant context, not independent human or
formal-kernel acceptance.

## 3. The actual quotient and intersection dimension

Let T be the span of the eleven independent pieces in the stated profile,
D=T intersect C, and assume dim D>=5. Then dim(T/D)<=6. The first six pieces
have support union S of size at most5*2+20=30. A binary rank-two support has
at most2 sites because all labels have leading one. The global rank-six
capacity20 is credited to Nick Petalas/PR3269 and rechecked here on every
788,035 binary six-space. Since30<53, every nonzero combination of those
six independent pieces has support below the code distance and is not a
codeword. Their quotient images are independent. Thus dim(T/D)=6 and dim D=5.

For each of the five remaining rank-seven pieces q_y, its quotient image
has a unique representative a_y in the six-piece span. Then c_y=q_y-a_y lies
in C. These five codewords are independent: their coefficients on the five
distinct nonbasis pieces are the identity matrix in the original independent
piece basis. Injectivity of evaluation gives five independent normals h_y.
Outside the SAME S, their supports lie in support(q_y), so their binary
support ranks are at most7. The theorem allows span dimension at most3,
contradicting5. Coefficients, overlaps and cancellations are unrestricted.

The authenticated original PR3154 necessary filter retains the literal list.
Its strict excess is29<30. All462 six-piece subsets are checked: the minimum
certified capacity sum is30, attained only by the five rank-two and one
rank-six pieces. This is not a lower bound on an actual support union.

## 4. Credit and limits

Nick Petalas supplies the global capacities, root-shortening and common-cut
lineage (including PR3269,3163,3282,3289); DreamingOfClouds/PR3154 supplies
TWOSIDE/C5; David Arias supplies the quadratic model; joaqcoo and retained
E8/P112 sources retain their attribution. This donor's PR3951 audits inherited
bounds and the field step; PR3960 supplies the common24 theorem and two
other callers. The table model and separate shell/Cramer implementation are
explicitly adapted from PR3960, and are not claimed newly independent of it.
The new finite graph, complete common30 span proof and named caller exclusion
are this package's contribution. Frozen predecessors are unchanged.

No complete cell reconciliation, full C5, complete decoder floor, native
physical/restoration/consumer/all-size/supplier admission, selected cold
replay or new kappa is claimed. Written proof and finite computation remain
subject to mathematical review. Chris R / Clear1nsight, with substantial
OpenAI Codex assistance, Apache-2.0.
