# A common cut of 23 sites admits at most three rank-seven directions

## Model and statement

Let P be the 112 E8 root lines left after deleting the eight frame lines
in the pinned PR3163 fixture. Use the doubled integral representatives r_t
and their simple-root parity labels ell(t) in F2^9, with affine bit one.
The replay checks every root row against the canonical
`research/one-sided-six-multisets/data/data.txt`. Its label convention moves
the affine bit from bit 0 to bit 8; the invertible bit permutation is checked
on all 112 labels. This changes no binary support rank.

For a characteristic-zero field K, put

    c_h(t) = r_t dot h,
    C = {c_h : h in K^8},
    w(q) = rank_F2 {ell(t) : q(t) != 0},
    Off(h) = {t : c_h(t) != 0}.

The pairing is bilinear, including over C. The live-row Gram matrix is
112 I_8, checked exactly, so evaluation is injective over K.

**Common-cut theorem.** Fix ONE subset S of P with |S| <= 23. The nonzero
directions h satisfying

    rank_F2 ell(Off(h) outside S) <= 7

belong to at most three distinct projective lines. In particular, their
K-linear span has dimension at most three. The bound three is an upper
bound: attainment by three directions and sharpness of 23 are unclaimed.
A literal two-independent-direction fixture at 22 cuts is checked.

The proof uses the standard finite E8 Weyl-chamber theorem and exact finite
checks described below. It is not proof-kernel verification. The new result
is the combination of the root-restricted flat cap and fourfold overlap
with one common deletion set, and its named caller application. The E8 model,
Weyl reduction and earlier flat-cap lineage retain predecessor credit.

## 1. Completeness: qualifying directions are root normals

There are exactly 43,435 binary seven-spaces. Their live traces have maximum
size 36. The primary enumerates all two-dimensional annihilators by their
three nonzero functionals a,b,a XOR b, using a<b<a XOR b. The second checker
enumerates every two-row reduced row-echelon annihilator independently.
Both agree on the complete live-trace cardinality histogram.

A residual span of rank at most seven extends to one of these spaces. Thus

    |Off(h)| <= |S| + 36 <= 59.

At least 53 live root lines are perpendicular to h. For real h, move h to
the closed E8 Weyl chamber. Its perpendicular roots are the parabolic
subsystem on the vanishing simple-root coordinates. Every face with at most
six vanishing coordinates has at most 36 full root lines. The eight
seven-coordinate faces have counts

    42,28,22,14,16,23,37,63.

Only the last can contain 53 perpendicular live roots. Its normal is an E8
root direction. These chamber counts, its normal, and all 960 simple-root
reflection images are checked; the Weyl-chamber theorem itself is inherited.
Weyl transformations preserve the E8 root set, so every qualifying h is
proportional to one of the 120 rational root representatives.

For arbitrary characteristic-zero K, fix the rational root rows on which h
vanishes. Their rational nullspace N contains h after scalar extension.
Each of the remaining root rows gives a proper rational hyperplane in N:
otherwise it would also vanish on h. A finite union of proper rational
hyperplanes cannot cover N. Hence a rational vector has exactly the same
zero pattern. The real argument makes that nullspace one-dimensional, with
a rational root normal. Its scalar extension contains h. This proves the
same complete 120-line alphabet over K; no ordering of K is assumed.

This argument also yields code distance 53: any nonzero word of support
below 70 must have a root normal, and root-normal supports are 53 or 56.
The live rows themselves attain support 53. The replay checks that histogram.

## 2. Every admitted live root normal consumes at least 21 common sites

For each of the 120 root normals alpha and each of the 43,435 seven-spaces
G, the replay checks |Off(alpha) intersect Lambda(G)|. The maximum is
exactly 32 for EVERY root normal: 5,212,200 root/space pairs in total.

There are 112 live normals with |Off(alpha)|=53, and eight frame normals
with |Off(alpha)|=56. Therefore deletion to residual binary rank at most
seven needs at least 21 and 24 sites respectively. A qualifying direction
under |S|<=23 cannot be a frame normal, and satisfies

    |S intersect Off(alpha)| >= 21.

The 32 cap is a fresh exhaustive check of an earlier type of local capacity
bound, not a newly claimed root/label model. Both implementations reproduce
it using their separate geometry and seven-space enumeration.

## 3. Four distinct root normals share at most 14 live off-sites

The exact finite identity needed is

    max |Off(alpha_1) intersect ... intersect Off(alpha_4)| = 14,

over every four DISTINCT projective E8 root normals. No independence
restriction is needed. The primary checks all C(120,4)=8,214,570 quadruples.
The second reconstructs roots from the doubled E8 lattice shell, and joins
ordered pairs with a<b<c<d. Their COMPLETE intersection-size histograms agree.
RESULT.json includes all counts, an attaining quadruple, and its root rows.

Suppose four distinct projective directions qualify for one common S.
By section 1 they are root normals. Put A_i=S intersect Off(alpha_i).
Since |A_i|>=21 and every A_i is contained in that SAME S,

    |A_1 intersect A_2 intersect A_3 intersect A_4|
      >= sum_i |A_i| - 3|S|
      >= 84 - 3*23 = 15.

This contradicts the exact upper bound 14. Hence at most three projective
directions qualify. At the actual caller's budget 22, the lower bound is 18.
Per-direction cuts would not imply this inequality. The controls explicitly
exhibit four independent normals with individual 21-site cuts whose common
union has 66 sites; pooling them is rejected.

## 4. Excluding the named historical caller 2,3,4,4,7,7,7,7,7,7

Suppose ten K-linearly independent pieces span T, have these binary weight
bounds, and dim(T intersect C)>=6. Their first four supports have union S
with

    |S| <= 2+4+8+8 = 22.

These low-rank cardinality bounds follow directly from the distinct labels'
affine bit: a d-dimensional binary linear space meets that affine
hyperplane in at most 2^(d-1) points. No rank-five or rank-six census is used.

Write D=T intersect C. The quotient T/D has dimension at most four. The
four small pieces have independent quotient images. Otherwise a nonzero
linear combination would be a nonzero codeword supported on S, contradicting
distance 53. They are therefore a quotient basis; dim D=6.

Each of the six other pieces q_i has a unique combination a_i of the four
small pieces with c_i=q_i-a_i in C. These six c_i are independent, by their
coefficients on the six distinct q_i in the original independent-piece
basis. Evaluation supplies six independent directions h_i. Outside the ONE
common S, c_i agrees with q_i, so its residual binary support rank is at
most seven. The common-cut theorem permits at most three projective
directions. This contradiction excludes the named caller.

This result concerns the explicit independent-piece/code-intersection
hypotheses. Applying the historical TWOSIDE reduction to a physical decoder
continues to inherit that reduction's other premises.

## 5. Application audit and decision about normal planes

The source-bound PR3289 inventory conditionally covers 65 of its 69
historical (6,4) rows and lists four inventory-uncertified rows. The explicit
PR3322 contract excludes 2^3,7^7; the PR3405 contract excludes 2,5,6^8.
Those two theorems remain inherited conditional premises in this tally;
their heavy scientific replays are not claimed here. The new theorem
excludes 2,3,4^2,7^6. This NAMED contract inventory therefore accounts for
68/69 rows, leaving 4,5^3,6^6 uncertified BY THIS INVENTORY. This is neither
a current global unresolved count nor a proof that the last row is possible.

The PR3163 global two-six-flat/rank-seven/common-four question has different
hypotheses from this theorem. It is not settled here. For the named caller,
the actual small footprint already excludes normal planes before section 2.
For the other inventory row, its four-small-piece budget 8+12+12+12=44 and
rank-six endpoint cap 20 similarly give support<=64<70, hence root normals,
under those inherited capacities. Uniform normal-plane exclusion would not
close either of these caller gaps by itself. No all-first-space or global
normal-plane census is launched or claimed.

## Evidence boundaries and credit

The generic metadata/pin checks authenticate sources; they are not theorem
acceptance. The primary and separate mathematical implementations establish
the stated finite facts. The written arguments discharge the finite-to-
characteristic-zero implication and the caller composition, using the
explicit standard Weyl-chamber theorem. Same-session computational
corroboration is not independent human review or formal-kernel verification.

Credit DreamingOfClouds/PR3154 for C5, TWOSIDE and the FINITE lineage; Nick
Petalas/PR3160/3161/3163 for geometry, quantifier controls and the completed
slice; PR3282/3289 for the historical caller inventory and exact cover
contracts; PR3253/3322 and PR3397/3405 for the separate inherited exclusions;
and joaqcoo and the retained E8/P112/root-code lineage. All exact live pins
are at canonical main 20ecf2891d80b5acf18d980b2164fb44ea7faa90 in SOURCES.json.
New work is by Chris R / Clear1nsight with substantial OpenAI Codex
assistance, Apache-2.0. No complete C5, global decoder floor, physical
supplier, new kappa or selected-frontier change is claimed.
