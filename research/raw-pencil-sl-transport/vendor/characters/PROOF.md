# Complete determinant images of supplied finite-field pencils

## 1. Scope and conventions

Let K=F_q. The input is a complete supplied Kronecker block model for a matrix pencil with positive total row and column dimensions m,n. The types are:

- Right singular blocks R_e, of shape e by e+1, with s on the diagonal and t above it.
- Their transposes L_e. Zero indices are allowed.
- Finite regular blocks `(I,C(f^ell))`, where f is a monic irreducible polynomial over K, ell>=1, and C is the companion matrix with ones below the diagonal.
- Infinity blocks `(C(X^ell),I)`.

Every type can have any positive multiplicity. All matrices and both tensor dimensions are finite. The model is supplied. This note does not implement its discovery from an arbitrary tensor. These are the full Kronecker types, not only semisimple or split regular blocks.

Use the covariant action

`(A0,A1) -> (P(a A0+b A1)Q^T, P(c A0+d A1)Q^T)`,

where `R=[[a,b],[c,d]]` is invertible. Let Delta be the image of the stabilizer under `(det P,det Q,det R)`. Polynomial pencil identities are coefficient identities in independent indeterminates. They are not tests at only the q+1 rational directions.

The singular Hom spaces and slice lifts are credited to PR5683 and apoursh PR5672. The regular centralizer determinant theorem is the classical result retained by Nick Petalas PR5250. New here are the per-primary chart construction, full mixed assembly and the removal of the global invertible-rational-slice premise.

## 2. Normalize one primary block after any slice action

Consider a finite block `(I,J)`, with J=C(f^ell). Set B=aI+bJ and D=cI+dJ. If B is invertible, put H=B^-1 D. Otherwise D is invertible: failure of both would make both linear polynomials a+bX and c+dX divisible by the same irreducible f, contrary to det R!=0. In the second case f must be linear. Put H=D^-1 B. Its only eigenvalue is zero, and its nilpotence index is ell.

For an infinity block `(J,I)`, use B=aJ+bI and D=cJ+dI. If b!=0, B is invertible. If b=0, D is invertible and H=D^-1 B is nilpotent of index ell. Thus one chart is always available on each primary block even when no chart is invertible on the full pencil.

In either chart H is a fractional linear function of J with nonzero determinant. Its inverse fractional expression is defined in K[J]. Hence `K[H]=K[J]`. The first coordinate vector v is cyclic for J and therefore for H. The matrix

`S=[v,Hv,...,H^(k-1)v]`

is invertible, where k is the block dimension. Then `S^-1 H S` is the companion matrix of the transformed monic primary polynomial. This gives a direct construction with no eigenvalue choice or extension-field embedding.

In the finite chart take

`P=S^-1 B^-1`, `Q=S^T`.

The transformed block is `(I,S^-1 H S)`. In the infinity chart take `P=S^-1 D^-1`, `Q=S^T`; it is `(S^-1 H S,I)`. These formulas prove both literal identities, not only a determinant equality. The transformed primary degree and Jordan length are preserved, except that a linear finite primary can exchange with infinity.

For a fixed R, normalize every regular block and compare the resulting multiset with the original regular multiset. Retain R exactly when the types and multiplicities match. Match equal blocks and apply the corresponding common row/column block permutation. Its determinant signs are part of the actual matrices. Combine these matrices with the credited singular slice lifts. This constructs a literal full-pencil stabilizer `(P_R,Q_R,R)` for every retained R.

Conversely a full-pencil equivalence preserves its Kronecker types. This also follows from the Hom decomposition below: singular types remain singular with the same indices, while the regular diagonal must be a module isomorphism with equal primary lengths and multiplicities. Thus a rejected regular multiset cannot be repaired by singular/regular mixing. The retained R are exactly the possible slice actions. Let their explicit lift determinants be `(p_R,q_R,z_R)`.

## 3. All fixed-slice mixing and its determinant image

Set `C=Q^-T`. A fixed-slice stabilizer is precisely an automorphism satisfying `P A_i=A_i C` for both i.

The singular Hom table from PR5683 is retained: right-to-right dimension max(e-f+1,0), left-to-left dimension max(f-e+1,0), right-to-left zero, and left-to-right dimension e+f. Its scalar recurrences include zero indices.

For one finite regular block `(I,M)` of dimension k, comparison of the two coefficients gives:

| Source | Destination | Hom dimension |
| --- | --- | ---: |
| R_e | regular | 0 |
| regular | R_e | k |
| regular | L_e | 0 |
| L_e | regular | k |

For regular to R_e, the second matrix has rows `u,uM,...,uM^e`; the first consists of its first e rows. The row u is arbitrary. For L_e to regular, the first matrix has columns `v,Mv,...,M^e v`; the second consists of its first e columns. The column v is arbitrary. In the two zero directions, a zero boundary row or column propagates across the recurrence and forces every entry to zero. These formulas include e=0. Exchanging the two slices and using the singular slice lift proves the same statements for an infinity primary. Multiplicities give arbitrary matrices between multiplicity spaces.

Order right types by increasing index, then all regular types, then left types by decreasing index. The full morphism is upper triangular between these three groups. Thus all regular/singular and singular inter-type mixing is included and has no effect on either determinant.

Within the regular group, different projective primary points have zero Hom. For finite primaries this is the usual Bezout argument for relatively prime polynomials. For finite versus infinity, one equation gives U=M U N with N nilpotent, and iteration forces U=0. Infinity versus finite is the transpose argument.

For one finite irreducible f of degree d, the regular module is

`direct_sum_ell (K[X]/f^ell)^(r_ell)`.

The filtration by powers of f has residue field E=K[X]/f. The exact-length-ell diagonal multiplicity map D_ell appears on ell successive layers. Maps between different lengths are triangular on each layer. Therefore

`det_K P_regular = product_(f,ell) Norm_(E/K)(det_E D_(f,ell))^ell`.

The same formula for infinity uses E=K. Each residue norm is onto K*. Conversely multiplication on one selected block by a unit lifting any residue element realizes that norm to the ell-th power. This is the credited classical centralizer theorem from PR5250, now applied separately at every projective primary point. Since Q=P^-T for this diagonal regular group, its determinant pairs are exactly `(h,h^-1)`, with

`h in (K*)^g`, `g=gcd(all regular block lengths)`.

The residue degree and the multiplicity do not replace the block length in g.

For each distinct right singular index e, its multiplicity determinant gives `(u^e,u^(-e-1))`; for each left index it gives `(u^(-e-1),u^e)`. This uses the transposed parameter convention of PR5683. All u in K* occur. Hence the complete fixed-slice image F is the subgroup of `(K*)^2` generated by

`(u^e,u^(-e-1))` for every right type,

`(u^(-e-1),u^e)` for every left type,

`(u^ell,u^-ell)` for every regular block length,

for all u in K*. Repeated copies do not add generators. No block-diagonal assumption is used in the upper bound: the full Hom analysis gives it.

For a mixed model with at least one singular type, choose its primitive vector v0 and the primitive row eta annihilating it as in PR5683. Then F is equivalently the condition

`x^eta1 y^eta2 in (K*)^d`,

where d is the gcd of all singular values `eta dot v_i` and all regular lengths. This follows because eta1-eta2 is 1 or -1. It explains why a regular semisimple block removes the row/column obstruction, while a length-two regular block need not do so.

## 4. Complete image, labels and literal correction

**Theorem.** For the supplied model over F_q,

`Delta = union_(retained R) {(p_R x,q_R y,z_R) : (x,y) in F}`. (1)

For necessity, divide any stabilizer by the constructed lift with its exact slice action R. The quotient fixes the slices, so its determinants lie in F by section 3. For sufficiency, compose the lift with a fixed-slice witness. This proves (1), attainment and independence from all block-matching choices. Different R with the same determinant can give different cosets. The algorithm must keep that union; it cannot choose one arbitrary representative per determinant.

The ambient determinant map from `GL_m x GL_n x GL_2` onto `(K*)^3` is surjective because m,n>0. Its kernel is the product of the three special linear groups. Thus the SL orbits in the GL orbit are exactly `(K*)^3/Delta`. The executable returns the smallest triple in each finite coset as its label. Their number is `(q-1)^3/|Delta|`.

If a supplied GL map g has determinant triple in Delta, take the literal stabilizer h with the same triple. Then `g h^-1` has three determinant-one factors and the same tensor image as g. A prescribed slice action can be requested only when its particular coset admits the triple; global membership does not imply membership for every R of the same determinant.

A supplied change of coordinates to the model conjugates the stabilizer. Conjugation leaves all three determinants fixed. The formula therefore applies to any pencil with that supplied decomposition and checked factor maps. It does not discover those maps.

## 5. A closed family with no invertible rational slice

Take one length-ell Jordan primary at every point of P1(F_q), with common multiplicity r. Every rational slice is singular, but the homogeneous determinant polynomial is a nonzero scalar multiple of

`(s^q t-s t^q)^(r ell)`.

Thus the pencil is regular. Every GL2 action permutes these equally weighted primary types and is admitted. Write `H=(K*)^ell`. Then the exact character image is

`Delta = {(x,y,z): x in H and x*y*z^(r ell)=1}`. (2)

In particular y is also in H. There are exactly `(q-1)*gcd(q-1,ell)` SL orbits. For ell=1 this gives q-1, including the binary diag(s,t,s+t) case. For F5 with ell=2 there are eight, not four. For F4 with ell=3 there are nine.

Here is the extra determinant argument needed for nonsemisimple lengths. The fixed-slice first determinant group is H. Therefore `R -> p_R mod H` is a group homomorphism. Every elementary unipotent in SL2 has p-power order, where p is the characteristic; K*/H has order prime to p. SL2 is generated by those elementary matrices, so its image is trivial.

It remains to evaluate `R=diag(z,1)`. On each of the q finite primary blocks, the cyclic basis is diagonal with entries `1,z^-1,...,z^(-(ell-1))`. Its P determinant is `z^(ell(ell-3)/2)`. On infinity it is `z^(-ell(ell-1)/2)`. The common block permutation has a sign raised to r ell, which lies in H. The total exponent is

`r*((q-1)*ell*(ell-3)/2-ell)`.

Since ell(ell-3)/2 is an integer and z^(q-1)=1, this is an ell-th power. Hence p_R lies in H for every R. Conversely all x in H can be supplied by the regular fixed-slice group. Finally, `s^q t-s t^q` transforms by det R, so determinants of the pencil identity force `xy=z^(-r ell)`. This proves (2). A determinant-polynomial comparison alone would miss the condition x in H.

## 6. Algorithm and cost boundary

For fixed q and a supplied complete model, equation (1) gives deterministic polynomial-time image and label extraction in the total factor dimensions. Enumerate the fewer than q^4 matrices in GL2, normalize each companion block by matrix arithmetic, match its exact transformed companion polynomial, and compute F from the displayed exponent generators in the at most (q-1)^2-element group. No large matrix stabilizer is enumerated. The quotient has at most (q-1)^3 elements. The exact polynomial exponent is not optimized.

The singular witnesses use the credited characteristic-safe symmetric powers. A regular witness needs a residue element of a specified norm. Existence is proved above. Uniform sampling in the finite residue field gives an exact Las Vegas construction: test the norm and accept only the required value. Its expected trial count is at most q, and each trial has polynomial field-operation cost. Deterministic enumeration also terminates, but no polynomial bound is claimed for that norm search in unbounded residue degree. The bounded executable enumerates residues of degree at most three. It does not implement the randomized general solver or claim polynomial complexity in log(q).

The finite verifier uses F2/F3/F4/F5, singular indices 0..5, regular lengths 1..3, residue degrees 1..3, multiplicities 1..3, and total dimensions at most sixteen. Its declared models cover strict subdomains of those bounds; it does not enumerate every admissible model. The written theorem has no such dimension, length, degree or field-size restriction.

A separate coefficient-equation oracle imports no lift or character formula. For each declared slice action it solves all `P B_i=A_i C` equations, enumerates every vector in that solution space, and retains exactly invertible P,C. Large fixtures explicitly mark a selected action set; the other fixtures cover all GL2. Literal witnesses cover every admitted GL2 action in every declared model. Malformed inputs, wrong determinant restrictions and corrupt literal maps reject.

## 7. Use, limits and credit

This completes the determinant-character interface for supplied finite-field pencil models, including nonsplit primary factors, all Jordan lengths, infinity, both singular orientations and zero indices. It resolves the missing global-slice premise in PR5250 and the regular/singular coupling question from PR5672/5683. It is not an arbitrary-tensor recognizer, a general tensor-atlas solution, a proof-assistant certificate or independent human acceptance.

A multiplication use still needs a concrete native producer and consumer. Native maps, dirty ownership, movement, restoration, storage, precision, repeated preparation and the complete recursive bill remain unknown. They are not free. No new kappa or selected-frontier change follows from this algebraic result.

Ali Romman with substantial OpenAI Codex assistance. Credit Nick Petalas PR5250 and its Arne Storjohann and Ferrer/Mingueza/Montoro lineage; apoursh PR5672; Ali Romman PR5683; David Ganz A030/A026/A029; and classical Kronecker, companion-matrix and finite-field norm theory. Original source notices remain under source/. The new assembly and checks are Apache-2.0. Global literature priority is unclaimed.
