# A seven-rotation improvement to the odd-axis Clifford Gram bound

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof, with exact finite corroboration.
Independent human and formal proof-kernel review are unclaimed.

## Statement and cited inputs

Let n be odd, n>=3, D=2^n, and choose one unitary representative U_g
of each projective n-axis Gaussian-dyadic Clifford operator. The scalar
kernel of the exact group is {1,i,-1,-i}. For every integer f>=4n+4,
define the normalized tensor Gram matrix

    G_f[g,h] = (tr(U_g* U_h)/D)^f.

Then

    G_f >= gamma I,
    gamma = 14601049/29130752 > 1/2.                    (1)

Equivalently, arbitrary complex coefficients, including coefficients chosen
separately at each width, satisfy

    D^(-f) ||sum_g b_g U_g^(tensor f)||_HS^2
        >= gamma sum_g |b_g|^2.                       (2)

Principal submatrices inherit the bound. Changing representative phases
conjugates G_f by a diagonal unitary and preserves it.

We cite, without re-enumerating or auditing, the following inputs from Ali
Romman's #5526 and Hiroki KUMAZAKI's #5694. Put N=2n and let c_(N,k)
count symplectic Pauli actions S with rank(S-I)=k.

* c_(N,k) <= 2^(Nk-k(k-1)/2).
* Exactly 2^k projective lifts of each such S have nonzero trace. Their
  normalized trace modulus is 2^(-k/2).
* Every rank-one S is the transvection associated with a unique nonzero
  binary Pauli label v. Its two nonzero-trace lifts are C_P and C_P^(-1),
  where P is a Hermitian Pauli with label v and

      C_P = ((1+i)I + (1-i)P)/2.

The last item also follows directly from C_P's Pauli conjugation action:
C_P^2=P, its symplectic action is that transvection, and the cited lift
count is two. The two projective lifts are distinct because P is nonscalar.

The cited count and trace formula bound the absolute row contribution at
each displacement rank k, when f>=2N+4, by

    2^k c_(N,k) 2^(-kf/2) <= 2^(-k(k+1)/2).          (3)

Set T=sum_(k>=1) 2^(-k(k+1)/2). The exact rational upper tail certificate
in #5694 gives

    T <= T_plus = 2670177/4161536.

Javier Vera's #5714 proves that T is the limiting absolute row sum, and
explicitly leaves spectral improvement open. We change the treatment of
rank one, rather than strengthen that asymptotically sharp count.

## 1. Seven commuting quarter turns

Take three independent commuting Hermitian Paulis P_1,P_2,P_3. For each
nonzero a in F_2^3 put P_a=product_j P_j^(a_j) and C_a=C_(P_a).
The seven C_a commute and have fourth power I. Moreover,

    product_(a!=0) C_a = I.                            (4)

To see this, simultaneously diagonalize the three commuting involutions.
Write their joint eigenvalues as (-1)^(x_j). On this eigenspace C_a has
eigenvalue i^(a dot x). If x=0 all seven exponents vanish. If x!=0,
exactly four a have a dot x=1, so the product is i^4=1.

This relation holds as an exact operator identity, before taking a
projective quotient. For a general isotropic label space, choosing the
signed products P_a is essential. Arbitrary independent sign choices
need not give (4).

Let R be any unitary representation of the projective Clifford group.
The seven R(C_a) still commute, have fourth power I, and have product I.
On a simultaneous eigenspace their eigenvalues lambda_a are fourth roots
with product one. Therefore

    sum_(a!=0) (lambda_a + conjugate(lambda_a)) >= -10. (5)

Here is an elementary proof. Each summand belongs to {-2,0,2}. A sum
below -10 is either -14, requiring seven eigenvalues -1, or -12,
requiring six eigenvalues -1 and one eigenvalue i or -i. Their products
are respectively -1 and i or -i, contradicting product one. Six -1
and one +1 give -10 and product one, so this root constraint alone
cannot give a larger constant. Thus, in operator order,

    sum_(a!=0) (R(C_a)+R(C_a)*) >= -10 I.              (6)

## 2. Average over Clifford conjugation

For each of the m=2^(2n)-1 nonzero unsigned Pauli labels v choose a
Hermitian representative P_v and define

    A = sum_(v!=0) (R(C_(P_v))+R(C_(P_v))*).

The pair of summands is independent of the sign choice. Indeed
C_(-P)=i C_P^(-1), so their projective classes are inverses. Clifford
conjugation acts transitively on the nonzero labels, and consequently
averaging a conjugate of the left side of (6) gives (7/m) A. Every
conjugate obeys the same operator inequality. Hence

    A >= -(10/7) m I.                                 (7)

This is the new step. The absolute row bound for this adjacency operator
would only give A>=-2m I. Its lower coefficient improves by the factor 5/7.
We assert a sufficient bound, not the exact full-group minimum eigenvalue.

## 3. Apply the bound to the tensor Gram matrix

First take f_0=4n+4. Since n is odd, f_0 is divisible by eight. Its
Gram kernel is well-defined on the projective group because the exact
scalar kernel has order four. Choose the right-regular convention
(R(a)b)(g)=b(ga). Then the kernel convolution has entries
G_(f_0)[g,h]=(tr(U_g*U_h)/D)^(f_0). Products of representatives can differ
by a scalar fourth root, whose f_0-th power is one.

For C_P and its inverse,

    tr(C_P)/D = (1+i)/2,
    (tr(C_P)/D)^(f_0) = 2^(-f_0/2) = w > 0.

Thus the complete displacement-rank-one contribution is exactly w A in
the right-regular representation. All other nonidentity nonzero-trace
contributions have displacement rank at least two. Write

    G_(f_0) = I + w A + H.

The remaining matrix H is Hermitian. Equation (3) bounds its absolute
off-diagonal row sum by T-1/2, so H>=-(T-1/2)I. This uses the elementary
inequality 2|b_g b_h|<=|b_g|^2+|b_h|^2 in its quadratic form.
Meanwhile (7) and m<2^(2n) give

    w A >= -(10/7) m 2^(-2n-2) I >= -(5/14) I.

Combining the two bounds yields

    G_(f_0) >= (1-5/14-(T-1/2)) I
             = (1-T+1/7) I
             >= (1-T_plus+1/7) I
             = (14601049/29130752) I.                 (8)

The improvement over #5694's rational lower constant is exactly 1/7
in this odd-axis domain. The new constant exceeds 1/2 by
35673/29130752. No sharpness for the complete Gram matrix is claimed.

For later widths, G_(f+1)=G_f entrywise-multiplied by G_1. The matrix G_1
is positive semidefinite with diagonal one. If G_f>=gamma I, its entrywise
product with G_1 preserves the same lower bound. Explicitly, write
G_1=sum_j v_j v_j*. Then

    (G_f-gamma I) entrywise-multiplied by G_1
      = sum_j diag(v_j)(G_f-gamma I)diag(v_j)* >= 0.

This proves (1) at every f>=f_0. It also explains why the projective
convolution argument only needs to be used at the initial width.

## 4. Scope, finite evidence and remaining questions

The written argument supplies all odd n>=3 and all f>=4n+4. The finite
verifier checks its new local ingredients, not those universal quantifiers
or the cited predecessor counts. In F_2^6 it enumerates every isotropic
three-space and checks uniform point incidence. For a chosen signed basis
in each space it applies all seven literal 8-by-8 quarter turns to every
input basis column, using Gaussian integers and an explicit denominator.
An abstract fourth-root enumeration and a separate 512-character diagonal
subgroup calculation both give minimum -10. Wrong words and the excluded
phase residue supply rejection controls. The emitted receipt binds the
package and cited input bytes by SHA-256.

For the diagonal calculation the three coordinate turns generate the
three order-four single-axis phases. The turn on e_i+e_j, divided by
the two coordinate turns, gives the order-two controlled phase on i,j.
These six independent parameters give Z4^3 x Z2^3. The turn on v has
coordinates (v_i; v_i v_j), since binary parity modulo four is
sum_i v_i x_i - 2 sum_(i<j) v_i v_j x_i x_j. Thus the 512 parameter
choices in the verifier enumerate all characters of this subgroup.

The even-n initial width is congruent to four modulo eight. Its rank-one
coefficient is negative, so the lower bound (7) is the wrong side of the
inequality there. The verifier's trivial-character control detects this
sign distinction. We make no improved claim for that starting width.

No one-/two-axis spectrum is recomputed. No complete caller, native cost,
owned-state restoration, finite compiler, precision/tape, stock, outer
bound, new kappa or complete multiplication theorem is supplied.

## Credit

Javier Vera / #5714 supplies the explicit spectral-strengthening question
and the sharp limitation of the absolute row method. Hiroki KUMAZAKI /
#5694 supplies the rank count and rational tail certificate. Ali Romman /
#5526 supplies the trace-lift and projective Gram framework. Their classical
symplectic, Pauli and Clifford provenance and retained native/kernel credit
remain with the pinned source packages. The seven-rotation operator bound,
conjugation average and resulting odd-axis constant are the new step here.
No global literature-priority claim is made.
