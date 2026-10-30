# The full Clifford tensor threshold is at least 2n+1

## Statement

Let G_n be the group of n-qubit unitary Clifford matrices with entries in
Z[i,1/2]. Its scalars are the four units i^k. For one representative U_a of
each projective class and positive width f, put

    H_f(a,b) = (tr(U_a^* U_b) / 2^n)^f,

the Gram matrix of the unit vectors U_a^{tensor f}/2^{nf}. Let T(n) be the least
width from which H_f is nonsingular at every larger width. (By the Schur
product step of MatShep's #5675, Section 4, nonsingularity at f persists to
f+1, so T(n) is also the least nonsingular width.)

**Theorem.** For every n >= 2 and every width 1 <= f <= 2n, H_f is singular.
Hence

    2n + 1 <= T(n) <= 4n + 4.

The upper bound is Ali Romman's pointwise theorem (#5526). The lower bound is
new. It is sharp for neither n=2 (T=9, #5675) nor, presumably, larger n; it
proves that T(n) grows linearly, and it gives 7 <= T(3) <= 16.

Two refinements follow from cited code lemmas without new work: for n = 1
modulo four, n >= 5, H_f is singular through f = 2n+2 (#5635, Section 2), so
T(n) >= 2n+3; for n = 2 modulo four, through f = 2n+1 (#5902), so T(n) >= 2n+2.

## 1. A monomial subgroup and a principal submatrix

Let M_n be the input-phase monomial group of Ali Romman's native grammar
(#5369, #5529):

    U(g,q) e_x = i^{q(x)} e_{g(x)},
    q(x) = c + sum_j a_j x_j + 2 sum_{j<k} b_jk x_j x_k  (mod 4),

with g an invertible affine map of X = F2^n. Each U(g,q) is a product of X,
CNOT, S, CZ and a scalar i^c. These are Gaussian-integer Clifford matrices, so
M_n is a subgroup of G_n. Its scalars are again the i^k. Distinct projective
classes of M_n are therefore distinct projective classes of G_n.

Choose the M_n representatives among the G_n representatives. The M_n Gram
matrix is then a principal submatrix of H_f. H_f is positive semidefinite. If
x is a null vector of the principal submatrix, extending x by zeros gives
x^* H_f x = 0, hence H_f x = 0. So **every singular width of the monomial
Gram is a singular width of the full Clifford Gram.**

## 2. A fixed monomial residual that vanishes through width 2n

This section restates the residual of Ali Romman's #5635 (Sections 3 and 4)
and replaces its n = 1 (mod 4) code step by a weaker step valid for every n.

*Cuspidal cancellation (cited).* For n >= 2, let Psi be the sum of the
cuspidal characters chi_theta of GL(n,2) over Frobenius orbits of primitive
characters theta of F_{2^n}^*. By Green's theorem Psi is a genuine integer
character with Psi(1) > 0 and Psi(1) + (2^{n-1}-1) Psi(t) = 0 at a
transvection t. Every nonidentity element of the pointwise stabilizer H of a
hyperplane is a transvection, so the representation has no H-fixed vector and

    sum_{h in gH} Psi(h^{-1}) = 0   for every g.

The element

    A_n = sum_{t in X} sum_{g in GL(n,2)} Psi(g^{-1}) [x -> g x + t]

therefore satisfies rho_f(A_n) e_tuple = 0 for every f-tuple of points of X
whose affine span is proper (#5635, Section 3, eq. (2)).

*Phase projector.* With D the diagonal subgroup and

    E_r = (1/|D|) sum_{c,a,b} i^{-r c} [D_q],   P_r = A_n E_r,

rho_f(E_r) is the projector onto tuples with zero nonconstant phase character
when f = r (mod 4), and is zero otherwise (#5635, Section 4). A tuple
x_1..x_f has zero nonconstant phase character exactly when

    sum_t x_tj = 0 (mod 4),   sum_t x_tj x_tk = 0 (mod 2) for j < k.

*Code step, every n.* Let x_1..x_f have zero phase and full affine span, with
f <= 2n. Append zero points to length N = 2n. This keeps both properties.
The n coordinate rows span a binary code C of length N. Every row weight is
divisible by four and distinct rows meet evenly, so C is self-orthogonal and,
by full linear span, has dimension n. Full affine span also means the all-one
word 1_N is not in C. Every word of C has even weight, so 1_N is orthogonal to
C, and 1_N . 1_N = N = 0 (mod 2). Thus C + <1_N> is self-orthogonal of
dimension n + 1 > N/2, which is impossible. Hence **no zero-phase tuple of
length at most 2n has full affine span**, and

    rho_f(P_r) = 0   for every f <= 2n with f = r (mod 4),

and trivially at the other residues.

*Nonzero residual.* The tuple of length 4n+1 consisting of the zero point and
four copies of each basis vector e_j has zero phase (each column sum is four,
each pair product is zero) and full affine span. Pad with zeros to the width
f* in {4n+1,...,4n+4} with f* = r (mod 4). Only the identity affine map fixes
every point of a full-span tuple, so the diagonal entry of rho_{f*}(P_r) at
this tuple is Psi(1) > 0. Thus P_r is not in the central ideal
I_r = (z - i^r) that every width of residue r annihilates.

## 3. From the residual to a null vector of H_f

Group the terms of P_r by projective class. If U = i^k U_a, then
U^{tensor f} = i^{kf} U_a^{tensor f}. For f = r (mod 4) this gives a class
vector v_r, depending only on r, with

    rho_f(P_r) = sum_a v_r(a) U_a^{tensor f}.

The diagonal entry at width f* is a linear functional of v_r and is nonzero,
so v_r is nonzero. At a width f <= 2n of residue r, rho_f(P_r) = 0, so
sum_a v_r(a) U_a^{tensor f} = 0 and the monomial Gram annihilates v_r. By
Section 1, H_f is singular. This holds for every 1 <= f <= 2n, which proves
the theorem.

## 4. Finite corroboration

`verify.py` uses exact integer and Gaussian-integer arithmetic. It checks:

- the code step exhaustively for n = 2, 3, 4: all 7, 34 and 458 zero-phase
  multisets of size at most 2n lack full affine span; and the explicit
  length-(4n+1) tuple for n = 2..64;
- the cuspidal coset identity on GL(2,2) and GL(3,2), at all 1,194
  (g, hyperplane) pairs, with the degree and transvection values;
- the two-qubit transfer literally. All 3,072 monomial matrices normalize the
  two-qubit Pauli group and form 768 projective classes. For each f = 1..4,
  the class vector of P_{f mod 4} is nonzero (full support, 768 classes) and
  is annihilated by the exact class Gram matrix (tr(U_a^* U_b))^f. Its
  diagonal entry at widths 9..12 is 128 = |D| Psi(1), as predicted;
- three rejection controls: the trivial character, the sign with its
  order-three values negated, and one perturbed coefficient each leave a
  nonzero entry of H_4 v.

The two-qubit null vectors agree with MatShep's ranks at widths 1..4 in #5675
(all below 11,520); that package was not rerun.

## 5. Limits

This is a scoped proof. Green's character theorem enters through #5635 and
is cited, not proof-kernel checked; the finite checks at n = 2, 3 corroborate
it. The theorem does not decide T(3); in particular it neither proves nor
refutes T(3) = 13. It says nothing about the spectral constants of #5594 or
#5675, or about any physical caller, invoice or κ.
