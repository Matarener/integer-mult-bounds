# Four inverse cyclic targets need eight calls

This scoped proof was produced by Nick Petalas. New work is Apache-2.0.

Let A=F2[g]/(g^3+1), the full formal group algebra F2[C3]. There are
exactly four scalar roles, each with arbitrary dirty input in A. The paid
alphabet consists of

    D_N(g) = I + (1+g) N,
    N = u v^T over F2, v^T u = 1.

Each call costs one. Any binary invertible scalar matrix is free. The
required complete endpoint is T=g^2 I_4. No extra role, clean allocation,
erasure, free g^2 call or free address operation is allowed.

**Theorem.** The minimum paid-call count is eight.

## Remove free scalar bridges

For any S in GL_4(F2), conjugation sends D_N(g) to D_(SNS^-1)(g).
Move every scalar bridge to one endpoint, conjugating the intervening
couplings. Augmentation g=1 sends every paid factor to I and sends T to I.
Thus the remaining scalar endpoint factor is I. This reduces every program
to a product of paid factors with the same count and legal binary couplings.
It accounts for arbitrary interleaved scalar changes, not only a fixed basis.

## Only five calls could improve on eight

Write F4=F2[w]/(w^2+w+1). Specialize g to w. Put d=1+w=w^2. Each paid
factor is I+dN and has determinant w, since N is a rank-one idempotent.
The target is w^2 I_4 and has determinant w^8=w^2. A k-call word therefore
requires k=2 modulo 3. Also rank(T-I)=4 in F4. Telescoping a product of k
rank-one increments bounds rank(T-I) by k. Among k<8, only k=5 survives.
These are necessary conditions on a formal identity; specialization is not
used as a sufficient formal-endpoint test in the proof.

## A product with four independent update directions

Consider four factors F_i=I+d u_i v_i^T with binary u_i,v_i and v_i^T u_i=1,
in chronological order i=1,2,3,4. If rank(F_4 F_3 F_2 F_1-I)=4, their four
image vectors u_i are independent. Indeed the image of the product minus I
lies in span_F4(u_1,u_2,u_3,u_4), by telescoping left updates. Binary vectors
are independent over F4 exactly when they are independent over F2.

Conjugate by the binary matrix with columns u_1,...,u_4. Each factor now
updates only row i, and its binary row functional a_i has a_ii=1. Let L
and U be the strict lower and strict upper parts of the binary matrix with
rows a_i. If M is the final product, its i-th row satisfies

    M_i = e_i^T + d (sum_(j<i) a_ij M_j + sum_(j>=i) a_ij e_j^T).

Earlier rows already have their final values; later rows are still their
identity rows. Consequently

    (I+d L) M = I+d(I+U).                              (1)

This is a row-once identity for the stated four factors. It does not assume
that their functionals or projectors commute.

Suppose, in addition, M=d I+P with P binary. Substitute in (1), use
w^2=w+1 and d^2=w, and compare the coefficients of 1 and w. They give

    I+P+LP = U,
        L+LP = U.

Subtracting gives P=I+L. A strict lower triangular L makes I+L invertible.
Thus such a four-factor product requires rank_F2(P)=4. In particular it
cannot have rank(P)=1.

## Exclude five calls

Assume F_4 F_3 F_2 F_1 F_0 = d I, with five legal paid factors after
specialization. Since F_0^-1=I+w N_0, removing the chronological first
factor gives

    F_4 F_3 F_2 F_1 = (d I)(I+w N_0) = d I+N_0.       (2)

The right side minus I is w I+N_0. It is invertible: on im(N_0) it is
multiplication by w+1, and on ker(N_0) by w. Both scalars are nonzero.
The preceding four-direction lemma applies. Its binary basis change sends
N_0 to a binary rank-one projector P, while leaving d I fixed. Equation
(2) would therefore require rank(P)=4. This contradicts rank(P)=1.
Five calls are impossible, completing the lower bound.

## Attainment and scope

On each coordinate role apply its coordinate projector twice. This is eight
positive-g calls and gives g^2 on that role, hence T exactly in the full
formal algebra. All four input columns remain arbitrary. There are no
spectators to restore and no auxiliary input is silently set to zero.

The argument proves this four-role tariff only. In a larger register space
the target with restored spectators is no longer a scalar matrix. Removing
the first factor then need not leave the full-rank four-direction situation
above. No lower bound with extra roles is claimed. Additional paid labels,
nonbinary scalar coefficients and different endpoints also need new analysis.
No native, physical or recursive supplier cost follows from the formal count.
Independent human and formal proof-kernel review are unclaimed.
