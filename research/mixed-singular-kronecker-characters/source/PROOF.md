# Determinant image of an isotypic singular Kronecker pencil

This note gives a self-contained proof for one positive right minimal index
with arbitrary positive multiplicity, and obtains the left-block case by
transposition. It addresses the corresponding open question in Nick Petalas's
[pencil-determinant-image package at its pinned head](https://github.com/CrocSwap/integer-mult-bounds/blob/43142bedc7cb5c0f1f73ff3fea6d9bfd237949ee/research/pencil-determinant-image/README.md).
The block and symmetric-power constructions are classical; no literature
novelty is claimed. The addition here is the explicit determinant-image formula,
its action conventions, and its bounded verification package. This is a scoped
proof, not a new multiplication bound or a classification of arbitrary pencils.

## 1. Pencil and action conventions

Let K be any field, and let e,r be positive integers. Define

```
A_0 = [I_e | 0],       A_1 = [0 | I_e],
L_e(s,t) = s A_0 + t A_1.
```

Thus L_e is e by e+1, with s on its main diagonal and t immediately above
that diagonal. Set

```
T_0 = A_0 tensor I_r,   T_1 = A_1 tensor I_r,
T(s,t) = L_e(s,t) tensor I_r.
```

The row dimension is er and the column dimension is (e+1)r. The tensor-product
ordering groups each monomial index into an r-dimensional block. A simultaneous
permutation of rows and columns identifies this pencil with the direct sum of
r identical L_e blocks.

For P in GL_(er)(K), Q in GL_((e+1)r)(K), and

```
R = [[a,b], [c,d]] in GL_2(K),
```

use exactly the action

```
(T_0,T_1) -> (P(a T_0 + b T_1)Q^T, P(c T_0 + d T_1)Q^T).
```

In particular the right factor in the action is Q^T, not Q^(-1). If
z=(s,t)^T, the mixed pencil is T(R^T z), because

```
s(a T_0+b T_1) + t(c T_0+d T_1)
    = (as+ct)T_0 + (bs+dt)T_1.
```

Let Stab(T) be the stabilizer under this action, and let

```
Delta(T) = { (det P, det Q, det R) : (P,Q,R) in Stab(T) }.
```

All equalities of pencils below are polynomial equalities in independent
indeterminates s,t. No interpolation over the points of K is used.

## 2. The exact image

**Theorem.** For every field K and all e,r >= 1,

```
Delta(L_e tensor I_r)
 = { (u^e z^[r e(e-1)/2],
      u^[-(e+1)] z^[-r e(e+1)/2],
      z) : u,z in K^* }
 = { (x,y,z) in (K^*)^3 :
       x^(e+1) y^e z^[r e(e+1)/2] = 1 }.
```

The half-products in these exponents are integers. They do not denote division
inside K, so the statement includes characteristic two.

For the transposed block the result is

```
Delta(L_e^T tensor I_r)
 = { (x,y,z) in (K^*)^3 :
       x^e y^(e+1) z^[r e(e+1)/2] = 1 }.
```

The proof also constructs a stabilizer element for every triple in the stated
image, with any prescribed R having determinant z.

## 3. A characteristic-safe lift of every slice transformation

For k >= 0 let V_k be the homogeneous degree-k polynomials in X,Y, with ordered
basis

```
X^k, X^(k-1)Y, ..., Y^k.
```

Let S_k(R) be the matrix of polynomial substitution

```
f(X,Y) -> f(aX+bY,cX+dY)
```

on coefficient columns in this basis. Equivalently, column i, with
0 <= i <= k, consists of the coefficients of

```
(aX+bY)^(k-i) (cX+dY)^i.
```

In particular S_0(R)=[1] and S_1(R)=R^T. This convention matters for the
transposes in the lift. Substitution by R^(-1) is inverse to substitution by R,
so S_k(R) is invertible in every characteristic.

Use ordinary monomials and binomial coefficients reduced in K. There are no
normalized monomials, divided factorials, or assumptions that k! is invertible.
The substitution identities remain valid when some binomial coefficients
vanish in K.

The determinant is

```
det S_k(R) = (det R)^[k(k+1)/2].                    (1)
```

For completeness, this follows on generators of GL_2(K). For a diagonal
R=diag(alpha,beta), S_k is diagonal with entries alpha^(k-i) beta^i,
whose product is (alpha beta)^[k(k+1)/2]. Upper and lower unitriangular
matrices act triangularly with all diagonal entries one. For the matrix
interchanging X,Y, S_k reverses k+1 basis vectors, with determinant
(-1)^[k(k+1)/2]. These matrices generate GL_2(K) by row elimination.
With the stated coefficient-column convention, composition satisfies
S_k(R)S_k(U)=S_k(UR). Determinants are multiplicative in either order,
proving (1) for all R. This proof also works in characteristic two.

Let B_e(s,t)=L_e(s,t)^T. It is the coefficient matrix of multiplication by
sX+tY from V_(e-1) to V_e. Substituting the two linear forms into this product
gives

```
S_e(R) B_e(s,t) = B_e(as+ct,bs+dt) S_(e-1)(R).
```

Transposing and rearranging proves

```
L_e(as+ct,bs+dt)
    = S_(e-1)(R)^(-T) L_e(s,t) S_e(R)^T.           (2)
```

Consequently a stabilizer lift of every R is

```
P_R = S_(e-1)(R)^T tensor I_r,
Q_R = S_e(R)^(-1) tensor I_r.                      (3)
```

Indeed (2) says P_R T(R^T z) Q_R^T = T(z). There is no residual sign and
no restriction on R beyond invertibility.

## 4. The complete fixed-slice stabilizer

Suppose R=I_2 and (P,Q,I_2) fixes T. Put C=Q^(-T). The two equations are

```
P T_0 = T_0 C,       P T_1 = T_1 C.               (4)
```

Write P as an e by e block matrix and C as an e+1 by e+1 block matrix,
with every block of size r by r. Use indices starting at zero. The first
equation of (4) says that the first e block rows of C equal [P | 0]. The
second says that the last e block rows of C equal [0 | P]. In their overlap,
for 1 <= i <= e-1, one obtains

```
P_(i,0) = 0,
P_(i,j) = P_(i-1,j-1)       for 1 <= j <= e-1,
P_(i-1,e-1) = 0.                                  (5)
```

The recurrence makes each block diagonal constant. The first boundary
condition kills every diagonal below the main diagonal; the last kills every
diagonal above it. Thus

```
P = I_e tensor D,       C = I_(e+1) tensor D
```

for one r by r matrix D. When e=1 there is no overlapping block row,
but the two equations directly give C=diag(P,P), which is the same conclusion.
Invertibility of P forces D to be invertible. Conversely every invertible D
satisfies (4). Therefore the fixed-slice stabilizer is exactly

```
(P,Q) = (I_e tensor D, I_(e+1) tensor D^(-T)),
       D in GL_r(K).                              (6)
```

In particular arbitrary mixing between the r equal blocks is already included;
it contributes one full GL_r(K), not just r independent scalar factors.

## 5. All stabilizers and their determinants

Fix R. Both a given stabilizer (P,Q,R) and the lift (P_R,Q_R,R) send
T(R^T z) to T(z). Their quotient on the row and column factors therefore
fixes the unmixed pencil T(z). Equation (6) applies. Since the factors acting
on the monomial index commute with those acting on the multiplicity index,
every stabilizer with slice factor R is uniquely of the form

```
P = S_(e-1)(R)^T tensor D,
Q = S_e(R)^(-1) tensor D^(-T),       D in GL_r(K).  (7)
```

More explicitly, putting H=P P_R^(-1) and J=Q Q_R^(-1) gives
H T(z) J^T=T(z), so (6) gives H=I_e tensor D and
J=I_(e+1) tensor D^(-T). This proves necessity as well as sufficiency of (7).

Let u=det D and z=det R. Applying (1) and
det(A tensor B)=(det A)^(dim B)(det B)^(dim A) to (7) gives

```
det P = u^e z^[r e(e-1)/2],
det Q = u^[-(e+1)] z^[-r e(e+1)/2].               (8)
```

The determinant maps GL_r(K)->K^* and GL_2(K)->K^* are surjective,
as witnessed by diagonal matrices. Hence every u,z in K^* occurs, proving
the parametrized form of the theorem. Eliminating u from (8) gives

```
(det P)^(e+1) (det Q)^e (det R)^[r e(e+1)/2] = 1.
```

## 6. Constructive converse without root extraction

Suppose x,y,z are nonzero and satisfy

```
x^(e+1) y^e z^[r e(e+1)/2] = 1.                  (9)
```

Define

```
u = (xy)^(-1) z^(-re).                            (10)
```

There is no need to take an e-th root or an (e+1)-st root. To check (10),
put A=r e(e-1)/2 and B=r e(e+1)/2. Then A+B=re^2 and
2B=re(e+1). Equation (9) gives

```
u^e z^A
  = x^(-e) y^(-e) z^(-re^2+A)
  = x z^(B-re^2+A) = x,

u^[-(e+1)] z^(-B)
  = x^(e+1) y^(e+1) z^[re(e+1)-B]
  = y z^[re(e+1)-2B] = y.
```

Take D=diag(u,1,...,1), and take any R with determinant z, for example
diag(z,1). Equations (7) then give an explicit stabilizer with determinant
triple (x,y,z). This proves that (9) is the only constraint, over any field.
Conversely (8) implies xy=u^(-1)z^(-re), so (10) also proves uniqueness
of u for a given image triple.

## 7. Transposition and the finite-field orbit count

Transposing the two slice equations exchanges P and Q and leaves R unchanged.
Thus (P,Q,R) stabilizes (T_0,T_1) if and only if (Q,P,R) stabilizes
(T_0^T,T_1^T). The determinant image for the left block is exactly the right
block's image with its first two coordinates exchanged. This proves the
transposed formula in Section 2.

For K=F_q, the parametrization (8) is injective in (u,z), by (10), so

```
|Delta(T)| = (q-1)^2.
```

Let G=GL_(er)(F_q) x GL_((e+1)r)(F_q) x GL_2(F_q) and let N be the
product of its three special linear subgroups. The determinant map identifies
G/N with (F_q^*)^3. Because N is normal, the N-orbits within the single
G-orbit of T are indexed by

```
(F_q^*)^3 / Delta(T).
```

The character

```
chi(x,y,z) = x^(e+1) y^e z^[r e(e+1)/2]
```

has kernel Delta(T) and is surjective: chi(w,w^(-1),1)=w.
Consequently there are exactly q-1 such special-linear orbits. For the left
block exchange x and y in this character. This is an orbit statement about
the displayed isotypic pencil only.

## 8. Boundaries of the result and checks that can falsify mistakes

The theorem covers e>=1 and r>=1 only. The degree-zero right and left blocks
have shapes 0 by 1 and 1 by 0, respectively. They represent unused columns
or rows and require separate treatment of zero-dimensional factors; the lift
above would also call for the undefined V_(-1). Adjoining such blocks to a
positive-index pencil introduces extra fixed-slice maps that are outside the
recurrence proved here. This exclusion is a scope boundary, not a claim that
the displayed equation has been disproved under some extension of conventions.

Different positive minimal indices, mixtures of right and left blocks, and
regular/singular coupling are also outside this theorem. Their off-diagonal
homomorphisms have not been classified here. No result is claimed for the
separate regular-pencil question with no invertible rational slice.

Useful discriminating finite checks include:

- For e=1,r=1, the lift reads P=[u] and Q=u^(-1)R^(-T). The equation is
  x^2 y z=1, which checks the sign and the inverse transpose on the right.
- For e=2,r=1 over F_3, the image equation is x=z with y unrestricted.
  Dropping the slice determinant exponent would instead require x=1.
- For e=1,r=2 over F_3, the equation is y=1 with x,z unrestricted,
  whereas e=1,r=1 gives y=z. This detects an omitted multiplicity factor.
- In characteristic two, e at least two exercises vanishing binomial
  coefficients in S_e. F_4 provides nontrivial determinant characters;
  testing only F_2 cannot distinguish determinant exponents.
- Directly solve the stabilizer slice equations in small dimensions instead
  of checking only matrices generated by (7). Such a check can falsify the
  completeness assertion in Sections 4 and 5.

Finite checks support the implementation and expose convention errors. They
do not replace the arbitrary-field proof above or settle any excluded case.
