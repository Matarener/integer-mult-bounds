# A characteristic-three obstruction to nine-product S3 convolution

This contribution was produced by Nick Petalas. It is a scoped proof using a
classical tensor-rank theorem, with finite exact corroboration. Independent
human and formal proof-kernel review are unclaimed.

## 1. Boundary and result

Let S3 be the symmetric group on three letters. Let R be a commutative unital
ring admitting a unital homomorphism to a field K of characteristic three.
For b >= 1, consider b independent, unrestricted S3 convolutions over R.
Their input and output spaces each have dimension 6b. A bilinear formula
of length r means

    xy = sum(j=1..r) u_j(x) v_j(y) w_j,

where u_j and v_j are R-linear scalar forms on the complete respective
input spaces and w_j is an output vector over R. Forms and outputs may mix
different blocks freely. Only the r scalar products are counted; all linear
preprocessing, postprocessing and finite linear scratch are free in this
model. The product xy here is componentwise multiplication in R[S3]^b,
not convolution between the different blocks.

**Theorem. Every such formula has r >= 10b.** In particular, no nine-product
formula exists over Z[1/2], over Z[1/2,i], or over Z[1/2,zeta_8]. Joint
formulas cannot amortize this floor below ten products per block.

**Rational consequence.** Any rational bilinear formula for b such blocks
with fewer than 10b products must have at least one coefficient with reduced
denominator divisible by three. This includes its input forms and output
vectors. Thus the nine-product construction of Cinna Davis's
[PR #2224](https://github.com/CrocSwap/integer-mult-bounds/pull/2224) cannot
be replaced at the same product count by a formula using only coefficients
regular at three. This is a new application of a classical bound to that
package's exact-division question; it does not question its rational identity.

## 2. Classical theorem used

For a finite-dimensional associative unital algebra A over a field, let t(A)
be its number of maximal two-sided ideals. The Alder--Strassen bound gives

    rank(multiplication in A) >= 2 dim(A) - t(A).

This is a cited mathematical input, not a theorem established by this verifier.
See A. Alder and V. Strassen, *On the algorithmic complexity of associative
algebras*, Theoretical Computer Science 15 (1981), 201--211,
[DOI](https://doi.org/10.1016/0304-3975(81)90070-0).
The same bound and definition of t are stated in the abstract of Markus
Bläser's *A Complete Characterization of the Algebras of Minimal Bilinear
Complexity*, [SIAM publication](https://epubs.siam.org/doi/10.1137/S0097539703438277).
The bound and modular specialization are classical. No priority for either
method, or for the representation theory of S3, is claimed.

## 3. The characteristic-three algebra

Write a=(123), s=(12), so a^3=s^2=1 and sas=a^-1. Put B=K[<a>] and
u=a-1. In characteristic three,

    B = K[u]/(u^3),
    A = K[S3] = B direct-sum B s.

Let I=uB be the augmentation ideal of B. Conjugation by s preserves I,
because s u s = a^-1-1 = -u+u^2. Therefore

    J = I direct-sum I s

is a two-sided ideal of A. More explicitly, if c,d are in I^j and e,f
are in I^k, every B-coefficient of (c+d s)(e+f s) lies in I^(j+k).
It follows that J^3=0. Its dimension is four, with basis u,u^2,u s,u^2 s.

Modulo J, a becomes 1 and s remains an involution. Consequently

    A/J = K[C2] = K[t]/(t^2-1) = K x K,

because 2 is invertible in characteristic three. The last isomorphism is
evaluation at t=1 and t=-1. Equivalently, the quotient map consists of the
trivial and sign characters on S3. Their images on 1 and s are (1,1) and
(1,-1), with determinant -2 != 0, so the map is surjective.

Every maximal two-sided ideal contains J: its image in a simple quotient
is a nilpotent two-sided ideal, which must be zero. Maximal two-sided ideals
therefore correspond to those of K x K, of which there are exactly two.
Thus t(A)=2. This argument works over every characteristic-three field;
no finite-field enumeration or algebraic-closure assumption enters it.

For b independent blocks the algebra is A^b. Its nilpotent ideal is J^b
(direct product, with componentwise multiplication), its quotient is
K^(2b), and its dimension is 6b. Hence t(A^b)=2b, and the cited theorem gives

    rank(A^b) >= 2(6b) - 2b = 10b.

This applies directly to joint formulas, including cross-block linear forms.
It does not invoke any general tensor-rank direct-sum additivity conjecture.

## 4. Specialization of coefficients

Apply R -> K to every coefficient in a proposed length-r formula. Its tensor
identity remains valid, since it is an equality of the integer structure
constants of S3 multiplication. Some product terms may become zero, so the
specialized formula has length at most r. Section 3 forces r >= 10b.

For rational coefficients whose reduced denominators avoid three, all
coefficients lie in the local ring

    Z_(3) = {m/n in Q : 3 does not divide n}.

Reduction m/n -> (m mod 3)(n mod 3)^-1 maps this ring to F3. Contraposition
proves the rational consequence. Invertible changes of input/output basis
over this ring cannot evade it: after specialization they remain invertible,
or one can simply absorb them into the linear forms and output vectors.

The complex examples also have characteristic-three specializations. In
F9 = F3[j]/(j^2+1), use

    1/2 -> 2,       i -> j,       zeta_8 -> 1+j.

The polynomial X^2+1 has no root in F3, so F9 is a field. The image of i
satisfies its defining equation. Further, (1+j)^2=2j and (1+j)^4=-1, so
the eighth-root relation is preserved. These assignments define maps from
the respective coefficient rings. In particular, allowing binary Fourier
normalizations does not evade the result: sqrt(2)=zeta_8+zeta_8^-1 and its
inverse belong to Z[1/2,zeta_8]. This is an exact-coefficient statement;
arbitrary complex coefficients need not admit such a specialization.

Free linear scratch does not change the displayed formula class. With
arbitrary dirty auxiliary inputs and outputs, set the auxiliary inputs and
the initial accumulated output to zero and retain only the required data
outputs. Any formula that handles those arbitrary inputs also handles this
restriction, with no additional scalar products. Likewise, affine constants
in the separate input forms cannot evade the bound: extracting bidegree
(1,1) gives the same number of bilinear product terms. These observations
do not cover products whose two factors both mix the two input families,
nor arbitrary nonlinear straight-line algorithms.

## 5. Exact finite evidence and its limits

The verifier constructs S3 independently as permutations and as the normal
forms a^i s^e, and compares all 36 basis products. Over F3 it constructs a
four-vector basis for the common kernel of the trivial and sign characters,
checks two-sided closure, checks the quotient on all 36 products, and checks
all 16 radical basis products and 64 triple products. The resulting dimensions
are dim J=4, dim J^2=2 and J^3=0.

As a separate finite corroboration, it enumerates all 729 algebra elements,
computes the rank of each six-by-six left-multiplication matrix, and checks
that invertibility agrees with both characters being nonzero. It obtains
324 units. The theoretical count is (3-1)^2 3^4, since every fiber of the
two-character quotient has 3^4 elements and units lift across a nilpotent ideal.

Eight rejection controls cover a missing radical direction, transplanting the
radical to characteristic five, three invalid coefficient specializations,
two underpriced one-/eight-block claims, and an incorrect quotient dimension.
The product-floor controls exercise the arithmetic application of the cited
theorem; they are not exhaustive searches over tensor decompositions.

All checks remain active with Python optimization. A generated optional
receipt binds all six package source files by SHA256. It contains measured
finite evidence, not a proof-kernel certificate of the theorem above.

## 6. Research decision and remaining obligations

Stop at this obstruction. Ten is a lower bound, not a proved attainable
dyadic rank. The rational formula, its numerator divisibility, and the old
conditional ceiling are not replayed or re-certified here. No current
selected-word placement, signed invoice, recursive child implementation,
rounding, tape, native map or complete multiplication theorem is supplied.

A division by three that is known exact on restricted intermediate inputs
lies outside the coefficient ring model and remains a possible route. This
result gives neither its physical cost nor an impossibility for it. It also
does not exclude a changed convolution, restricted input space, approximate
or border-rank construction, or a different decoder mechanism. The selected
frontier and its five framework assumptions are unchanged.
