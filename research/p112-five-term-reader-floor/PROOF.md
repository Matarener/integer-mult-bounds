# Five actual terms cannot lower a literal pair's tariff

## Statement

Partition n indexed binary labels into positive even groups, with identity
Gram matrix inside each group. Pair consecutive ports of each group into
complete Gram-I2 planes. The two alternating halves of every group define
two scalar indicator vectors. Choose two distinct indicators a,b, from groups
of sizes m_A,m_B; the groups may coincide. The scalar supports of a,b are
disjoint. Cross-group binary pairings are unrestricted.

For a scalar vector x let cl(x) include both ports of each plane touched by a
nonzero coordinate of x. Charge the actual term u q^T by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Over every coefficient field F, every identity with t <= 5 terms

    aa^T + bb^T = sum_(i=1)^t u_i q_i^T

satisfies sum_i C(u_i,q_i) >= m_A+m_B. Queries and readers may have arbitrary
external directions, numeric values, repeated rays, zeros and cancelling
spectator values. The original two terms attain equality. Thus any disjoint
pair replacements using at most five terms preserve the complete literal
bill 2n, including 224 on a 112-port partition.

This extends PR3489's four-term theorem and PR3506's non-Fano five-ray case.
The new step is the complete seven-point classification. This is a written
proof with exact finite incidence/field certificates, not a proof-kernel
verification or a physical supplier theorem. No exponent improvement follows.

## A seven-point finite representation lemma

A simple rank-three configuration on seven indexed projective points has one
of the 23 line systems in TEMPLATES.json. Each maximal line with at least
three points is encoded by the bit mask of its point set. Twenty-two systems
have the displayed seven-column representations over
GF16=F2[t]/(t^4+t+1), with field elements encoded by their four polynomial bits.
The remaining system is the non-Fano pattern. The all-seven-points line is
rank two and is excluded from the 23.

Here is an exhaustive enumeration argument, rather than an assumption that
an external matroid catalogue is complete. Two distinct maximal lines share
at most one selected point. Delete the last point from a configuration on k+1
points. A line through the deleted point and at least two old points leaves
one of two objects: an entire old maximal line of size at least three, or a
pair not already on an old line. Distinct lines through the new point leave
disjoint old point sets. All old maximal lines not extended remain unchanged.
Consequently every extension is obtained by choosing a disjoint family from
these old lines and uncovered pairs, adjoining the new point to each chosen
block, and retaining the other old lines. The empty family is allowed.
There are at most floor(k/2) chosen blocks.

Starting with one point and no recorded line, this rule enumerates every
possible incidence system through seven points. To identify relabelings,
assign each point its sorted multiset of incident line sizes. Any isomorphism
preserves this signature. Arrange signature classes in sorted order, try every
permutation within them, and choose the least sorted tuple of line masks.
This is a complete canonical labeling: the restriction removes no possible
isomorphism. The numbers of types at sizes 1 through 7, including the all-point
line when present, are exactly

    1, 1, 2, 3, 5, 10, 24.

verify.py regenerates these systems and matches the entire template set.
It checks all 128 subset ranks of each of the 22 representations by field
elimination, including nonzero/distinct points and rank three. Thus line
incidences are sufficient to identify all subset ranks, not just some tested
triples. Rank zero/one/two cases are recognized before any rank-three case.

independent.py uses a different exhaustive construction. It lists every subset
of {0,...,6} of sizes 3 through 7, records its consumed pairs, and enumerates
every family whose consumed pairs are disjoint. It finds 8,390 labeled line
systems. These are exactly the union of all 5,040 relabelings of each of the
24 templates, including the rank-two line. No presumed orbit sizes enter the
comparison. It embeds GF16 into GF256=F2[z]/(z^8+z^4+z^3+z+1) and checks all
2,816 subset ranks again using pair minors and triple determinants. The two
implementations do not import each other. These finite certificates prove the
stated coverage; they do not claim an independent human mathematical review.

For an augmented configuration of at most seven indexed vectors of rank at
most three, remove zero elements and identify parallel elements. Rank two is
represented by at most seven distinct points of the 17-point projective line
over GF16. For rank three with at most six simple points, extend the coefficient
field to an infinite field and add generic points until there are seven.
Each added point avoids all existing points and pair-lines. This changes no
old subset rank. The resulting system has a point on no recorded line, so it
cannot be non-Fano, where every point belongs to at least two lines. Apply its
GF16 template, delete the added points and restore zero/parallel copies.
Only subset ranks need preservation; old proportionality constants do not.

The only residual case has seven simple rank-three points in the non-Fano
pattern. It need not preserve every subset rank: the next lemma preserves
exactly the implications used by two independent marked targets.

## The non-Fano marked-target exception

Use the ordered rational columns

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G, P5=F+G, P6=E+F+G.

Their six lines are 013,024,056,125,146,236. For any marked pair A,B and the
other five columns Q_i, a characteristic-two configuration A',B',Q'_i exists
with independent marks and the following properties for every query subset:

    A outside span(B,Q_Z) => A' outside span(B',Q'_Z);       (source)
    A in span(Q_S)        => A' in span(Q'_S).              (reader)

Both statements also hold with A,B exchanged. They depend only on the old
subset-rank pattern, so apply to every representation of that pattern over
any field. Work over GF4=F2[w]/(w^2+w+1). Three explicit cases suffice:

| Marked pair | New columns |
| --- | --- |
| P0,P1 | Replace P3 by (1,1,w); retain the other binary columns |
| P0,P3 | Interpret all seven binary columns in GF4 |
| P3,P4 | Replace P5 by (0,1,w); retain the other binary columns |

The four points {0,1,2,6} are the vertices of a complete quadrangle. The other
three are its perfect matchings: 3=01|26, 4=02|16, 5=06|12. Permuting the four
vertices preserves the six lines and gives a 24-element action transitive on
the six vertex/vertex pairs, twelve vertex/matching pairs and three
matching/matching pairs. These are precisely the three table cases.

Both checkers verify every implication for every one of the 21 marked pairs,
using all 32 subsets and both orientations. There are 288 true source premises
and 672 true reader premises among the 2,688 candidates. The primary checker
uses GF16 elimination with w=6. The second uses rational integer determinants
for the old ranks and GF256 determinants for the new ranks. It does not infer
old ranks by reducing the integer columns modulo two. This rechecks the exact
selective transfer of PR3506; it does not claim to represent the entire
non-Fano matroid in characteristic two. The retained predecessor proof and
three templates preserve its source credit and exact public bytes.

## Transfer the supports on a rank-three side

Let W be the span of the actual queries q_i. The target row space shows that
a,b belong to W. If rank(Q)<=3, apply the preceding classification and marked
lemma to q_1,...,q_t,a,b. Pad missing queries with zero columns. For non-Fano
use its selective table; for all other cases use the full GF16 representation.
We obtain independent A',B' and Q'_i satisfying both marked implications.
GF4 embeds in GF16, so use GF16 for every case.

For a source port p on a's support let Z_p={i:q_i(p)=0}. The old coordinate
functional vanishes on b and Q_Z but takes value 1 on a. Therefore a is
outside span(b,Q_Z). The source implication supplies a functional f_p on the
new span with f_p(A')=1, f_p(B')=0 and f_p(Q'_i)=0 for every i in Z_p. At a b
port exchange the two marks. Outside both supports take f_p=0. Define the
actual new query by q'_i(p)=f_p(Q'_i). Every old query zero survives.

For a reader port p on a's support, the original operator equation gives

    a = sum_(i in S_p) u_i(p) q_i,  S_p={i:u_i(p)!=0}.

The reader implication expresses A' in span(Q'_(S_p)). Choose such coefficients
as u'_i(p), with zero values off S_p. At a b port express B' instead. Outside
both target supports set all new reader coefficients to zero, even where old
readers cancelled. Thus every old reader zero survives too. Applying f_r to
the reader equation yields the literal port identity

    sum_i u'_i(p)q'_i(r)=a(p)a(r)+b(p)b(r).

Both supports shrink term by term. Plane closure preserves inclusion, and
removing rows/columns cannot increase binary matrix rank. Consequently
C(u'_i,q'_i)<=C(u_i,q_i). Neither the old numeric coefficients nor external
values/directions need preservation. This is why preserving the two marked
implications is enough.

## Five terms always have a rank-three side

Let U,Q have t columns, the actual readers and queries. Their product UQ^T
has rank two. Restrict U to the rank(Q)-dimensional image of Q^T. Its kernel
there has dimension at most t-rank(U). Hence

    rank(U)+rank(Q) <= t+2 <= 7.

Both ranks are at least two. At least one is at most three. Use the preceding
support transfer on Q if possible, otherwise transpose the symmetric target
identity and transfer on U. The binary Gram matrix is transposed by swapping
the factors, so the tariff is unchanged. This completes the reduction for
every t<=5; there is no remaining rank-(3,4) exception.

## The characteristic-two expanded identity forces the bill

Let v_c be every original alternating-half indicator and K=sum_c v_c v_c^T.
Replace each scalar entry M_pr by M_pr times the binary 2-by-2 Gram block
between the complete planes at p,r, interpreted in GF16. This expansion is
linear in M. The expansion of K is I_(2n): diagonal entries supply I2;
distinct planes in one orthonormal group have zero Gram block; and the two
ports of the same plane belong to different indicators, so their scalar
cross-entry is zero. These exhaust its nonzero possibilities.

An expanded term u'q'^T factors through Gram(cl(q'),cl(u')), up to transpose,
using selection, repetition and row/column scaling. Its GF16 rank is at most
C(u',q'). A binary matrix has the same rank over F2 and GF16. This uses a
field extension within characteristic two, never characteristic-zero rank
of a binary-entry matrix.

Append the untouched original indicator terms to the transferred pair. Their
bill is 2n-m_A-m_B. Rank subadditivity for the expanded I_(2n) gives

    sum_i C(u'_i,q'_i) >= m_A+m_B.

Support domination proves the same lower bound for the original factors. The
original two terms each have the identity Gram matrix of their whole group,
and therefore attain m_A+m_B. This proves sharpness.

The expanded-identity method retains Philippe Van Velzen's PR3345 credit;
the arbitrary-reader support-transfer lineage includes PR3414, PR3463,
PR3472, PR3489, PR3491, PR3505 and PR3506. The new finite classification closes
the previously stated five-term pair gap.

## Boundary

Six terms can have factor ranks (4,4), beyond this classification. Three or
more marked targets, changed fitting matrices, masked identities, different
closure/cost rules, and shared physical operations are separate questions.
This theorem does not prove a global P112 decoder floor. Native acquisition,
coefficient execution, frames, dirty restoration, hosting, stock, precision,
compiler/all-size admission, a complete paid consumer, both suppliers and the
outer multiplication theorem remain unproved here. No selected-frontier file
is changed. Independent human and formal proof-kernel review are unclaimed.
