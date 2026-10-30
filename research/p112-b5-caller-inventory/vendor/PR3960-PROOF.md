# A common24 rank-seven bound and two literal C5 callers

Fix the 120 doubled E8 root lines R, oriented by first nonzero coordinate,
the eight frame lines F = {2e_0 +/- 2e_1,...,2e_6 +/- 2e_7}, and P=R\F.
The original caller table orders P lexicographically. Its labels are
ell(r)=(1,c(r) mod2) in F2^9, where c(r) are the integral simple coordinates
in the pinned simple system. Binary weight means the rank of the actual
support labels, not the number of support sites.

For a characteristic-zero field K put C={c_h : h in K^8}, where
c_h(r)=r dot h for r in P. Let Off(h) be its nonzero support.

**Theorem.** For every ONE fixed S subset P of size at most 24, the nonzero
directions h with

    rank_F2 ell(Off(h)\S) <= 7

occupy at most TWO projective lines over K. Their K-linear span has
dimension at most two. A literal independent pair at a cut of size 24
attains two. Sharpness of the cut allowance 24 is not claimed.

**Caller corollary.** Eleven collectively independent pieces with binary
weight bounds either

    2,2,2,2,3,5,7,7,7,7,7
    2,2,2,2,4,4,7,7,7,7,7

cannot have dim(span(pieces) intersect C)>=5. These are two actual historical
TWOSIDE (b,t)=(5,6) profiles, each with strict excess deficit one. This is a
scoped exclusion, not the full cell, C5, a decoder floor, supplier admission
or a new kappa.

## 1. Complete finite spaces and the root-normal reduction

The primary reconstructs the 112 original table rows and adds exactly F.
It checks the elementary 56 two-coordinate and 64 all-odd E8 line patterns,
the nonsingular simple system, every exact coordinate reconstruction, uniform
simple-coordinate signs and the original 112 label bindings. The live Gram
matrix is 112 I_8. Evaluation is therefore injective over every characteristic-
zero K. The binary labels all have leading bit one.

Every seven-space is the kernel of a unique two-dimensional annihilator
in reduced row-echelon form. The reversed-column enumeration chooses its
highest pivots and all free nonpivot entries below each pivot. Uniqueness of
RREF proves coverage and nonduplication. All 43,435 spaces are enumerated;
their full-root trace maximum is 36. Smaller residual spans extend to a
seven-space. Consequently a qualifying direction has

    |Off(h)| <= |S|+36 <= 60 < 70.

Here is the needed chamber statement, including the field step. The checked
eight simple reflections permute all 240 signed roots (1,920 images). Since
these roots span, their generated group acts faithfully on a finite set and
is finite. The checked rational rho satisfies rho dot alpha_i=1. For a real
normal v maximize rho dot g(v) over this finite group. If g(v) dot alpha_i<0,
reflecting in alpha_i strictly increases that functional, a contradiction.
Thus g(v) is in the closed chamber. Uniform signs of the simple coordinates
imply that a root is perpendicular exactly when its simple support lies in
the zero simple pairings. The perpendicular roots are therefore a checked
simple face. This argument classifies full-root zero systems; no move is
assumed to preserve the removed frame or live support labels.

The largest face on at most six simple nodes has 36 full root lines. The
seven-node face counts are 42,28,22,14,16,23,37,63. The last face has a single
normal root line. If the rational span Z of the live roots perpendicular to
a qualifying K-normal had rank at most six, choose a generic real normal
to Z avoiding all other root hyperplanes. Such a choice exists because a
finite union of proper hyperplanes cannot cover a real vector space. Its
perpendicular roots span Z, so its chamber face has rank at most six.
But it has at least 112-60=52 perpendicular live roots, contradicting 36.

Thus Z has rational rank seven. Rational minors and Gaussian elimination
preserve this rank over any characteristic-zero K; its one-dimensional
rational kernel extends to the kernel over K and contains h. A rational
generator is real and has at least 52 perpendicular roots. Of the listed
seven-node faces only the 63-line face can occur. Its normal is a root,
and inverse reflection transport preserves the signed root set. Therefore
h is a K-scalar multiple of one of the 120 rational root normals. No embedding
of K into R or C is assumed. Direct evaluation gives support 53 for each
of the 112 live normals and 56 for each of the eight frame normals.

## 2. Exact completion cuts, including frame normals

For each root normal a and every binary seven-space V define

    C(a,V) = Off(a)\Lambda(V),

where Lambda(V) is the live root trace of V. A normal qualifies under S
exactly when C(a,V) subset S for some V. This includes arbitrary partial
supports: extend their residual binary span to a seven-space. The primary
tests all 120*43,435=5,212,200 normal/space pairs. The root-word trace maximum
is 32. The complete records with |C(a,V)|<=24 are:

| Normal type | Cut size | Records |
|---|---:|---:|
| Live | 21 | 336 |
| Live | 23 | 5,376 |
| Frame | 24 | 504 |

There are 6,216 records and 6,188 distinct cuts. There are no other cut
sizes at most 24. Each of the 336 size-21 cuts has exactly one record,
hence one normal owner. Retaining frame normals is necessary at size 24.
Complete sorted record and flat-multiplicity digests, not just maxima, are
reconstructed and compared in RESULT.json.

## 3. Why the finite common-cut test covers every S

Make a graph on the 336 size-21 cuts, joining two distinct cuts when their
union has size at most 24. Exact comparison of every pair gives 168 edges,
each vertex of degree one: the graph is a perfect matching. Therefore no
set S of size at most 24 can contain three distinct size-21 cuts. Since
these cuts have single owners, they admit at most two normal directions.

To cover any remaining possibility, enumerate all size-23 and size-24 cuts,
and all unions of one size-23 cut with any completion cut whenever the union
has size at most 24. These give exactly 8,540 candidate sets:

| Size | Admitted normal directions | Candidate sets |
|---:|---:|---:|
| 23 | 1 | 5,376 |
| 24 | 1 | 448 |
| 24 | 2 | 2,716 |

Suppose S admitted at least three distinct normals. Select one contained
completion cut for each. They cannot all have size 21 by the matching.
If a selected cut has size 24, it equals S and is a candidate. Otherwise
a selected cut B has size 23. If all selected cuts lie in B, B already
admits the normals and is a candidate. If some selected cut T does not
lie in B, then B union T has size 24, equals S, and is an enumerated
candidate. All cases contradict the table's maximum two. Arbitrary unused
sites in S do not invalidate this argument. It does not replace one common
cut by separately chosen cuts for different directions.

The theorem follows over every characteristic-zero K because section 1
reduces all directions to rational root lines. The pair witness lists the
actual live labels, root normals, seven-space trace masks and a positive
Gram determinant. Direct residual-label ranks verify its attainment.

## 4. Two different literal caller bindings

Let T be the span of either eleven-piece list in the corollary, with
D=T intersect C and dim D>=5. The quotient T/D has dimension at most six.
The first six pieces have support-cap sums

    4*2+4+12=24,       4*2+8+8=24.

Ranks two, three and four permit at most 2,4,8 leading-one points. The
rank-five capacity 12 is Nick Petalas's prior bound and is independently
rechecked on all 3,309,747 binary five-spaces here. Since 24<53, every
nonzero combination of these six independent pieces has support below
the code distance and cannot be a codeword. Their quotient images are
independent, so the quotient dimension is exactly six and dim D is exactly
five. Let S be their ONE actual support union, of size at most 24.

For each of the five remaining weight-seven pieces q_y there is a unique
a_y in the six-piece span with c_y=q_y-a_y in C. These five codewords are
independent: their coefficients on the five distinct nonbasis pieces are
the identity matrix in the original independent piece basis. Injective
evaluation gives five independent h_y. Outside S their supports are subsets
of support(q_y), of binary rank at most seven. The theorem allows at most
two projective directions, contradicting five independent directions.
Coefficients, overlaps and cancellations are unrestricted over K.

The pinned PR3154 filter is retained in canonical main by PR3282. Both
literal lists satisfy its necessary conditions and have
sum(w-2)=29<30. No failed sufficient filter is interpreted as a construction.
This proof does not assert that the two lists were the only publicly open
profiles or that (5,6) is closed.

## 5. Independent implementation, predecessor credit and limits

The primary uses the table model adapted from this donor's PR3951 and a
reversed-column annihilator enumeration. The separate checker imports no
primary or predecessor executable. It constructs the E8 shell, uses Cramer's
rule with integer Bareiss determinants for the labels, and enumerates all
10,795 binary six-spaces in F2^8 and their four affine cosets. These 43,180
affine sections, plus 255 leading-zero seven-spaces, reproduce the entire
flat-multiplicity inventory and every critical record.

Its common-cut composition uses different joins: size-23 cuts sharing a
22-subset, and size-23/21 pairs sharing a 20-subset. Admission is checked by
looking up the candidate's 21-,23- and24-subsets. Complete candidate/admission
digests agree with the primary union and per-normal containment loops.
This is computational corroboration in the same author/assistant context,
not independent human or formal-kernel acceptance.

Credit Nick Petalas for the retained global capacities, root geometry,
root-shortening and shared-cut predecessors, including PR3163/3282/3289;
DreamingOfClouds/PR3154 for TWOSIDE and C5, David Arias for the quadratic model,
joaqcoo and the retained E8/P112 lineage. PR3931 already supplies a common23
bound of three and a different caller; its adjacent 2^3,3,5,7^5 application
requires only cut22 and is not a new geometric theorem here. PR3951 supplies
the previous dependency audit and chamber/field argument. The new result is
the common24 bound and these two caller applications. The donor's adapted
model is credited, not presented as newly independent relative to PR3951.

No full C5, complete decoder reduction, physical/supplier or multiplication
theorem, selected cold replay, new kappa, independent human review or formal
proof-kernel verification follows. Frozen predecessors and the selected
record remain unchanged. New work: Chris R / Clear1nsight, with substantial
OpenAI Codex assistance, Apache-2.0.
