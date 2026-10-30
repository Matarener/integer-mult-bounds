# Continuous Walsh-plane gauge obstruction

This is a scoped computer-assisted proof. Its universal step is the support
partition below; its finite geometric statements are exact rank certificates
computed by `verify.py`. It is not formal-kernel or independent human review.

## Model and theorem

Use the P112 matrix `X` and nine-bit source labels `p_i` and reader labels `q_i`
from Mihir Srivastava's `p112-single-lift/geometry.py`, following
DreamingOfClouds' PR717 geometry. The 112 rows of X have eight coordinates.
For two real 112-vectors define the support tariff

```
beta(d,t) = rank_F2 ((q_i dot p_j)_(d_i != 0, t_j != 0)).
```

This is the inherited pairing-rank tariff, not a physical execution invoice.
For `a,b` in F2^3 set `chi_a(b)=(-1)^(a dot b)`, with b in binary order.
Choose any two distinct characters for each ordered pair of columns of the
8-by-2 matrices U and V. For every M in GL2(R), set

```
U' = U M,        V' = V M^(-T),
D  = [X, XU'],   T  = [X(I - V'U'^T), XV'].
```

**Theorem.** Every such ten-term factorization has the pairing-rank profile
`{8:8, 9:2}`. Its total tariff is exactly 82. In particular no rational or
real invertible basis change in these fixed Walsh planes improves PR2042's
finite-domain profile. The exact power tariff is `8*8^s + 2*9^s` for every
real exponent s, since the whole rank multiset is unchanged.

This extends Cinna Davis's PR2042 family from five matrices to all GL2(R).
It does not decide the arbitrary overlapping rank-two problem posed in
mightyOil's PR1197: U and V must still have the specified Walsh column spaces
and the rank-two product UV^T must stay fixed during the basis change.

## Algebraic identity

The inverse transpose gives `U'V'^T = UV^T`. Therefore

```
DT^T = X(I - U'V'^T)X^T + XU'V'^T X^T = XX^T.
```

The eight original reader columns are the columns of X. Their source columns
are independent of M, since `V'U'^T = VU^T`. The remaining reader columns
are nonzero linear combinations of the two columns of XU; the remaining
source columns are nonzero combinations of the two columns of XV. Invertibility
of M and the full rank of the character pairs ensure nonzero coefficient
vectors on both sides.

## The complete support partition

Write u and v for the two columns of XU. For each row i, the vanishing equation
for a combination `z u + w v` is `z*u_i + w*v_i = 0`. If both coefficients
are zero it vanishes for every direction. Otherwise it has exactly one zero
direction in the real projective line. The verifier enumerates these directions
as primitive integer pairs `(v_i,-u_i)`, with a fixed overall sign.

For each of the 56 ordered character pairs, the entire set of zero directions
is exactly

```
(1,0), (0,1), (1,1), (1,-1).
```

Each exceptional point has its own support. At every other real projective
point the support is exactly `supp(u) union supp(v)`. Thus the four points
and the generic representative `(1,2)` are exhaustive, including irrational
slopes. They are not a bounded coefficient search. The same statement applies
to the V planes. There is no assumption that the four entries of M have small
height or that its determinant is a unit.

## Finite certificates

The standalone verifier imports only the exact pinned geometry constructor.
It uses a separate nine-bit elimination routine with nine explicitly bounded
pivot steps per input row. It checks:

1. For each of the eight coordinate reader supports, the span of q_i has
   dimension 8.
2. For every ordered character pair and each of its five support strata,
   both the p_i span and q_i span on that support have dimension 9. This is
   280 support certificates, each with both ranks checked.
3. For all 56 choices of U and 56 choices of V, each of the eight corrected
   source columns `X_j - U_(j,0)*(XV)_0 - U_(j,1)*(XV)_1` has p_i span of
   dimension 9. This is 25,088 corrected-source certificates.

All rows and labels are reconstructed from the pinned constructor. The support
receipt is hashed in deterministic order and printed with hashes of package
files. No stored predecessor rank receipt is consumed.

The standard binary dot product is nondegenerate. If the source labels span
all F2^9, the restricted pairing has rank equal to the dimension of the
reader-label span. Statement 1 and statement 3 therefore give rank 8 to
each original term. Statement 2 gives rank 9 to each added term, for every
nonzero real coefficient direction on either side. This proves the theorem.

The checker also verifies literal 112-by-112 factor identities for a
determinant-minus-two gauge and a determinant-one gauge. These are corroborating
endpoint fixtures, not the justification of the infinite quantifier. A
singular gauge and a dropped added term are rejected. A wrong inverse is
separated from the required inverse transpose.

## Scope and cost boundary

The result rules out further basis searches while these Walsh planes and their
fixed product are retained. It gives no exclusion for different planes,
simultaneous mixing with the original eight channels, changed geometry,
masked endpoints, or a different tariff. It does not supply preparation,
source access, frame transport, dirty restoration, hosting, native operations,
precision, stock, a recursive compiler, or a complete multiplication theorem.
No historical packing ceiling is transferred to the selected P104 supplier.
