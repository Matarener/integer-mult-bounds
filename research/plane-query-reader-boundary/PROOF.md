# One binary seed does not lower the actual reader bill

This is a scoped algebraic result. It fixes PR3370's literal rank-32 fitting
matrix K and complete-plane binary source-to-reader tariff. It supplies no
native COPY program, supplier admission or improved multiplication exponent.

## Contract and exact counterexample

Partition the 112 source labels into the retained even orthonormal groups G_g.
Pair consecutive ports within each group into complete Gram-I2 planes. The
literal queries are the indicators of the two alternating halves of each group.
Call these disjoint scalar vectors v_c. The literal matrix is

    K = sum_c v_c v_c^T.

There are 32 queries, and their full-plane ranks total 224. Let cl(v) include
both ports of every plane touched by a nonzero coefficient of v. For a term
u q^T in an exact decomposition of K, the actual declared charge is

    C(u,q) = rank_F2 Gram(cl(q), cl(u)).

The two arguments are source and actual reader. This is distinct from the
source self-Gram quantity

    S(q) = rank_F2 Gram(cl(q), cl(q)).

The two quantities agree for the literal indicator terms. They need not agree
for an external query. PR3383's theorem explicitly fixed S and its row-space
restriction. Nothing here contradicts that theorem.

CERTIFICATE.json replaces six disjoint pairs of literal queries. Let a and b
be one alternating half from the two listed groups, and let z indicate the
listed seed ports. Repeat after swapping each port with its plane partner.
For group pairs (1,11) and (3,14), use

    q = (z, a-z, b-z),       a = q_0+q_1, b = q_0+q_2.

For (5,6), use

    q = (a-z, z, a+b-z),     a = q_0+q_1, b = q_2-q_0.

All identities have integer coefficients and hold over every field. The seed
lists are respectively (58,9), (46,49), and (11,19,39,72). The remaining twenty
literal queries stay unchanged. Thus 38 signed queries realize the SAME K.
Each seed is nonconstant on a literal half, so these queries leave the old
literal row space. The old fixed-rowspace theorem does not cover them.

On each side of either first pair, the source self-ranks are (2,7,4), while the
actual reader ranks are (4,8,6). On either side of the last pair they are
(3,6,6) and (4,7,7). Consequently

    source self-Gram total = 218,
    actual source/reader total = 244,
    unchanged literal baseline = 224.

The actual histogram is twelve rank-4, four rank-6, four rank-7 and eighteen
rank-8 terms. This is a counterexample to substituting S for C outside the
literal row space. It is a failed cost-improvement hypothesis, even though the
scalar identity succeeds. No claim that 244 is the best outside-rowspace bill
is made.

## Precisely bounded replacement family

Choose any two different literal queries a,b. They may come from the same
group. Choose any zero-one seed vector z supported on the union of their complete
groups. The seven canonical signed directions are

    a, b, a+b, z, a-z, b-z, a+b-z.

Take any three whose formal coefficient matrix in (a,b,z) is nonsingular, and
recover a,b by that matrix's inverse. A query with zero reader is charged zero.
The theorem is that no replacement in this family costs less than the original
two queries. Hence applying any disjoint collection of these replacements cannot
lower the total 224.

This includes all binary bases of one-extra-dimension query spaces in
characteristic two, and the 29 specified rational lifts when the determinant is
invertible. It does not include arbitrary rational three-query directions,
multiple external seed dimensions, a different fitting matrix or a changed
physical contract. If z already lies in the binary span of a,b, the binary case
is a recoding inside the old row space and the original rank bound applies.

## Unimodular cases

Of the 35 three-element subsets of the seven directions, six formal matrices
are singular, 28 have determinant +1 or -1, and exactly one has determinant
of absolute value two. Direct symbolic inversion checks that the first two
rows of every unimodular inverse have entries only -1,0,1. The zero-one seed,
disjoint a,b and canonical signed directions give query entries only -1,0,1.
Thus both supports are unchanged over every coefficient field.

We recall and apply the retained integral full-port rank floor. Index a binary
expanded operator by (p,s), where p is a scalar port and s is either of its
plane's two basis labels. Replace each scalar entry K_pq by K_pq times the
2-by-2 binary pairing block of those complete planes. The expanded literal K
is I_224. Its diagonal blocks are I2; nonzero off-diagonal scalar entries join
orthogonal planes in one group and therefore have zero binary blocks.

Any integral factorization K = sum u q^T reduces modulo two. Each expanded
term factors through the rectangular complete-plane pairing matrix between
its touched source and reader planes. Its binary rank is at most C(u,q).
Repeated plane occurrences and zero reduced coefficients cannot increase this
rank. Subadditivity gives

    224 = rank(I_224) <= sum_terms C(u,q).

This is the previously retained integral expanded-identity argument, not a new
unrestricted fractional-decoder lower bound. For a unimodular replacement, add
back all unchanged literal terms. Their charge is 224 minus the original
pair's charge. The inequality forces the replacement to cost at least that
pair. Because the supports are field-independent, this charge conclusion and
the integral identity hold over every field, including characteristic two.

## The unique half-integral case

The remaining nonsingular triple is

    q_1 = a+b, q_2 = a-z, q_3 = b-z,
    a = (q_1+q_2-q_3)/2, b = (q_1-q_2+q_3)/2.

It requires two to be invertible in the coefficient field. It is not an
invertible formal basis in characteristic two, and the integral reduction
argument cannot be applied to its halves.

All three readers touch both a and b. Their complete reader closure is G, the
union of the relevant complete groups. Write r = rank_F2 Gram(G,G). The first
query touches every plane of G, so it costs r. Since q_2-q_3 = a-b touches
every plane of G, the other two source closures together contain G. Row-rank
subadditivity therefore gives

    C(u_2,q_2) + C(u_3,q_3) >= r.

If the original group sizes are m_a and m_b, a contained identity principal
minor proves r >= max(m_a,m_b). For the same-group case both sizes are that
group's size. Thus the total is at least

    2r >= m_a+m_b,

which is exactly the original pair's charge. This proves the remaining case
without pretending that half coefficients reduce modulo two.

## Source binding and checks

The primary checker authenticates canonical selected labels and the unchanged
retained PR3370 certificate. It checks all 12,544 integer UQ=K entries, all
11,392 forced strict-mask entries and all 50,176 expanded binary entries.
The 35 formal triples are classified by integer determinants and exact inverse
identities. All 496 literal query pairs satisfy the contained-identity and
half-integral bound. Every one of the 38 term invoices records both complete
closures, rather than silently identifying them.

The separate checker imports no primary code. It reconstructs a sparse
integer operator, uses explicit nine-coordinate labels and dense binary
elimination, verifies all 224 source and additive dirty-target columns, and
classifies the 35 triples by rational elimination. This is separately
implemented author verification, not independent human or formal-kernel review.
The written rank argument supplies universal seed coverage. No extrapolation
from a finite random sample is used.

Native acquisition, coefficient implementation, physical frame transport,
private scratch restoration, hosting/storage, precision/tape, all-size
compilation, both suppliers and outer multiplication transfer remain outside
this result. Preserving arbitrary additive target inputs in the algebraic
check is not a native private-workspace restoration certificate.
