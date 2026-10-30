# Minimum size of the symmetric helper normalization

This is a restriction on the specific symmetric reflection construction in
the attached followup. It does not exclude the asymmetric dirty-core pair,
changed scalar graphs, general native operator coefficients, or other suppliers.

The authenticated programs give `K=R^T/4`, `RR^T=56I8`, and an eight-column
minor of the helper matrix `H` whose determinant is a unit in `Z[1/2,i]`.
Suppose a helper-only normalization `B` belongs to `GL_408(Z[1/2,i])`, so
both `B` and its inverse have Gaussian-dyadic entries. Suppose it puts
`HB=[A,0]`, where `A` has `k` columns, and forms

\[
Q=[R,A],\qquad D=I-\tfrac14 Q^TQ.
\]

The required ordinary-data block is `J=I−R^TR/4`. Since `R` has a right
inverse, `Q` has full row rank and `D^2=I` forces `QQ^T=8I8`. Thus

\[
AA^T=-48I_8.
\]

Reduce Gaussian dyadics modulo 3. The result is the field
`F9=F3[i]`, because `x^2+1` has no root in `F3`. The unit minor of `H`
survives reduction, and the inverse of `B` also reduces, so `A` must retain
row rank eight. But `AA^T=0` modulo 3. Its row space `U` is therefore an
eight-dimensional totally isotropic subspace of the nondegenerate bilinear
dot product on `F9^k`. Consequently

\[
U\subseteq U^\perp,\qquad 8\le k-8,\qquad k\ge16.
\]

The existing `[4I8,8iI8]` witness attains 16. The source-supported symmetric
Gaussian-dyadic normalization therefore cannot be shortened to eight added
source ports while keeping these hypotheses. The transpose here is bilinear,
not a Hermitian transpose. Using a Hermitian norm would be a different claim.

## What changes if division by 3 is permitted

Let `B4` represent left multiplication by the quaternion `1+i+j`, and let
`B8=diag(B4,B4)`. Then `B8 B8^T=3I8`, so

\[
A_8=4iB_8,\qquad A_8A_8^T=-48I_8,
\qquad A_8^{-1}=-\frac{i}{12}B_8^T.
\]

This gives an eight-column Gaussian rational factor. Its determinant is
`2^16·3^4`, and its reduction modulo 3 has rank four. There is no contradiction
with the obstruction: the helper normalization now needs division by 3.
The reflection entries alone being Gaussian dyadic does not make its
normalization and denormalization Gaussian dyadic.

This matrix alternative was screened before attempting another native
implementation. For the explicit boundary-conversion family used in the new
transition, its most favourable tested dimension is 81. Even pricing all idle
work fractionally at rank 57 leaves only approximately `69.0729673244143 H8`
for a terminal consumer. Seventy `H8` already fails this optimistic price.
The 120-port native word and a 69-`H8` consumer have not been constructed.

## Replay and controls

Run `check_normalization.py --followup /path/to/kappa-consumer-followup`.
The checker authenticates both native providers, reconstructs their actual
`R` and `H`, checks the unit minor, and checks the exact Gaussian-rational and
finite-field witnesses. Controls replace the imaginary factor, drop a column,
and reject treating the rational inverse as dyadic. The dimension inequality
is the written linear-algebra argument above, not an enumeration of matrices.

Apache-2.0. New analysis and code used substantial OpenAI assistance under the
user's direction. The original supplier and helper construction retain their
credited attribution in the attached package.
