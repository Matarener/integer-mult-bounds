# Excluding the literal P112 `2,5,6^8` caller

## Statement and inherited premises

Let K be a characteristic-zero field. On the literal 112 doubled E8 root
lines P, with the pinned leading-one binary labels ell(r), write

    C = {c_h = (r dot h)_(r in P) : h in K^8},
    w(q) = dim_F2 span {ell(r) : q(r) != 0}.

There do not exist ten K-linearly independent pieces s0,s1,q0,...,q7 of
weights at most 2,5,6,...,6 whose span T satisfies dim(T intersect C)>=6.
This is one literal historical caller exclusion. It is not full C5 or a
bound on every P112 decoder.

The proof inherits PR3397 at exact head
`10ac93be8dbf2ba5f85859dbeec90895ebbbabfd`. Its four-piece theorem says that
pieces of weights 2,5,6,6 span no nonzero codeword. Its support capacities
are 2,12,20 for weights 2,5,6, and the code distance is 53. That theorem and
its finite census are not independently reproved or replayed here. The
verbatim proof and receipt are retained as `predecessor-PROOF.md` and
`predecessor-RESULT.json`, authenticated by `PREDECESSORS.json`. Source
retention is not independent verification of those premises.

We also use the standard finite E8 Weyl-chamber theorem. The small finite
chamber and orbit facts needed below are checked anew. No proof kernel or
independent human review is claimed. The new conclusion is conditional on
these explicit premises.

## The quotient and its actual triple relations

Put D=T intersect C. By the inherited four-piece theorem, the quotient
images of s0,s1 and ANY TWO different qi are independent. Since dim(T/D)<=4,
its dimension is exactly four, dim D=6, and the small images span a plane.
In the further quotient by that plane, the eight qi give nonzero, pairwise
independent columns pi in K^2. Thus their projective endpoints are distinct.

For any triple i,j,k there is a unique projective relation among pi,pj,pk.
All three coefficients are nonzero. Lift it to T and subtract the unique
small-piece combination that makes its quotient image zero. This gives a
nonzero codeword c_ijk in D. The map from the six-dimensional relation
space ker[p0 ... p7] into D is an isomorphism. Indeed a zero lifted word
would contradict independence of the ten original pieces.

Consequently the normal h_ijk of c_ijk is nonzero. For any four endpoints
their four triple normals are pairwise different projective lines in one
two-dimensional normal space. For any five endpoints their triple normals
span three dimensions. These statements use the coefficient supports of
the relations and injectivity, rather than an assumption about rational
endpoint values.

Let S=supp(s0) union supp(s1), s=|S|<=14, and let
U=sum_i |supp(qi)|<=160. Every triple codeword is supported in S and the
three corresponding qi, so it has at most 14+3*20=74 nonzero sites.

## All triple normals belong to two finite Weyl orbits

The 1,200-direction completeness argument and support histogram already occur
in PR3253/3322, with PR3322 at `131605e644ec2aa78834d8707fe79bb05f44d169`
explicitly checking the same 38>37 threshold. They are rechecked here to
bind the new incidence and fifth-endpoint argument, not claimed as a new
classification. PREDECESSORS.json records that exact related proof.

A codeword with support at most 74 has at least 38 perpendicular live root
lines. The same roots are among the full 120 E8 lines. In a closed Weyl
chamber, a nonzero normal with at most six vanishing simple roots has at
most 36 perpendicular root lines. The eight seven-node faces have counts

    42,28,22,14,16,23,37,63.

Only the first and last reach 38. The last normal is a root direction.
The first is the D7 normal, represented in the retained coordinates by e8.
Its doubled-lattice representative 4e8 has norm squared 16, while the
retained doubled roots have norm squared 8. The Weyl orbits have 120 root
lines and 1,080 D7 lines. Thus every triple normal belongs to their union L
of 1,200 rational projective lines.

This argument also applies over K. The perpendicular rational roots have
rational rank seven. Rank at most six would allow a generic real normal
with those same roots perpendicular, contradicting the rank-six cap 36.
The resulting one-dimensional rational kernel makes the field-valued normal
proportional to a rational direction, to which the chamber argument applies.

For the literal frame, the D7 orbit's live support histogram is

    128 directions of support 70,
    896 directions of support 73,
     56 directions of support 76.

Hence every non-root triple has support at least 70. The 56 directions of
support 76 cannot actually occur here. We retain them in L for the finite
geometric exclusion, which therefore proves a stronger local lemma.
Root triples have support at least 53, including possible frame normals.

## Incidence forces at least nine root triples

There are 56 triples. At r outside S let k be the number of nonzero qi(r).
A triple with all three values zero has c_ijk(r)=0, because the small
pieces vanish there. Therefore at most

    f(k)=56-binomial(8-k,3)
        = 0,21,36,46,52,55,56,56,56  for k=0,...,8

triple codewords are nonzero at r. This upper bound permits all cancellations
and arbitrary endpoint coefficients. It needs no condition on nonzero
values. The elementary bound f(k)<=15k+6 gives total triple incidence

    I <= 56s + 15U + 6(112-s)
       <= 56*14 + 15*160 + 6*98
        = 3772.

The separate checker also obtains 3772 by an integer dynamic program over
all s=0,...,14 and U<=160. This is an incidence relaxation, not a constructed
caller.

If R of the 56 triples are root normals, distance gives

    I >= 53R+70(56-R) = 3920-17R.

Thus R>=ceil((3920-3772)/17)=9. If no two root triples shared an endpoint
pair, each of the eight endpoints would lie in at most floor(7/2)=3 root
triples, giving 3R<=24 and R<=8. There must be two root triples sharing a
pair of endpoints.

## The forced four-endpoint configuration

Call the shared endpoints 0,1 and the other two 2,3. Send their quotient
columns to p0=(0,1), p1=(1,0), p2=(1,t2), p3=(1,t3), with t2,t3 nonzero and
different. This uses a quotient basis change and nonzero piece rescaling;
it changes no supports. Let the lifted normals of triples 012 and 013 be
A*a and B*b, with a,b oriented doubled roots and A,B nonzero.

The other two triple normals are proportional to

    B*b-A*a,    t3*A*a-t2*B*b.

All four are distinct lines in span(a,b). The finite root-pencil check
establishes the following statements in L. For a nonorthogonal pair a,b,
the plane has only the three A2 root lines. For an orthogonal pair, it has
exactly a,b,a+b,a-b. The first case cannot contain our four lines. In the
second case B*b-A*a is a diagonal, forcing A/B=+1 or -1. Orient b to absorb
the sign, so A=B. The remaining diagonal then forces t3=-t2. Rescale p0
and divide the normal map by A. We have the normal form

    p0=(0,1), p1=(1,0), p2=(1,1), p3=(1,-1),
    h012=a, h013=b, with a dot b=0.

The Weyl action is transitive on all 30,240 ordered oriented orthogonal
root pairs. The replay checks this orbit, so it suffices to use

    a=(0,0,0,0,0,0,2,-2), b=(0,0,0,0,0,0,2,2).

The full set L is Weyl invariant. This transport does not assert that the
literal removed frame is invariant; the geometric lemma uses all of L.

## There is no fifth endpoint

A fifth endpoint has p4=(1,t), where t is not 0,1,-1. Write u=h014.
Injectivity of the relation map makes a,b,u independent. The other five
triple normal lines involving 4 are represented by

    u-t*a,  u+t*b,  u-a,  u-b,
    u-((t+1)/2)*a+((t-1)/2)*b.

All must belong to L. The first four already give a contradiction.

Here is the finite lemma and the completeness of its enumeration. Since
u and u-a lie on different rational lines v,w in L, the equation

    a=x*v+y*w

has unique rational coefficients, even when first considered over K.
Thus u=x*v or u=y*w for an unordered choice of v,w in a plane containing a.
The primary groups every line of L other than a by the exact exterior-product
key a wedge v. There are 378 groups with one member, 316 with two, and 63
with three. It checks every unordered pair and both assignments, discards
u in span(a,b), and requires u-b in L. Exactly 360 rational vectors remain.
The committed receipt binds their complete sorted set by SHA256.

For every remaining u, enumerate every v in L in span(u,a). Solving
v=x*u+y*a, x nonzero, gives the unique possible t=-y/x for u-t*a to lie
on v. After excluding t=0,1,-1, exactly 32 pairs (u,t) remain, all with t=2.
For example, the first candidate in sorted order is

    u=(-1,-1,-1,-1,-1,-1,3,-1), t=2.

Its second direction is proportional to (1,1,1,1,1,1,-7,-3), outside L.
For every one of the 32 candidates, u+t*b does not lie in L. Thus no fifth endpoint exists.
The last displayed triple relation is unnecessary for this contradiction.

The separate reconstruction does not import this shell generator, exterior
product, coefficient solver or enumeration. It generates the norm-eight and
norm-sixteen E8 shells directly from their integral coordinate patterns.
For each line outside span(a,b), it divides by the first nonzero coordinate
among positions 0,...,5. Lines with equal six-coordinate prefixes form a
section with only two free coordinates. Differences of those last coordinates
solve u-a and u-b directly. This independently yields the same 360 vectors,
32 first-pencil pairs, parameter t=2 and zero second-pencil survivors.
Both set digests agree. The implementations share input authentication and
receipt encoding, so this is separate computational corroboration, not an
independent human or formal proof.

## Conclusion and boundary

Incidence forces a pair of root triples sharing two endpoints. Their four
endpoints have the forced configuration, which admits no fifth endpoint.
The actual caller has eight distinct endpoints. This is the contradiction.

The theorem closes this literal independent-piece `2,5,6^8` obligation under
the inherited four-piece theorem/capacities and standard Weyl premise.
It does not establish any remaining-public-row count, full C5, C(P112)>=64,
physical decoding, dirty restoration, hosting, precision, consumer costs,
supplier admission, multiplication theorem or a new kappa. No selected record
is changed. The inherited multi-million-space census, historical heavy caller
suites, selected cold replay, Lean, Docker and human/proof-kernel review are
unrun in this session.

Credit Nick Petalas/PR3397/3295/3289/3161/3162 and the root-simplex geometry,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage. New material
is Apache-2.0. Automated assistance was used for research and implementation.
