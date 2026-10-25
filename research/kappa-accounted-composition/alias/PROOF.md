# Exact scope of the alias probe

The frozen geometry has K=L^T and LK=13I. The construction below uses only
dyadic scalar additions and signs. It assumes the previously verified H
kernel; the pending emitter is responsible for authenticating that input and
all physical boundary adapters.

## Forward exchange

At a completed source frame perform:

1. A <- A+LU, forming v.
2. U <- U+KP-KA, giving U+K(d-v).
3. Exchange A and P using three shears and a sign.

The result is `(U+K(d-v),d,v)`. From the output, recover

\[
d=A',\quad v=P',\quad U=U'-K(A'-P'),\quad A=P'-LU.
\]

Thus arbitrary cache data are moved reversibly, not erased. With 416 signed
half coefficients in L, the wrapper has 1248 half additions, 24 unit
additions, and eight signs: `1248*10 + 24*8 + 8*2 = 12688` real scalar
allowance. Eight identity-to-full cache paths add eight rank-nine children.

## Backward exchange

Normalize selected original X_A to the Y entrance frame. Form `w=e+Lc` in
Y_A, then apply the three-shear signed exchange

\[
(X_A,Y_A)=(b,w)\longmapsto(w,-b).
\]

Subtract Lc from Y_A and return X_A to its original line. The prefix therefore
maps `(a,b,c,e)` to `(a,e+Lc,c,-b-Lc)`. The backward H call subtracts

\[
H\begin{bmatrix}c\\-b-Lc\end{bmatrix}
=\begin{bmatrix}c+Kb\\-Lc-12b\end{bmatrix}
\]

from X. This gives the stated whole-word formula. The prefix inverse is
`c=Y_U'`, `b=-(Y_A'+Lc)`, `e=X_A'-Lc`; its integrality and invertibility do not
depend on any data value.

The scalar invoice is `832*10+24*8=8512`. The selected fields each make a paid
rank-one descent and ascent, for16 rank-one children. In the inherited
backward convention their actual input transform is conjugate(C_q); the
physical descent must be its adjoint, and the return its original operator.
The emitter checks both lowering monomials, the recursive Fourier, and
absolute phase. These checks remain pending while the frozen inputs are
unavailable.

## A local cancellation is not a complete caller

Immediately after a forward H call, ordinary target data are
`Y_U = y_U + x_U - K_s v`. The forward exchange gives
`X_U = x_U + K_s(d-v)` and `X_A=d`. If these enter the backward prefix without
an intervening ordinary mutation, its ordinary result is

\[
X_U-Y_U-K_t d=-y_U+(K_s-K_t)d.
\]

Only equal charts make the last term vanish. The full caller also contains
bridges that act on both ordinary and selected fields.

The independent audit restricts to one active constant-chart channel with
K=1,L=13. It constructs H shears literally, including all original selected
inputs and fresh forward-cache inputs. It uses the complete alternating
schedule and both bridge directions, then the signed terminal swap. Exact
rational elimination proves invertibility for p=1,...,5 and the scoped
observer gaps p-1. Other charts or additional observations are outside this
negative result.

For p=2 an explicit witness, in initial order
`[X0_U,X0_A,Y0_U,Y0_A,X1_U,X1_A,Y1_U,Y1_A,d0,d1,d2]`, is

\[
(-12,156,13,-182,12,13,0,-143,0,13,0).
\]

Every granted final selected A value, forward cache, and completed ordinary
Y value is zero. Ordinary endpoint errors in order
`[X0_U,Y0_U,X1_U,Y1_U]` equal `(13,-13,-13,0)`. Thus these observations alone
cannot determine the required correction, even though the full augmented
operator is invertible.

## Physical helper normalization: a distinct useful lemma

If a fully verified native word restores every helper logical input and has
zero helper-to-data and data-to-helper blocks, its whole physical operator is

\[
\operatorname{diag}(D,T_1,\ldots,T_h),\quad
T_i=F_{i,\mathrm{end}}F_{i,\mathrm{start}}^{-1}.
\]

Boundary monomials on helper i can normalize T_i to its ordinary recursive
Fourier normal form without changing D or any internal ADD. This does not
retag each intermediate helper frame independently. It is a whole-operator
fact and can remove a spurious requirement to prepare every canonical helper
entrance in a new productive host.

To use it, each T_i still needs an exact relative-frame lowering certificate:
the claimed rank, both adapters must be free monomials, and the absolute
phase must match. The available frozen `clifford_exact.lower_child` routine
can supply this certificate. Outer host packing and disjoint productive axes
must then be proved for the normalized complete blocks. This lemma does not
by itself supply a caller correction or a new kappa.
