# The non-Fano exception admits two marked targets

## Claim and tariff

Let n indexed binary labels have a partition into positive even groups. Each
group has identity Gram matrix over F2. Pair consecutive ports in each group
into complete Gram-I2 planes. An indicator of either alternating half touches
one port of each plane in its group. Let a,b be two distinct such indicators,
from groups of sizes m_A,m_B, possibly the same group. Their scalar supports
are disjoint. Cross-group binary pairings are unrestricted.

For a scalar port vector x, cl(x) contains both ports of each plane touched by
its nonzero coordinates. Charge an actual term by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Let F have characteristic other than two and suppose

    aa^T + bb^T = sum_(i=1)^5 u_i q_i^T.

Assume that the seven indexed vectors a,b,q_1,...,q_5 have the subset ranks of

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G, P5=F+G, P6=E+F+G,

with any two of these seven points distinguished as a,b. In particular this
covers arbitrary projective scalings and invertible changes of coordinates of
the canonical non-Fano configuration. Both actual factors can have arbitrary
external coordinates, and the u_i have no span restriction. Zero readers and
cancellations outside the target supports are permitted. Then

    sum_i C(u_i,q_i) >= m_A+m_B.

This closes the non-Fano five-ray subquestion of PR3489. It does not classify
other seven-point configurations or prove the floor for every five-term pair
factorization. It is an algebraic support-tariff statement. There is no new
supplier, exponent, or selected-frontier claim.

## The rank conditions that are actually needed

Write A,B for the two marked points and Q_i for the other five. A new
configuration A',B',Q'_i over a characteristic-two field need only satisfy the
following implications, separately with A and B exchanged:

    A outside span(B,{Q_i:i in Z})
        implies A' outside span(B',{Q'_i:i in Z});               (source)

    A in span({Q_i:i in S})
        implies A' in span({Q'_i:i in S}).                      (reader)

A',B' must also be independent. Here Z,S range over all 32 subsets of the five
query indices. Preserving every subset rank is a stronger requirement. These
implications can hold even if an unneeded independent triple becomes dependent
or an unneeded old line breaks.

## Three GF4 configurations prove the marked-target lemma

Use GF4=F2[w]/(w^2+w+1), encoded by 0,1,2=w,3=1+w. Retain P0,...,P6 as the
ordered point list. The following changes produce valid new configurations:

| Marked pair | New configuration | Source implications | Reader implications |
| --- | --- | ---: | ---: |
| (P0,P1) | Replace P3 by (1,1,w); retain the other six points | 14 | 34 |
| (P0,P3) | Use the original binary coordinates, interpreted in GF4 | 13 | 31 |
| (P3,P4) | Replace P5 by (0,1,w); retain the other six points | 16 | 32 |

The counts include both marked orientations. Every one of the 128 candidate
implications per row is checked in verify.py; only implications with a true
original premise contribute to the two counts. This is a finite rank proof:
for each subset, compare the ranks before and after adjoining the marked
point. Gaussian elimination uses exact field arithmetic. independent.py checks
the same implications using 2-by-2 minors and 3-by-3 determinants in a different
field, GF16, with w embedded as 6 and polynomial t^4+t+1. It also checks the
original ranks over F3,F5,F7. No random search or floating-point acceptance is
part of this lemma.

These rows cover all 21 marked pairs. To see this without classifying arbitrary
seven-point matroids, the original configuration has exactly the six lines

    013, 024, 056, 125, 146, 236.

The four points O={0,1,2,6} are the vertices of a complete quadrangle. The
remaining three points D={3,4,5} correspond to its three perfect matchings:

    3: 01|26,  4: 02|16,  5: 06|12.

Every permutation of O permutes these matchings and preserves the six lines.
Thus S4 acts transitively on the six O/O pairs, twelve O/D pairs and three D/D
pairs, represented by the three table rows. Distinct points are independent,
and these six lines determine every subset rank in rank three. This action
therefore preserves all old rank conditions. Relabeling the table rows gives
all 21 cases. The full check finds 288 source and 672 reader implications.

The old ranks are the same in every characteristic other than two. The 35
integer determinants have values only 0,+1,-1,+2,-2, with zeros precisely on
the six lines; each pair has a nonzero 2-by-2 minor equal to +1 or -1. Hence
reduction in an odd characteristic cannot change a subset rank. An extension
field also preserves rank. The finite table consequently proves the lemma for
every F in the claim, not just the rational fixture or the tested primes.

## Transfer the actual supports

Apply the lemma to the seven vectors in their query span. At a source port p
where a(p)=1, let Z_p={i:q_i(p)=0}. The old coordinate functional is nonzero on
a and zero on b and all queries in Z_p. Therefore a is outside their span.
The source implication gives a GF4 functional f_p with

    f_p(A')=1, f_p(B')=0, f_p(Q'_i)=0 for i in Z_p.

At a b port exchange A' and B'. Outside both target supports take f_p=0.
Define q'_i(p)=f_p(Q'_i). Every old query zero remains zero. Numeric values,
external query coordinates and the original span are not preserved or needed.

At a reader port p where a(p)=1, the old operator equation gives

    a = sum_(i in S_p) u_i(p) q_i,  S_p={i:u_i(p)!=0}.

The reader implication expresses A' in the span of the corresponding Q'_i.
Choose coefficients u'_i(p) supported in S_p for that expression. At a b port
express B'. Outside both targets set all new readers to zero, even if the old
readers cancelled there. No old reader zero becomes nonzero.

Apply the source functional at port r to the new reader equation at p. It gives

    sum_i u'_i(p)q'_i(r) = a(p)a(r)+b(p)b(r).

Thus the new literal operator is the same target, and both factors have
termwise support inclusion. Plane closure preserves inclusion. Deleting rows
or columns of a binary Gram matrix cannot increase rank, so

    C(u'_i,q'_i) <= C(u_i,q_i).

This handles arbitrary external reader directions as well as external query
directions. Projective scalings in the original configuration do not affect
any span premise. The two disjoint indicators allow us to assign the new
functional values 1 and 0 without preserving those original scalings.

## The expanded identity proves the bill

Let v_c run over every alternating-half indicator and K=sum_c v_c v_c^T.
Expand a scalar matrix entry M_pr into M_pr times the binary 2-by-2 Gram block
between the complete planes at p,r. Treat that block over GF4. The expansion
is linear in M. The expansion of K is I_(2n): a diagonal block is I2, different
planes in one orthonormal group have zero Gram block, and the two ports of
one plane belong to different indicators and hence have scalar entry zero.

The expansion of u'q'^T factors through Gram(cl(q'),cl(u')), up to transpose,
by selection, repetition and scaling of its rows and columns. Its GF4 rank is
at most C(u',q'). A binary matrix has the same rank over F2 and GF4, since GF4
is an extension field. There is no identification with characteristic-zero
binary-entry rank in this step.

Append the untouched indicator terms to the new realization. Their total bill
is 2n-m_A-m_B. Rank subadditivity for I_(2n) gives

    sum_i C(u'_i,q'_i) >= m_A+m_B.

Support inclusion proves the claimed inequality for the original factors.
The proof is self-contained. The expanded-identity method retains Philippe
Van Velzen's PR3345 credit and the preceding actual-reader lineage.

## The predecessor boundary remains true

PR3489 correctly shows that the entire seven-point non-Fano matroid has no
characteristic-two representation. Its six lines force the triple P3,P4,P5
to be dependent in characteristic two, whereas its rational determinant is
-2. This package does not change that result. It replaces whole-matroid rank
preservation by the two implications the pair proof needs. The new GF4 table
deliberately changes some unneeded subset ranks.

The 21 literal fixtures have query/reader ranks (3,4), a query value outside
the target support and a nonzero cancelling reader row on another spectator.
The checker transfers both supports and compares all 112-by-112 operator
entries and all actual rectangular Gram bills. Their bills are examples,
not global minima. The written proof supplies the universal quantifiers.

Other five-query rank patterns, six or more query rays, larger target blocks,
changed fitting matrices, shared physical operations and different closure
rules remain outside this statement. Native acquisition, coefficients,
frames, restoration, hosting, stock, precision, compiler/all-size admission,
complete suppliers and outer multiplication transfer are not established.
Independent human and formal proof-kernel review are unclaimed.
