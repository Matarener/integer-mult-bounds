# A common binary span forces the four-term triple floor

## Statement

Partition finitely many indexed binary labels into positive even groups. Each
group has binary Gram matrix I. Pair consecutive ports of each group into
planes. Its alternating halves define two scalar indicators. Choose three
distinct indicators a,b,c. Their scalar supports are disjoint. Write G_A,G_B,G_C
for the complete groups, with sizes d,d,e. Assume

    span_F2(G_A) = span_F2(G_B) = V,       e <= d.

The two groups may be the same group, with a,b its complementary halves.
G_C may have directions outside V. Cross-group pairings are unrestricted.
Indexed labels in different groups need not be distinct.

For a scalar vector x, cl(x) contains both ports of every plane touched by its
support. The actual-reader tariff of a term is

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Over every coefficient field F, every exact identity with t <= 4 terms

    aa^T + bb^T + cc^T = sum_i u_i q_i^T

has sum_i C(u_i,q_i) >= 2d+e. Both factors may have arbitrary ambient values,
external directions, zero terms, repeated rays and cancellations. The three
original terms attain the floor.

The new ingredient is a geometric bound of 3d for each of the two residual
non-Fano families in characteristic other than two. If e<d, those families
lose by at least d-e. This replaces a literal finite geometry check by an
all-dimension argument under the common-span hypothesis. It does not establish
a floor for arbitrary different group spans or improve a supplier or kappa.
The proof is author-checked. Independent human and formal proof-kernel review
are unclaimed.

## Reduce arbitrary four terms to two residual families

The algebraic reduction is inherited from PR3538, whose exact proof bytes are
retained locally. Its finite P112 census is not used here. The classification
and support-transfer premises below are pinned canonical sources, including
their proofs and runtime inputs.

Let U,Q have the t readers and queries as columns. The target T has rank three.
Restrict U to im(Q^T). Its kernel there has dimension at most t-rank(U), so

    rank(U)+rank(Q) <= t+3 <= 7.

Both ranks are at least three. Transpose the symmetric target if necessary.
This transposes every binary tariff matrix and preserves its rank. We may
therefore assume rank(Q)=3 and span(Q)=span(a,b,c).

The seven-point classification in the pinned PR3513 proof applies to the at
most seven indexed columns q_1,...,q_t,a,b,c. Twenty-two simple rank-three types
admit characteristic-two representations. One is non-Fano. Zeros and parallel
copies can be removed and restored. A rank-three configuration with fewer than
seven simple points can first be extended by generic points over an infinite
field extension. Each new point avoids every old pair-line, so the resulting
seven-point configuration is not non-Fano. Deleting the added points gives
the needed characteristic-two representation. The registered replay reruns
both canonical classification implementations, rather than assuming the table
is exhaustive from its successful representation checks alone.

For the represented types, the pinned PR3505 support-transfer lemma preserves
every source zero and every reader's target-span request. It constructs the
same literal target operator in characteristic two with termwise smaller
supports. To see why its bill is at least 2d+e, replace scalar entry M_pr by
M_pr times the 2-by-2 binary Gram block of the planes at p,r. The expansion of
T is diagonal, with two ones per selected indicator port. Its rank is 2d+e.
An expanded rank-one scalar term factors through its complete-plane Gram
matrix and has rank at most C(u,q). Rank subadditivity proves the bound. This
also treats an original coefficient field of characteristic two directly.
The expansion method retains Philippe Van Velzen and Arham Tahir/PR3345 credit.

For the non-Fano type use points E,F,G,E+F,E+G,F+G,E+F+G, with the six lines
013,024,056,125,146,236. The complete quadrangle on 0,1,2,6 has 24 automorphisms.
Its 29 independent target triples have four orbits, represented by

    012, 014, 034, 345, with sizes 4,12,12,1.

For the two middle orbits the normalized query columns and characteristic-two
replacements are:

| Marks | Old columns | Binary columns |
| --- | --- | --- |
| 014 | (-1,0,1), (1,1,0), (-1,1,1), (0,1,1) | (1,0,1), (1,1,0), (1,1,1), (0,1,1) |
| 034 | (-1,1,0), (-1,0,1), (-2,1,1), (-1,1,1) | (1,1,0), (1,0,1), (0,1,1), (1,1,1) |

Each binary column's support is contained in the old support. For every query
subset and each marked target, every old target-span request remains true.
There are 14 and 15 true requests among 96 candidates. verify.py checks these
implications over Q and F2. Thus every actual reader port can choose binary
coefficients on its original active terms, giving the same support-shrinking
characteristic-two identity and tariff floor. These are selective maps, not
representations of the full non-Fano matroid.

The quadrangle incidences determine every representation projectively: send
three vertices to the axes, scale the fourth to (1,1,1), and intersect opposite
sides to obtain the other points. This is possible precisely when 2 is
invertible. Independent target and query scalings cause no restriction. If
q_i=t_i sum_j N_ji a_j/s_j, let D scale target j's ports by s_j. Then

    q'_i=D q_i/t_i,       u'_i=t_i D^(-1)u_i.

The transformed operator is D^(-1)TD=T and both supports are unchanged.
Therefore the two remaining marked orbits have these normalized exact forms:

    VVV queries: a+b, a+c, b+c, a+b+c
    2u: a+b-c-w, a-b+c-w, -a+b+c-w, 2w

    MMM queries: a+b-c, a-b+c, -a+b+c, a+b+c
    2u: a+b-v, a+c-v, b+c-v, v.

Here w and v are arbitrary ambient vectors. Direct substitution proves each
identity, and solving the three target-coordinate equations proves these
are all readers for the four queries. The new geometric lemma applies to
both forms.

## Shrink readers and identify their zero spaces

In VVV replace w at each selected target port by one of 0,+1,-1. These are
distinct in every field under consideration. Every other value makes all four
reader entries nonzero, so replacing it by zero shrinks supports. In MMM use
v=0 or v=1 at each selected target port. Every other value again activates all
four readers. Outside the targets set the parameter to zero. Each change
preserves the exact affine identity and shrinks supports term by term.

At an A port the VVV support patterns, in term order 1,2,3,4, are
1110,0011,1101 for values 0,+1,-1. At a B port they are 1110,0101,1011.
The MMM A patterns are 1100,0011 and the B patterns are 1010,0101. A target
contains exactly one port of each plane of its group. Consequently its
parameter values partition the complete binary basis G_A or G_B into unions
of planes.

For MMM let A_0,A_1 be the spans of G_A's planes with parameter 0,1. Define
B_0,B_1 similarly. Each is an orthogonal direct-sum decomposition of V. For
VVV use A_0,A_+,A_- and B_0,B_+,B_-. Empty summands are allowed.

Every query closure in either family contains V. In VVV each query contains
at least one of the two full common-span target groups. In MMM each contains
both. For reader i define the binary subspace

    K_i = {x in V : x is orthogonal to every label in cl(u_i)}.

Rank-nullity gives rank Gram(V,cl(u_i))=d-dim(K_i). Since V is contained in
the query span, this rank is at most the actual tariff. The A and B reader
supports force the following inclusions:

| Family | K_1 | K_2 | K_3 | K_4 |
| --- | --- | --- | --- | --- |
| MMM | A_1 intersect B_1 | A_1 intersect B_0 | A_0 intersect B_1 | A_0 intersect B_0 |
| VVV | A_+ intersect B_+ | A_+ intersect B_- | A_- intersect B_+ | A_0 intersect B_0 |

The complete group Gram matrices are I, so orthogonality to every nonzero
reader plane is exactly membership in the complementary coordinate summand.
These are necessary inclusions. C's labels, external readers, and an active
plane mate can only impose more orthogonality conditions. This also handles
a,b from complementary halves of the same group.

## Distinct joint atoms form a direct sum

Let V have any two finite direct-sum decompositions V=sum_r A_r=sum_s B_s.
Take any distinct pairs (r_i,s_i). The subspaces A_(r_i) intersect B_(s_i)
form a direct sum. Indeed, given a relation sum_i x_i=0, project onto A_r.
Only terms with r_i=r remain. Then project that relation onto each B_s.
The pairs are distinct, so only one term remains and it must be zero.
The two projection families need not commute on all of V.

All four pairs in each row of the table are distinct. Therefore the actual
K_i also form a direct sum and sum_i dim(K_i)<=d. It follows that

    sum_i C(u_i,q_i)
      >= sum_i (d-dim(K_i))
      >= 4d-d
       = 3d
      >= 2d+e.

Support shrinking cannot increase tariffs, so the same inequality holds
before specialization and for arbitrary ambient readers. Together with the
represented and selectively transferred cases this proves the stated sharp
four-term triple floor. Each original indicator term has tariff equal to its
complete group's size, so 2d+e is attained.

## Evidence and boundary

The new primary and separate raw-Gram implementation exhaust eight fixtures,
including dimensions 2,4,6, noncommuting coordinate decompositions, equal and
smaller third groups, external third-group directions, and complementary
halves. They compare every four-charge stream and histogram. A separate
set-sum injection checks every joint-atom assignment; the primary uses rank
elimination. These finite replays check the implementation and examples, not
an exhaustive enumeration of the theorem's unbounded dimensions. The proof
above supplies that quantifier. RESULT.json gives exact counts and hashes.

The earlier scratch probe is not evidence for a general-partition theorem.
Its initial projected-rank width bug was discarded; its corrected bounded
random sample found no saving. Neither sample enters acceptance or this proof.
The canonical classifier is rerun on its exact pinned bytes. PR3538's literal
censuses are not rerun or needed by this common-span argument.

The common-span premise is essential to this proof's decompositions of V.
No assertion is made that it is necessary for the actual tariff floor.
Different group spans, five terms, other target blocks, changed closure or
masked identities and nonadditive physical sharing remain open. Native
acquisition, scalar execution, frames, dirty restoration, hosting, stock,
precision, all-size/compiler admission, full paid suppliers and outer
multiplication transfer are not supplied. The selected frontier is unchanged.

Credit retains Nick Petalas/PR3538, PR3513, PR3505 and PR3527, Philippe Van
Velzen and Arham Tahir/PR3345, Tekalign/PR3370 and the P112/E8/native/compiler
lineage in the pinned proofs. No frozen predecessor has been edited.
