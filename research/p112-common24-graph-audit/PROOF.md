# Independent graph audit of the common24 application

This audits PR3960 at `7e8d98e351ac153d81943218bf168dc8548b1cea`.
It finds no mathematical defect in the stated theorem or the two transfers.
The new finite result is stronger structure of the **complete colored
completion graph**: it is a matching with 2,884 edges and 448 isolated vertices.
This gives an alternative proof of the common-cut coverage step. It does not
establish independent human review or formal-kernel verification.

## 1. Exactly which finite objects are checked

Write R for the 120 oriented doubled E8 root lines, F for the eight frame
lines `2e_0 +/- 2e_1,...,2e_6 +/- 2e_7`, and P=R\F. The live table and simple
system are canonical-main inputs. A fresh rational Gauss-Jordan calculation
recovers integral simple coordinates and the original labels
`ell(r)=(1,c(r) mod 2)` in F2^9. The verifier checks the full E8 shell, original
row-label binding, distinct labels and live Gram matrix `112 I_8`. No
predecessor executable is imported.

A two-dimensional binary annihilator has exactly three nonzero elements
`a,b,a+b`. Sort them. Its unique first two satisfy `a<b<a xor b`. Conversely
every such pair is independent and generates this two-space. Consequently the
nested nonzero-functional pair enumeration covers each annihilator exactly
once, hence each seven-space exactly once by the nondegenerate standard
pairing. It produces `511*510/6=43,435` seven-spaces. The verifier computes the
full-root trace mask of each. Their largest trace has 36 lines. Lower-rank
residual spans extend to seven-spaces.

For each of the 120 root normals a and each seven-space V compute

    C(a,V) = {r in P : r dot a != 0 and ell(r) not in V}.

All 5,212,200 pairs are visited. Retain every record with cut size at most24.
There are 6,216 such records, and exactly 6,216 distinct `(a,C)` vertices;
no inclusion-minimality reduction or representative discard is used. The
complete sorted record digest and the full-flat multiplicity digest match
PR3960. `REVIEWED.json` binds that comparison to the exact published target
and records hashes of the reviewed source/proof files. It is review provenance;
the replay does not fetch or import pending PR3960 files.

## 2. All-cut coverage by a matching

Color a vertex `(a,C)` by its projective root normal a. Join two vertices
of **different colors** exactly when their cuts have union size at most24.
The checker compares every unordered pair of the 6,216 vertices. Its result:

| Vertex degree | Number of vertices |
|---:|---:|
| 0 | 448 |
| 1 | 5,768 |

There are therefore 2,884 disjoint edges and no triangle. The checker also
independently checks triangle absence through adjacency-bitset intersections.
The matching property concerns the entire colored graph, including frame
normals and all cut sizes, rather than just the size21 subgraph used in PR3960.

Fix ONE S subset P with size at most24. Suppose three distinct root normals
qualify: their residual supports have binary rank at most7. Extend each
residual span to a seven-space V_i. Its complete cut C(a_i,V_i) is contained
in S, so the corresponding retained vertices exist. Their three different
colors and pairwise unions contained in S force a triangle. This contradicts
the graph result. Thus at most two root-normal directions qualify.

Only this implication is used. A triangle in the graph need not have total
three-cut union at most24; pairwise compatibility is a relaxation. The controls
include three singleton cuts with cutoff2: they form a triangle although
their total union has size3. Triangle **absence** remains a sufficient proof.
No assumption about unused sites of S, the relative cut sizes, or separate
cuts for different directions enters the implication.

An edge supplies an attaining pair: its union is an actual cut of at most24,
and the two root normals are independent. RESULT.json lists an explicit pair
and the actual cut labels. This corroborates attainment of two directions;
it does not prove sharpness of the permitted cut size24.

## 3. Audited characteristic-zero and distance implications

Here is the analytic bridge checked against PR3960, stated explicitly because
the graph enumerates rational root normals while the theorem quantifies over
all characteristic-zero fields K.

The verifier checks that the eight simple reflections permute the 240 signed
roots, and that the simple roots span. Hence the generated reflection group
is finite: its action on the roots is faithful. It also checks a rational
rho with `rho dot alpha_i=1`. For any real v, maximize `rho dot g(v)` over this
finite group. A negative simple pairing would be increased by its reflection,
so a maximizing vector lies in the closed chamber. The checked uniform signs
of each root's simple coordinates imply that its perpendicular roots are
exactly a simple face. The checked maximum face size on at most six nodes is
36, and the seven-node face counts are `42,28,22,14,16,23,37,63`; the 63-line
face has a root as its normal.

For nonzero h in K^8 with live support at most60, let Z be the rational span
of the live roots perpendicular to h. It cannot have rank8, because a nonzero
rational 8x8 minor stays nonzero over K. If its rank were at most6, a generic
real vector in Z-perp would avoid every root hyperplane not containing that
space. Its perpendicular roots would then be exactly the full roots lying
in Z, whose span is Z. Chamber transport would give a face of rank at most6,
contradicting the at least52 perpendicular live roots. Thus Z has rational
rank7. Its rational one-dimensional kernel extends to its kernel over K
by Gaussian elimination, so h is a K-multiple of a rational vector. The
corresponding real vector has at least52 perpendicular roots. Only the
63-line seven-node face can occur, making its normal a root; inverse
reflection transport preserves roots. The frame itself need not be preserved.
No embedding of K in R or C is used.

For a qualifying common24 h, the complete seven-space trace bound gives
`|Off(h)| <= 24+36=60`, so this bridge applies. Every such direction is one
of the 120 rational root lines already covered by the graph. They remain
distinct projective lines over K, since rational rank is preserved. At most
two projective lines imply span dimension at most2.

The same short-support bridge explicitly supplies the distance premise in
the caller transfer: if a nonzero codeword had support at most52, it would
be a root-normal word. Direct evaluation gives 53 live sites for each of
the112 live normals and56 for each of the eight frame normals, a contradiction.
Live normals attain53. Evaluation is injective over K because the live Gram
matrix is `112 I_8`, invertible in characteristic zero. Thus the code distance
is exactly53. This is an implication of the audited argument, not an extra
unproved distance assumption.

## 4. Coefficients and the two quotient transfers

Let eleven pieces p_1,...,p_11 be collectively K-linearly independent, T their
span, C the evaluation code, and D=T intersect C with dim D>=5. Assume the
binary ranks of their actual support labels are bounded respectively by

    2,2,2,2,3,5,7,7,7,7,7
    2,2,2,2,4,4,7,7,7,7,7.

Ranks2,3,4 give support caps2,4,8 because the labels lie in a leading-one
affine slice. The rank5 cap12 is **inherited from Nick Petalas's global
capacity theorem**, independently checked in PR3951; this audit does not
repeat its 3,309,747-space census. The first caller remains conditional on
that explicitly named dependency. Its six small pieces have capacity sum
`4*2+4+12=24`; the second has `4*2+8+8=24` and needs no rank5 capacity.
The original TWOSIDE status and necessary-filter membership are inherited
from PR3960 and PR3154/3282, rather than recounted as new inventory results.

Let A=span(p_1,...,p_6) and S the ONE actual union of their supports. Then
|S|<=24. Every element of A is supported in S, so distance53 gives A intersect
C=0. Since A has dimension6, its quotient image in T/D is independent. On
the other hand dim(T/D)<=11-5=6. Hence its dimension is exactly6, A maps
isomorphically to T/D, and dim D=5.

For each j=7,...,11 there is a unique a_j in A with c_j=p_j-a_j in D.
If sum(lambda_j*c_j)=0, expansion in the original independent p_i basis has
coefficient lambda_j on p_j for every j>=7. Thus all lambda_j vanish: the
five c_j are independent, regardless of the arbitrary coefficients of a_j,
intersections between supports, or cancellations inside S. Evaluation
injectivity gives five independent normals h_j. Outside S, c_j equals p_j,
so its residual label rank is at most7. The common24 bound limits their span
to dimension2, contradiction. This proves exactly these two transfers.

The executable receipt records graph facts and small caller arithmetic.
It does not turn this written coefficient argument into formal verification.

## 5. Scope, credit and remaining obligations

This is a fresh computational and written audit in the same donor/assistant
context as PR3960. It adds the complete matching certificate and a different
finite-space enumerator. It does not claim independent human acceptance,
a full C5 theorem, the full (5,6) cell, a decoder floor, supplier admission,
or a change to the selected kappa. The field proof rechecks and explains
PR3951/3960's argument; its underlying idea is credited there, not claimed
as new here.

Credit Nick Petalas for global capacities and the E8/root-shortening/shared-
cut predecessors, DreamingOfClouds for PR3154/TWOSIDE/C5, David Arias for the
quadratic model, joaqcoo and the retained E8/P112 lineage. The same donor's
PR3931, PR3951 and PR3960 retain their respective earlier results. New audit:
Chris R / Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0.
