# Regular query dictionaries preserve the full reader floor

## Statement

Let n indexed ports carry binary labels in F2^d. Partition the ports into
positive even-sized groups G, each with within-group Gram matrix I. Pair
consecutive ports within each group into complete Gram-I2 planes. The two
alternating halves of each group define disjoint scalar indicator vectors
a_j. Put K = sum_j a_j a_j^T. These hypotheses impose no restriction on
cross-group pairings, d, n or the number of groups.

Choose any k distinct indicators b_1,...,b_k, with complete-group sizes
m_1,...,m_k. Two chosen indicators may come from the same group. Over any
coefficient field F, suppose an arbitrary finite exact factorization satisfies

    sum_(j=1)^k b_j b_j^T = sum_(i=1)^t u_i q_i^T,
    q_i = sum_(j=1)^k Q_ji b_j.

Readers u_i may have arbitrary entries on every port. They need not lie in
the target span, and may cancel outside the target support. Query count,
repetitions, signs, denominators and characteristic are unrestricted.

The hypothesis on the complete query coefficient matrix is

    Q = D A E,

where D and E are invertible diagonal matrices over F and A is an integer
totally unimodular matrix, interpreted in F. Totally unimodular means every
square minor is 0, 1 or -1. Zero columns can be discarded with their terms.
There is no bound on the dimensions of A in this statement.

For a scalar vector v, cl(v) contains both ports of every matched plane
touched by its nonzero entries. Charge a term its actual-reader tariff

    C(u,q) = rank_F2 Gram(cl(q), cl(u)).

Then

    sum_i C(u_i,q_i) >= sum_j m_j.

The original literal terms attain the floor, and their query matrix I is
totally unimodular. Thus the minimum over the stated class is sharp. In
particular, this class cannot reduce the whole-K tariff 2n. For the retained
PR3370 partition of the selected 112 P112 labels, the sharp whole-K floor is
224. The same statement holds after interchanging queries and readers by
transposition of the exact operator and of each rectangular Gram matrix.

This is a support-tariff theorem, not a native implementation or an improved
selected multiplication bound.

## A field-independent axis-span lemma

Appending unit columns to a totally unimodular matrix preserves total
unimodularity. To see this, take any square minor using a new unit column.
It is zero if that column is zero on the selected rows. Otherwise expansion
along that column leaves, up to sign, a smaller minor. Repeat until only an
A minor or an empty determinant remains. Its value is 0, 1 or -1.

Fix any subset J of the query columns and any target axis e_j. Both A_J and
[A_J | e_j] therefore have the same rank over every field. Indeed their
nonzero integer minors are units in every field, and their zero integer
minors stay zero. Consequently

    e_j in span_F(A_J) iff e_j in span_F2(A_J mod 2).

This is the only coefficient-field transfer required below. It does not
assert a field homomorphism from F to F2. In particular, it does not reduce
an arbitrary rational reader coefficient modulo two.

## Preserve query supports and shrink reader supports

At a port p, let J_p be the indices of its nonzero original readers. Comparing
coefficients in the independent disjoint target indicators gives

    sum_i u_i(p) Q_:i = (b_1(p),...,b_k(p))^T.

If p is outside all selected indicators, the right side is zero. Set every
new reader to zero at that port. If p belongs to b_j, the right side is e_j.
Nonzero column scalings E do not change the span of the active columns.
Multiplication by D^-1 takes e_j to a nonzero multiple of e_j. Therefore
e_j belongs to span_F(A_(J_p)). The axis-span lemma supplies binary
coefficients on those same active columns that sum to e_j. Use these as the
new reader values u'_i(p), and use zero for every inactive column.

For every i, define the new binary query

    q'_i = sum_j (A_ji mod 2) b_j.

Each A entry is 0, 1 or -1. Its nonzero pattern is unchanged in every field.
Since the target supports are disjoint and D,E have no zero diagonal entries,
supp(q'_i) equals supp(q_i). The rowwise construction gives

    sum_i u'_i (q'_i)^T = sum_j b_j b_j^T over F2,
    supp(u'_i) subset supp(u_i).

This handles arbitrary global readers and their cancellations port by port;
it does not merge unrelated query rays. Plane closure preserves inclusion.
Deleting columns from a binary matrix cannot increase rank, so each new
term satisfies C(u'_i,q'_i) <= C(u_i,q_i). No termwise substitution of query
self-cost for actual reader cost is used.

## Expanded identity and the sharp tariff

Append every untouched literal indicator term to the new binary realization.
It realizes all of K over F2. Expand a scalar n-by-n matrix M by replacing its
entry M_pq by M_pq times the binary 2-by-2 Gram block between the planes at
p and q. This is an F2-linear map.

The expansion of K is I_(2n). A diagonal entry contributes I2. Distinct ports
in the same indicator lie in different planes of one orthonormal group, so
their Gram block is zero. All other scalar entries of K are zero. In
particular, the two ports of one plane lie in different alternating halves.
These cases check every expanded entry.

The expansion of a binary term u q^T factors through the rectangular Gram
matrix on cl(q),cl(u), up to transposition. Select the complete source and
reader planes, repeat their rows or columns at the corresponding scalar ports,
and multiply by the scalar entries of q and u. This produces exactly the
expanded term, so its binary rank is at most C(u,q).

Rank subadditivity forces the full new bill to be at least rank I_(2n) = 2n.
An untouched indicator costs the size of its complete orthonormal group.
Their total is 2n - sum_j m_j. Subtraction proves that the replacement terms
cost at least sum_j m_j. Their original F-valued bill is no smaller by the
support containment above. The literal terms give equality over every field.

The expanded-identity argument follows Philippe Van Velzen's prior integral
floor, Arham Tahir/PR3345's corroboration and the immediate P112 reader predecessors. The new implication is the
arbitrary-target, diagonal-scaled TU dictionary transfer with global readers.

## Useful dictionaries and the exact boundary

Signed vertex-edge incidence matrices with one row deleted are totally
unimodular. A square minor with a column containing at most one nonzero
reduces by expansion. If every column has two nonzeros, their signs are
opposite and the sum of the selected rows is zero, so the determinant is
zero. Induction proves all minors are 0 or plus/minus 1. Adding unit columns
preserves the property. Thus arbitrary finite graph-difference query networks
and their nonzero diagonal rescalings cannot save this tariff.

A network matrix B^-1 C, for a full-rank square basis B of such an incidence
matrix C, is also TU. Here det B is plus/minus 1. A minor of B^-1 C equals,
up to sign, the determinant of the matrix obtained by replacing the
corresponding columns of B by columns of C, divided by det B. This follows
by applying B^-1 and expanding along the unreplaced identity columns.
Repeated columns give zero; otherwise the numerator is a C minor.

The finite controls also include every consecutive interval on four target
axes. They check every minor directly. These examples include four targets,+dense directions and readers outside the target supports, beyond the earlier
seven-ray triple census. The theorem itself has no four-target limit.

The hypothesis is substantive. Take the three query columns

    (1,1,0), (1,0,1), (0,1,1).

Their determinant is -2. Over Q, one half of the first plus one half of the
second minus one half of the third is e_1. Over F2 every column has even
coordinate sum, so their span omits e_1. No binary support-preserving transfer
of that reader request exists. This is a transfer failure, not evidence of a
cheaper reader bill. The previous triple census handles its specific
half-integral branch by a different argument. Neither theorem subsumes all
nonregular dictionaries.

## Distinction from the retained pairing-signing theorem

DreamingOfClouds's PR2111, `research/three-total-decoders/README.md` section 6,
Lemma W', uses a TU signing of the binary pairing matrix B. The TU condition
here is on the target-query coefficient matrix A. It places no regularity
condition on B. Both arguments use field-independent ranks of TU matrices;
the object to which that fact applies and the support transfer are different.
The older rank-three decoder problem is not claimed solved here.

Here is an admissible geometry whose B has no TU signing. Take eight labels
in F2^4, in the following order:

    e_1,e_2,e_3,e_4, 1+e_1,1+e_2,1+e_3,1+e_4,

where 1 is the all-ones vector. The first four and last four each have Gram
I4, so they are two legal even groups. If L is their 4-by-8 label matrix,
B = L^T L has rank four and the same column dependencies as L, because
L^T is injective. Contract the first column e_1. Quotienting its coordinate
gives the seven distinct nonzero vectors of F2^3. Thus the column matroid
of B has the Fano matroid F7 as a contraction.

For completeness, F7 has no representation over a field of characteristic
other than two. If it did, choose independent basis images a,b,c. Nonzero
row/column scalings make the pair images x=a+b and y=a+c. The remaining
pair image z is supported on b,c. The Fano line {x,y,z} forces z proportional
to b-c. The seventh point t lies in span(c,x) and span(b,y), so its three
nonzero basis coefficients are equal. It also lies in span(a,z), which
forces its b,c coefficients to be negatives. Hence 1=-1, a contradiction.
All stated nonzero coefficients follow because F7 is simple and each listed
three-element line contains no parallel pair.

If B had a TU signing over the integers, its signed matrix would have the
same ranks on every column subset over Q and F2, by the unit-minor argument.
Its rational column representation would therefore represent the same
matroid as B. Contracting a nonzero represented element is linear quotient,
so it would give a rational representation of F7, contradicting the previous
paragraph. No TU signing exists. Nevertheless every projectively TU query
dictionary in the present theorem is covered on this geometry. For example,
the four literal alternating indicators are a TU query basis and attain 16.
This is an explicit separation of sufficient hypotheses, not a new claim
about matroid classification or about the general PR2111 decoder problem.

## Family decision and limits

Narrow the algebraic search. Graph and network recoding within the fixed
indicator span and this additive tariff cannot provide a saving, even with
global readers or any number of target terms. Another construction needs a
nonregular dictionary, an external direction or a changed nonadditive
consumer contract, followed by an explicit cheaper literal factorization.
The determinant-two example alone does not justify construction expansion.

Native acquisition, coefficient execution, frame transitions, dirty-state
restoration, ownership, hosting, stock, precision, all-size/compiler admission,
complete suppliers and outer multiplication transfer remain unproved here.
The theorem is conditional on the stated binary geometry. Finite checks
corroborate examples and source binding; the written proof supplies the
unbounded statement. Independent human and formal proof-kernel review are
unclaimed. No new kappa or selected-frontier change is asserted.
