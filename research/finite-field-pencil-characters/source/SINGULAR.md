# Determinant characters for all purely singular Kronecker sums

## 1. Scope and action

Let K be any field. Let R_e be the e by e+1 pencil with s on the diagonal and t above it, and let L_e=R_e^T be its left orientation. The predecessor calls the right block L_e; this note uses R and L to mark the two orientations. Minimal indices e can be zero. Thus R_0 has shape 0 by 1 and L_0 has shape 1 by 0.

Let T be a finite direct sum of these blocks with positive multiplicities. Combine repeated equal types. Both total row and column dimensions m,n must be positive. The result does not include a regular block. The model is supplied; extraction from an arbitrary tensor is a separate task.

Use exactly the predecessor's covariant action

`(A0,A1) -> (P(a A0+b A1)Q^T, P(c A0+d A1)Q^T)`,

where `R=[[a,b],[c,d]]` is the slice factor. Let Delta(T) be the image of its stabilizer under `(det P,det Q,det R)`. The right factor is Q^T, not Q^-1. All pencil equations are coefficient identities in two independent indeterminates, including over finite fields.

The source is apoursh PR5672 at `81c0577b83cdafa73346da8ade1261b0b202e45f`, following Nick Petalas PR5250. Its single-type theorem, characteristic-safe slice lift and exact action convention remain predecessor work. This note supplies the complete mixed singular extension.

## 2. Explicit intertwiner spaces

A morphism from a source block to a destination block is a pair U,C with

`U T_source(s,t)=T_destination(s,t) C`.

For a source with shape ms by ns and destination with shape md by nd, U has shape md by ms and C has shape nd by ns. Comparing the s and t coefficients gives the following complete table:

| Source | Destination | Dimension | Form |
| --- | --- | ---: | --- |
| R_e | R_f | max(e-f+1,0) | Rectangular upper Toeplitz |
| L_e | L_f | max(f-e+1,0) | Transpose dual of the preceding row |
| R_e | L_f | 0 | Zero |
| L_e | R_f | e+f | Rectangular Hankel |

Here are explicit bases and completeness arguments. For R_e to R_f with e>=f, choose coefficients a_0,...,a_(e-f). Put `C_(i,j)=a_(j-i)` for `0<=i<=f`, `0<=j<=e`, with coefficients outside that range zero. Use the same rule for U on `0<=i<f`, `0<=j<e`. The coefficient equations force each diagonal to be constant, with both boundary edges zero outside the displayed range. If e<f, those boundary conditions force every entry to zero. This proves both spanning and independence. It also covers e=0 or f=0.

Transposing the equation identifies L_e to L_f with R_f to R_e, exchanging and transposing the two matrices. This gives the second row in every characteristic.

For R_e to L_f, the top t-coefficient gives U_(0,j)=0 for every j. The s-coefficients then make the first row of C zero, including its last entry. The interior relation C_(i+1,j)=C_(i,j+1), together with the zero last column, makes every later row zero. The remaining coefficient equations make U zero. If an index is zero, the remaining pencil has no nonzero constant polynomial kernel of the required orientation, or the two matrices have no entries. Thus the third row is zero without an exception.

For L_e to R_f, choose a_0,...,a_(e+f-1). Set

`U_(i,j)=a_(i+j)`, for `0<=i<f`, `0<=j<=e`,

`C_(i,j)=a_(i+j)`, for `0<=i<=f`, `0<=j<e`.

The two coefficient equations say precisely that successive antidiagonals agree. They impose no further boundary condition. These e+f coefficients are independent. When e=f=0 there are none.

Multiplicities replace each scalar coefficient by an arbitrary matrix from the source multiplicity space to the destination multiplicity space. This includes all off-diagonal mixing; it is not a block-diagonal assumption.

## 3. Complete fixed-slice determinant image

Order distinct types as right blocks in increasing index, followed by left blocks in decreasing index. Section 2 makes every morphism between different types upper triangular in this order. On one repeated right type of index e and multiplicity r, a diagonal morphism is

`P=I_e tensor D`, `C=I_(e+1) tensor D`.

For a left type the two dimensions are exchanged. This includes zero indices: the nonempty diagonal matrix still determines D. A simultaneous automorphism requires and is implied by invertibility of every diagonal D. Its off-diagonal blocks do not change either determinant.

For a fixed slice action, put `C=Q^-T`. The two stabilizer equations are `P A_i=A_i C`. Hence the preceding morphism analysis gives every fixed-slice stabilizer, including its nonzero off-diagonal entries.

Parameterize the right-type determinant by u=det D. Parameterize a left type by u=(det D)^-1, to retain the predecessor's transposed lift convention. Each distinct type contributes a vector

`v_R(e)=(e,-e-1)`, `v_L(e)=(-e-1,e)`

to the exponents of `(det P,det Q)`. Every u in K* occurs, by a diagonal multiplicity matrix. Multiplicity does not multiply these two exponents: it is the determinant of the full GL_r matrix that is free.

Thus the fixed-slice image is exactly

`{(product_i u_i^(v_i,1), product_i u_i^(v_i,2), 1): u_i in K*}`.

## 4. All slice actions and multiplicities

For every `R in GL2(K)`, let z=det R. The predecessor's polynomial-substitution matrices S_k(R) use ordinary monomials, not divided powers or factorial inverses. Their determinant is `z^(k(k+1)/2)` in every characteristic. A right block of positive index e and multiplicity r has the explicit lift

`P_R=S_(e-1)(R)^T tensor I_r`,

`Q_R=S_e(R)^-1 tensor I_r`.

Its determinant shift is `(z^(r e(e-1)/2),z^(-r e(e+1)/2))`. A left block exchanges these two matrices and shifts. A zero-index block is identically zero and uses identity on its nonempty factor. Its shift exponents are zero, as the same integer formulas require.

Take the direct sum of these lifts. Define the integers

`A = sum_right r e(e-1)/2 - sum_left r e(e+1)/2`,

`B = -sum_right r e(e+1)/2 + sum_left r e(e-1)/2`.

The quotient of any other stabilizer with this same R and this lift fixes the unmixed pencil. Section 3 gives its complete determinant image. Conversely each of those fixed-slice factors can be composed with the lift. Therefore

`Delta(T) = {(z^A product_i u_i^(v_i,1), z^B product_i u_i^(v_i,2), z): u_i,z in K*}`.  (1)

The lift works for every prescribed matrix R of determinant z, not only a diagonal representative. All half-products above are integer exponents. There is no division by two in K.

## 5. One exact character and its power subgroup

Choose a base type. For a right base index e0 set `ell=(e0+1,e0)`; for a left base set `ell=(e0,e0+1)`. In both cases ell has coprime entries and `ell dot v0=0`. Put

`c_i=ell dot v_i`, `d=gcd_i(c_i)>=0`.

The gcd of an all-zero list is zero. Define

`chi(x,y,z)=x^ell1 y^ell2 z^(-ell1 A-ell2 B)`.

**Theorem.** For every field K,

`Delta(T) = {(x,y,z) in (K*)^3 : chi(x,y,z) in (K*)^d}`.  (2)

Here `(K*)^0={1}`. This convention recovers the exact equality for a single distinct block type.

For necessity, apply chi to (1). Its value is `product_i u_i^c_i`, which is a d-th power when d>0 and is one when d=0.

For sufficiency with d>0, let `w^d=chi(x,y,z)`. Choose integer Bezout coefficients b_i with `sum_i b_i c_i=d`, and set `u_i=w^b_i`. Remove the slice shifts and these u_i contributions from x,y, leaving X,Y with `X^ell1 Y^ell2=1`. For either base orientation, `a=(XY)^-1` supplies exactly the residual pair through `a^v0`. Multiply a into u_0. Equation (1) and the explicit block lifts now construct the requested stabilizer. When d=0, start with every u_i=1 and make the same kernel correction. No root is then needed.

Over an arbitrary field, membership in the power subgroup includes the existence of w; a constructive witness can take w as input. The theorem does not assume an algorithm that extracts arbitrary roots in K. The bounded finite-field executable finds w by enumerating the at most q-1 nonzero elements.

The kernel correction is elementary. For a right base, `X^(e0+1)Y^e0=1` gives `(XY)^(-e0)=X` and `(XY)^(e0+1)=Y`. For a left base, exchange X and Y. These formulas include e0=0.

The primitive vector v0 can be completed to an integral basis. Hence d is also the gcd of all two-by-two minors of the type vectors. These minors are, up to sign,

- Differences of two right indices.
- Differences of two left indices.
- Sums e+f+1 for a right index e and a left index f.

This is a direct criterion using the full type list. It is independent of multiplicities. Multiplicities still affect A,B and therefore the actual character label; they cannot be dropped from the slice shift.

## 6. Special-linear orbit labels and constructive correction

Because m,n are positive, the determinant map from `GL_m(K) x GL_n(K) x GL_2(K)` onto `(K*)^3` is surjective, with kernel the product of the three special linear groups. Its orbits inside one GL orbit are therefore the cosets of Delta(T).

The map chi is surjective onto K*: for a right base use `(x,y,z)=(u,u^-1,1)`, and for a left base exchange x,y. Equation (2) gives a complete label group

`K*/(K*)^d`.

Over F_q, the exact number of special-linear orbits is

`gcd(q-1,d)`, with `gcd(q-1,0)=q-1`.

For example, consecutive right indices give d=1 and one SL orbit. R_1 plus L_1 has d=3 and gives three SL orbits over F4. R_1 plus L_2 has d=4 and gives four over F5. Zero-index factors are included whenever both full factor dimensions are positive. In particular, a sum of R_0 and L_0 is a zero pencil with full determinant image, as d=1 requires.

If a supplied GL map g has determinant triple in Delta(T), choose the stabilizer witness h with that same triple. Then `g h^-1` has determinant one in every factor and has the same action on T as g. This gives a literal SL correction when the model and map are supplied. It does not discover a canonical model or a GL map from an arbitrary tensor. Equal labels similarly give an SL transporter between two supplied presentations by composing their maps and the appropriate stabilizer witness.

## 7. Verification boundary and use

The exact verifier checks the Hom formulas against literal coefficient equations for every ordered pair of orientations and indices zero through three over F2, F3, F4 and F5. It then solves the full mixed stabilizer equations in twelve declared domains, enumerates every vector in each resulting linear solution space, and retains precisely invertible P,C. It uses neither the character formula nor the symmetric-power lift in that oracle. Cases marked with all_slice_actions cover every GL2 action. The other cases cover one representative for every nonzero slice determinant, with every GL2 action separately checked by literal constructed lifts.

The finite evidence supports the all-field proof. It is not an exhaustive enumeration over all indices, dimensions or fields. The executable restricts indices to zero through five, combined multiplicities to one through three, fields to F2/F3/F4/F5, and both total factor dimensions to at most sixteen. The written proof has no such bounds.

This closes the supplied purely singular determinant-character interface in the tensor atlas. Native realization, dirty-state ownership, movement, restoration, storage, precision and the complete recursive cost remain unknown. Regular blocks, arbitrary-tensor extraction and a paid multiplication consumer are outside the result. No new kappa, selected-frontier change, human acceptance or proof-kernel verification is claimed.

New proof and checks: Ali Romman with substantial OpenAI Codex assistance. Credit apoursh PR5672; Nick Petalas PR5250; David Ganz's A030/A026/A029 atlas and the classical Kronecker and symmetric-power lineage. The source notice and action conventions remain unchanged.
