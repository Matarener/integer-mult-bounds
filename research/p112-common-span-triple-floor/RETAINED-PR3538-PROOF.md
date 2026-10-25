# Four arbitrary terms cannot save a literal triple's tariff

## Statement

Use the pinned P112 binary labels and Tekalign's PR3370 partition into sixteen
even orthonormal groups. Consecutive ports in each group form complete Gram-I2
planes. Its alternating halves give 32 disjoint scalar indicators. Choose any
three distinct indicators a,b,c, with complete-group sizes m_A,m_B,m_C.
Two indicators may be the two halves of the same group.

For a scalar vector x, cl(x) contains both ports of every plane meeting its
nonzero support. Define the actual-reader tariff

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Over every coefficient field F, every exact unmasked identity with t<=4 terms

    aa^T+bb^T+cc^T = sum_i u_i q_i^T

satisfies

    sum_i C(u_i,q_i) >= m_A+m_B+m_C.

Both factors may have arbitrary ambient coefficients, external directions,
zeros, repeated rays and cancellations. The original three terms attain the
floor. Disjoint triple replacements with at most four terms therefore retain
the original whole-partition tariff 224.

This is a source-specific, computer-assisted support-tariff theorem. It closes
the arbitrary-query four-term triple question, extending PR3527's four fixed
non-Fano query rays. It does not establish a cheaper decoder, physical program,
supplier, new kappa or universal floor for more terms or other partitions.
The author-written proof and exact replays are complete. Independent human
and formal proof-kernel review are unclaimed.

## A rank-three factor side and seven indexed points

Put the t query columns in Q and the readers in U. The target T has rank
three over every field, since its three nonempty disjoint indicators are
independent. Restrict U to the rank(Q)-dimensional image of Q^T. Its kernel
has dimension at most t-rank(U). Hence

    rank(U)+rank(Q) <= t+3 <= 7.

Both ranks are at least three, so one side has rank three. Transpose the
symmetric target if necessary. This preserves every tariff, because binary
Gram rank is unchanged by transposition. Now rank(Q)=3 and its span is exactly
span(a,b,c), since the row space of T lies inside the query span.

Consider the at most seven indexed vectors q_1,...,q_t,a,b,c. The complete
seven-point classification proved in PR3513, pinned here with its exact proof
and templates, gives the following dichotomy. Its rank-three configuration
admits a representation over GF16 with every indexed subset rank unchanged,
or it consists of seven distinct nonzero rays with the non-Fano incidence
pattern. Zeros and parallel copies can be restored after simplifying. With
at most six simple points, add generic points over an infinite extension and
then delete them after applying the seven-point templates. The new points lie
on no old pair-line, so the extension cannot be non-Fano. Extending the
coefficient field changes no original subset rank.

The classification's 23 simple rank-three line systems have 22 explicit GF16
representations and one non-Fano exception. Its exhaustive extension argument
and independent line-system enumeration are inherited mathematical premises,
not newly claimed classification results. The new replay checks all 2,816
subset ranks of those 22 exact templates again.

## Representable configurations and two selective non-Fano cases

The support-transfer theorem of PR3505 applies to the representable branch.
For completeness, only the following implications are needed. At a source
port on target j, a coordinate functional separates that target from the
other targets and all queries zero at that port. Preserving subset ranks lets
one choose the same separating functional in characteristic two. At a reader
port on target j, the exact operator equation says that target j belongs to
the span of the active queries. Preserve that span request and choose new
coefficients supported on those queries. Outside the targets take all new
source functionals and reader coefficients to be zero. Applying each new
source functional to each reader equation gives the same literal target
operator, with both supports contained term by term in the old supports.

For such a characteristic-two realization, replace scalar matrix entry M_pr
by M_pr times the binary 2-by-2 Gram block between its complete planes. The
expansion of T is diagonal of rank m_A+m_B+m_C. Diagonal scalar entries give
I2. Distinct ports in one indicator lie in distinct planes of an orthonormal
group, and have zero Gram block. Plane mates lie in different indicators,
with zero scalar cross-entry. Each expanded term factors through its actual
complete-plane Gram matrix. Over a characteristic-two extension its rank is
at most C(u,q). Rank subadditivity proves the floor. Support inclusion cannot
increase the binary tariff. This also handles an original characteristic-two
field directly, without classifying its configuration.

It remains to treat the non-Fano branch in characteristic other than two.
Use its standard projective columns

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G, P5=F+G, P6=E+F+G.

The six lines are 013,024,056,125,146,236. The four vertices 0,1,2,6 form a
complete quadrangle; 3,4,5 are its three opposite-side intersections. Every
representation with these incidences is projectively equivalent to these
columns. Indeed, send three vertices to the axes, rescale to send the fourth
to (1,1,1), and take the unique prescribed intersections. In characteristic
two the last three points would be collinear, contrary to non-Fano, so that
case cannot occur here.

Permuting the four vertices gives all 24 automorphisms. Its independent marked
triples have four orbits, with representatives and sizes

    (0,1,2):4, (0,1,4):12, (0,3,4):12, (3,4,5):1.

The six remaining triples are the six dependent lines. The replay checks all
5,040 permutations, all four orbits and their disjoint union of 29 independent
marked triples. Let the ordered marked triple be the target basis a,b,c.
For the middle two orbits, the following normalized query columns and binary
replacements suffice, in increasing order of the four unmarked indices.

| Marks | Original query coordinates | New binary coordinates |
| --- | --- | --- |
| 0,1,4 | (-1,0,1), (1,1,0), (-1,1,1), (0,1,1) | (1,0,1), (1,1,0), (1,1,1), (0,1,1) |
| 0,3,4 | (-1,1,0), (-1,0,1), (-2,1,1), (-1,1,1) | (1,1,0), (1,0,1), (0,1,1), (1,1,1) |

Each new query support lies inside the corresponding old coordinate support.
For each target and all 16 query subsets, every old target-span request stays
true after this replacement. The primary checks these 96 candidate requests
using the incidence ranks and GF16 elimination. The separate replay uses
integer minors for the old ranks and packed GF2 elimination for the new ones.
They obtain 14 true requests for the first row and 15 for the second. These
are implications, not full representations of the non-Fano matroid.

Each query is constant on each target support. Therefore the displayed
coordinate support inclusion gives source inclusion. The preserved target-span
requests let each actual reader port choose new coefficients on its original
active terms. This gives the same support-shrinking characteristic-two target
identity as above, and hence the tariff floor for both middle orbits.

## Why projective normalization does not restrict the coefficients

In any projective equivalence, a marked target can acquire its own nonzero
scalar s_j, and a query can acquire its own nonzero scalar t_i. Write the
canonical normalized query coordinates as N_ji. The actual query is then

    q_i=t_i sum_j (N_ji/s_j) a_j.

Let D be the diagonal port operator multiplying every port of target j by s_j
and every other port by one. It is invertible and commutes with T, including
when two selected targets are complementary halves of the same group. Set

    q'_i=D q_i/t_i, u'_i=t_i D^(-1) u_i.

The new sum is D^(-1) T D=T. Both supports are unchanged, and q'_i has exactly
the canonical coordinates N_ji. Thus the representative analysis covers every
numeric realization of the non-Fano pattern, including arbitrary external
readers. No equality of scalar coefficients is inferred from the incidence
pattern alone. The separate replay checks a full 112-by-112 operator with
nonzero spectators and independent target gauges 2,-3,5.

## The two remaining orbits

For marks (0,1,2), the four queries are a+b,a+c,b+c,a+b+c. Every ambient reader
belongs to PR3527's affine family. Its termwise support reduction to
w in {0,+1,-1} on the targets, zero elsewhere, is valid in every characteristic
other than two. Its exact census of 800 plane classes covers all 4,960 literal
target triples. Its minimum equals the original for six triples and exceeds
it for every other triple. This package pins that proof, code, result and all
runtime inputs. The registered replay executes its complete 185,031,864-state
primary again. The new checker also verifies all 800 reported floors. This is
inherited coverage, not a second newly implemented VVV census.

For marks (3,4,5), multiply all normalized queries by two and absorb that
nonzero scalar into their readers. The query rays become

    q1=a+b-c, q2=a-b+c, q3=-a+b+c, q4=a+b+c.

The exact solutions are

    u1=(a+b)/2-w, u2=(a+c)/2-w, u3=(b+c)/2-w, u4=w,       (1)

with arbitrary ambient vector w. Substitution proves the operator equation,
and solving the three independent coefficient equations proves exhaustiveness.
At an A port, w=0 gives reader support 1100 and w=1/2 gives 0011. At a B port
the corresponding supports are 1010 and 0101. At a C port they are 0110 and
1001. Every other w makes all four entries nonzero. Replacing it by zero
shrinks supports term by term. Outside the targets, w=0 deletes all four
entries. Each specialization remains exact by (1). Thus the exact minimum
over arbitrary coefficients is the minimum over two choices at each target
port. This works over every field with 2 invertible, including F3 and all
its extensions.

All four query closures equal the union S of the three complete target groups.
For concatenated target-port masks A,B,C and a binary choice mask W, the reader
masks are

    (A union B) xor W, (A union C) xor W, (B union C) xor W, W.

For every reader mask the primary computes the binary rank of its plane
columns projected against a basis of S. It then exhausts all W. Each target
has at most four ports, so each case has at most 4,096 assignments. Moving an
alternating half to its plane mates preserves query and reader closures.
There are 560 three-distinct-group classes and 240 repeated-group classes.
They represent 560*8+240*2=4,960 triples. The primary evaluates all 800 classes,
with 1,689,280 assignments.

The separate replay imports no primary code. It uses raw rectangular Gram
columns against every actual source port and solves all 4,960 target triples
without the plane-class shortcut. It checks 10,129,664 assignments. Both agree
on every row of the ordered stream [a,b,c,original,minimum,W] and its SHA256
`8c1512ea43fe447d843754b40e16e14fb0cb8ae64b85c249c2fc4c42cca09ce2`.
Rows are compact JSON arrays followed by ASCII newline, in lexicographic
triple order. W is the least integer minimizing mask, with bit order given by
the concatenated original target-port lists.

The minimum excess distribution is 220 at +2, 1,320 at +3, 100 at +4, 888 at
+5, 364 at +6, 1,200 at +7, 236 at +8 and 632 at +9. No MMM triple attains
the original bill. Together with the represented branch, two selective maps
and inherited VVV census, this proves the stated arbitrary-four-term floor.

## Limits and attribution

This closes all query dictionaries at at most four terms for these literal
three-target operators. Five terms can have ranks (4,4), so this rank-three
classification does not settle them. A different partition also needs a new
geometric check of both residual families. Shared physical calls, changed
fitting matrices and masked or nonlinear contracts are outside the theorem.
Source acquisition, coefficient execution, frames, dirty restoration,
ownership, hosting, stock, precision, all-size/compiler, physical consumers,
complete supplier invoices and multiplication transfer remain unproved.

The classification and representation criterion inherit Nick Petalas's
PR3513 and PR3505. The fixed VVV family inherits PR3527 and PR3515. The literal
partition retains Tekalign's PR3370 credit. The expanded-identity argument
retains Philippe Van Velzen and Arham Tahir's PR3345 credit, with the broader
P112/E8 and native/compiler/supplier lineage in the pinned predecessor sources.
All inherited proof premises are declared live source inputs. Comparison-only
public context does not replace any premise. No frozen predecessor is edited.
