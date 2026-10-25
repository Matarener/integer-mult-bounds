# A literal common-cut 36 counterexample for mixed 5,6,6

Let R be the fixed 112 nonframe E8 root lines with the canonical leading-one
nine-bit labels. Over a characteristic-zero field K, let

    C = {(r dot h)_(r in R) : h in K^8}.

A vector's binary support rank is the F2 rank of the labels at its nonzero
coordinates. Deletion pi_S removes ONE common set S from every vector.

Theorem. There is an explicit set S of 36 live coordinates and three
residual vectors q1,q2,q3 of binary support ranks exactly 5,6,6 such that

    dim_K(pi_S(C) intersect span_K(q1,q2,q3)) = 2.

This refutes the universal common-cut 36 extension proposed as an open
question by PR3368. Combined with that predecessor's conditional theorem,
its sufficient bound 35 is optimal under its inherited premises. The present
counterexample itself does not assume its capacities, concentration, Weyl
normalization or any native/physical contract.

## Exact construction

Use the doubled integer roots and simple-root convention of the pinned
geometry.py. Number the sorted 120 full root lines from zero. WITNESS.json
uses these full-root indices throughout, including its cut and supports.
The eight frame roots are excluded before any support or cut is formed.

The two normal roots, with full indices 2 and 13, are

    a = (0,0,0,0,0,2,-2,0),
    b = (0,0,0,2,0,-2,0,0).

They have squared norms eight and inner product minus four, so they span an
A2 root plane. Their evaluation pairs have a 78-coordinate nonzero union
U on the literal P112. The remaining 34 live coordinates annihilate both.

Choose the following three disjoint subsets of the large projective fibers.
The brackets contain full-root indices, not positions in the 112-point list.

    A1 = [12,19,31,40,54,61,82,97,108,117],
    A2 = [3,4,22,27,33,38,44,55,60,71,76,87,92,103,110,115],
    A3 = [7,10,23,26,34,37,47,56,59,68,75,84,95,104,111,114].

On these sets the evaluation pairs lie respectively on the lines
(0,1), (1,-1), (1,0). Their leading-one label ranks are respectively
5,6,6. All three sets avoid the eight frame roots. The certificate lists
all values, all 36 cut sites and all support sites explicitly.

Set A=A1 union A2 union A3 and S=U minus A. Thus |A|=42, |S|=36,
and the retained coordinate set R minus S has size 76. Define q1 on A1
by q1(r)=r dot b. Define q2 on A2 and q3 on A3 by q_i(r)=r dot a.
Set each vector to zero on all other retained coordinates. Every listed
nonzero value is plus or minus four. Consequently

    pi_S(c_a) = q2 + q3,
    pi_S(c_b) = q1 - q2.

These are identities on all 76 retained coordinates, including the 34
coordinates outside U. Their coefficient columns are fixed globally;
there is no site-dependent change of coefficients. The two codewords are
independent because A1 and A3 are nonempty with distinct evaluation lines.
Thus the claimed intersection has dimension at least two.

## Exact dimension and characteristic-zero transfer

The 76-by-8 restricted root matrix has rational rank eight. The 76-by-3
piece matrix has rank three, since its nonzero supports are disjoint.
Their concatenation has rank nine. The dimension formula gives

    dim(intersection) = 8+3-9 = 2.

The primary verifier performs exact rational elimination. The separate
checker instead imposes 73 integer linear constraints on h. Outside A,
r dot h must vanish. Inside a piece, evaluation divided by its nonzero
piece value must be constant. These constraints have rank six in eight
variables, and the restricted root matrix is injective. They therefore
give the same intersection dimension two without using the concatenated
matrix calculation. All matrices have rational entries. Their nonzero
minors and exact dependencies persist over every characteristic-zero
field, so the result is not restricted to real or rational coefficients.

## Reconstruction, evidence and scope

construct.py fixes this A2 plane and checks reduced-echelon annihilators
inside each seven-dimensional binary large-fiber span. It selects the
first live sections of sizes 10,16,16 and regenerates WITNESS.json exactly.
There are at most 2,667 rank-five and 127 rank-six candidates per fiber.
This is a bounded witness construction, not an optimization or exhaustive
classification of all counterexamples.

crosscheck.py independently constructs the 120 roots, inverts the simple
root matrix once, and rebuilds the labels. It imports neither geometry.py
nor the primary checker. Both methods use the same specified E8 convention
and the same literal certificate. Their agreement is internal computational
corroboration, not independent human or proof-kernel review.

PR3368's proof is retained verbatim only to explain the next-cut question
and conditional lower threshold. No executable predecessor package or
unmerged Git-history object is required for replay. SOURCES.json binds the
only external mathematical input, the canonical geometry source.

This is an actual coefficient-realizable support/code counterexample, not
an equality relaxation or failed search. It does not refute cut35, exclude
an actual decoder caller, settle full C5, provide a native/physical program,
price restoration or a consumer, admit a supplier, change the selected
frontier, or improve kappa. Those claims need their own contracts and proof.

Credit Nick Petalas's PR3368 and the retained PR3353/3325/3299/3295/3324/3292,
sharp A2 incidence20, PR3278/3269/3267/3260/3262, David Arias's quadratic
model, DreamingOfClouds/PR3154, joaqcoo and the E8/P112/root-simplex lineage.
New work and the retained proof are Apache-2.0.
