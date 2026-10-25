# Four terms cannot reduce a literal pair's actual-reader tariff

## Statement

Let a finite set of n indexed binary labels be partitioned into positive even
groups, with identity Gram matrix within every group. Pair consecutive ports
of each group into complete Gram-I2 planes. Each group's two alternating
halves defines an indicator vector. Fix two distinct indicators a,b. Their
scalar supports are disjoint; their group sizes m_A,m_B may come from the same
group. Cross-group pairings are unrestricted.

For a scalar vector x, cl(x) contains both ports of every plane touched by a
nonzero entry of x. Define the actual-reader tariff

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Over ANY coefficient field F, suppose at most four actual terms satisfy

    aa^T + bb^T = sum_i u_i q_i^T.

Both factors are arbitrary vectors on all n ports. In particular, they may
have external directions, nonbinary values, repeated rays, zero terms, and
cancellations outside the target supports. Then

    sum_i C(u_i,q_i) >= m_A + m_B.

The two original terms attain equality. Thus disjoint pair replacements by
at most four terms retain the whole literal tariff 2n, or 224 on the retained
PR3370 P112 fixture. This is an algebraic support-tariff theorem, not a native
execution or supplier theorem. It does not change the selected exponent.

The new case relative to PR3414, PR3463 and PR3472 has both factor ranks three.
No predecessor theorem or pending executable source is assumed below.

## A six-point representation lemma

Any vector configuration of rank two or three on at most six indexed elements
has a representation over GF16 with the same rank for EVERY indexed subset.
Remove zero elements and identify parallel nonzero elements first. After
representing the resulting simple configuration, restore zeros and parallel
copies. Their original nonzero proportionality constants need not be preserved.
They do not affect subset ranks. Two distinguished independent elements remain
independent.

For rank two, inject its at most six projective points into the seventeen
points of the projective line over GF16. Subset ranks are determined by zero,
parallelism and the presence of two distinct points.

For rank three, freely add generic points until there are six simple points.
This is legitimate over an infinite extension of the original coefficient
field: choose each new point outside the finitely many old points and lines.
This extension changes no old subset rank. Removing added points later will
retain the desired representation. It is enough to classify six simple points
of rank three by their collinear triples.

If a line contains five points, the sixth is outside it. There is one type.
If the longest line contains four points, the other two points are outside.
Their join meets that line either at one of its four selected points or at an
unselected point. These are the two types. No other collinear triple is possible:
two points on the long line already determine that line.

If every line has at most three points, call the three-point lines triples.
Two distinct triples share at most one point. Each point belongs to at most
two triples, because three triples through it would require seven points.
If there are t triples, 3t <= 12, so t <= 4.

For t=0 or t=1 there is one type each. For t=2 the triples either meet or are
disjoint, giving two types. For t=3, their nine incidences must fit into six
points. Since every degree is at most two, at least three points have degree
two. There are only three pairs of triples, so each pair meets once, at three
different points. This is the triangle type. For t=4, all six points have
degree two, every pair of triples meets once, and the type is the six pairwise
intersections of four lines in general position. This is the quadrilateral
type. These arguments give nine types in total, without a realizability
assumption on an enumerated candidate list.

Here are explicit representations of all nine types. Work in
GF16 = F2[t]/(t^4+t+1), writing each polynomial as its four-bit integer.
Let E=(1,0,0), F=(0,1,0), G=(0,0,1). Coordinates are projective columns.

| Type | Six points |
| --- | --- |
| No triple | (1,s,s^2) for s=0,1,2,3,4,5 |
| One triple | E,F,(1,1,0),G,(1,2,1),(1,3,2) |
| Two disjoint triples | E,F,(1,1,0),G,(1,2,1),(2,4,3) |
| Two meeting triples | E,F,(1,1,0),G,(1,0,1),(1,2,4) |
| Three triangle lines | E,F,G,(1,1,0),(1,0,1),(0,1,2) |
| Four quadrilateral lines | E,F,G,(1,1,0),(1,0,1),(0,1,1) |
| Four-point line, selected join | E,F,(1,1,0),(1,2,0),G,(1,0,1) |
| Four-point line, unselected join | E,F,(1,1,0),(1,2,0),G,(1,4,1) |
| Five-point line | E,F,(1,1,0),(1,2,0),(1,4,0),G |

Taking the twenty 3-by-3 determinants verifies the stated incidences. The
checked lists and all relabelings are in TEMPLATES.json and the two verifiers.
For simple rank-three configurations, independent pairs and collinear triples
determine every subset rank. The templates therefore prove the lemma, rather
than only suggesting a finite-field pattern. The executable coverage check
also enumerates every short-line system allowed by the preceding combinatorial
argument, obtaining 1,20,100,120,30 labeled systems at t=0,1,2,3,4.

## Transfer both supports when the query rank is at most three

Let W be the span of the original queries q_i as actual port vectors. The row
space of the target is span(a,b), so a,b belong to W. Suppose dim(W) <= 3.
Apply the lemma to the at most six indexed vectors

    q_1,q_2,q_3,q_4,a,b in W.

Write their GF16 representatives as Q_i,A,B in a space W'. They preserve all
subset ranks and A,B are independent. We now build actual GF16-valued port
vectors q'_i,u'_i with the SAME target and termwise support inclusion.

At a source port p, put Z_p={i:q_i(p)=0}. We seek a linear functional f_p on
W' such that

    f_p(A)=a(p), f_p(B)=b(p), f_p(Q_i)=0 for i in Z_p.

If p is outside both indicators, take f_p=0. If a(p)=1, the original coordinate
functional on W vanishes on b and every q_i with i in Z_p, but not on a.
Consequently a is outside span(b,{q_i:i in Z_p}). This is precisely a subset
rank condition, so A is outside span(B,{Q_i:i in Z_p}). A functional with
the desired values exists. The b(p)=1 case exchanges A and B. Disjointness
of the indicator supports exhausts the cases. Define q'_i(p)=f_p(Q_i).
Every original query zero survives, and hence supp(q'_i) is contained in
supp(q_i), separately for each term.

At a reader port p, let S_p={i:u_i(p)!=0}. The old operator identity states
as an equality in W that

    a(p)a+b(p)b = sum_{i in S_p} u_i(p) q_i.

Outside the target supports set all u'_i(p)=0. At an a port this equality says
that a belongs to span({q_i:i in S_p}). Subset-rank preservation implies that
A belongs to span({Q_i:i in S_p}). Choose coefficients u'_i(p) supported in
S_p that express A. At a b port express B in the same way. Thus every original
reader zero survives too.

Applying f_r to the new reader equality for each source port r gives

    sum_i u'_i(p)q'_i(r) = a(p)a(r)+b(p)b(r).

The new factors need not preserve the original query span as port vectors,
numeric coefficients, independence, or external values. They preserve the
target operator and satisfy both support inclusions. Deleting rows or columns
cannot increase binary rank, and plane closure respects inclusion, so

    C(u'_i,q'_i) <= C(u_i,q_i) for each i.

This transfer is the additional step needed when queries AND readers have
independent external directions. It is not a common-seed star argument and
does not require readers to lie in span(a,b).

## Four terms always admit the transfer on one side

Pad a shorter list with zero terms. Let U and Q have their four factor vectors
as columns, so U Q^T has rank two. Write r=rank(Q), s=rank(U). Restrict the
map U to the r-dimensional image of Q^T. Its kernel there has dimension at
most dim ker(U)=4-s. Therefore

    2 = rank(U Q^T) >= r+s-4, so r+s <= 6.

Both r and s are at least two. If r<=3, use the preceding transfer. If r=4,
then s<=2; transpose the symmetric target identity and transfer the readers
instead. Binary Gram rank, and thus C, is unchanged by this transposition.
This also explains why the genuinely new residual case is r=s=3. No rank
classification by itself would settle that case; the six-point transfer does.

## The characteristic-two expanded identity supplies the bill

For all indicators v_c in the partition put K=sum_c v_c v_c^T. Expand a scalar
port to its two plane coordinates. Replace each scalar entry M_pr by M_pr
times the binary 2-by-2 Gram block of the planes at p,r, interpreted over GF16.
This is a linear operation on scalar matrices.

The expansion of K is I_(2n). A diagonal entry supplies I2. Any other nonzero
entry connects different planes in one orthonormal group, with zero Gram block.
The two ports of one plane belong to different indicator halves, so the scalar
entry between them is zero. These cases cover every entry.

The expansion of a term u q^T factors through Gram(cl(q),cl(u)), up to
transposition, by selecting, repeating and scaling its plane rows and columns.
Its GF16 rank is at most the binary rank C(u,q). A binary matrix has the same
rank over F2 and GF16, since extending a field preserves rank. This statement
does not reinterpret a binary rank as a characteristic-zero rank.

Append every untouched original indicator term to the transferred pair
realization. Their bill is 2n-m_A-m_B and their sum with the new pair is K.
Rank subadditivity for the expanded I_(2n) yields

    sum_i C(u'_i,q'_i) >= m_A+m_B.

Termwise support domination proves the same inequality for the original
factors. Using the two original indicator terms proves sharpness.
The expanded-identity idea retains Philippe Van Velzen's and PR3345's credit.

## Where the argument stops

Five terms plus two distinguished targets can contain seven projective points.
The six-point representation lemma does not extend automatically. The seven
rational vectors E,F,G,E+F,E+G,F+G,E+F+G have six collinear triples. In any
characteristic-two representation of those incidences with all points distinct,
normalize the first three to the axes and write the next three as
(1,a,0),(1,0,b),(0,1,c), with a,b,c nonzero. The last point's three incidences
force b=ac. The determinant of the preceding three points is then b+ac=0.
Over the rationals that determinant is -2. A required independent triple has
become dependent. This is a proof-method boundary, not a cheaper five-term
P112 factorization or a universal five-term obstruction.

The theorem is specific to a fixed sum of two disjoint indicator terms and
the additive complete-plane rectangular tariff. Arbitrary five-term lists,
larger target blocks, changed fitting matrices, different closure/cost rules,
shared native operations and nonlinear contracts remain separate. No source
acquisition, coefficient execution, frames, dirty restoration, hosting, stock,
precision, all-size/compiler admission, complete supplier or multiplication
transfer is established. Independent human and formal proof-kernel review are
unclaimed. The exact finite checks corroborate the written universal proof.
