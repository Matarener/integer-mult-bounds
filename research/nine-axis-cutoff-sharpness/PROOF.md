# The nine-axis window is sharp

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. The theorem

Retain the input-phase grammar of PR5369 and PR5529 on X=F2^n:

    U(g,q)e_x = i^q(x) e_(g x),
    q(x) = c + sum_j a_j x_j + 2 sum_(j<k) b_jk x_j x_k modulo 4,

where g is affine invertible, c and a_j are modulo four, and b_jk are
modulo two. Let G be this finite monomial group. Work over Q(i) or C.
Let rho_f evaluate each group element at its f-th tensor power; external
coefficients stay fixed. Let z=[iI] and I_r=(z-i^r[1]).

For every n>=5 with n=1 modulo four, put F=2n+3 and

    L_r = F + ((r-F) modulo 4).

Then, for every positive f congruent to r modulo four,

    ker rho_f = I_r  if and only if  f >= L_r.

For n=9, F=21 and (L_0,L_1,L_2,L_3)=(24,21,22,23).
Thus 21,22,23,24 is a sharp four-width test window. Four residue tests
are necessary, and no complete test set can have maximum width below 24.
The corresponding statement for general n has maximum width at least 2n+6.

The upper bound is the retained PR5529 theorem. The new part is a general
lower residual from a code obstruction and a cuspidal character. No
physical cost, supplier, efficient expansion or kappa improvement follows.
This result concerns the complete fixed endpoint grammar, including all
independent inputs and every specified return.

## 2. The zero-phase tuple must be longer than 2n+2

A tuple x_1,...,x_f has zero nonconstant phase character exactly when

    sum_t x_tj = 0 modulo 4,
    sum_t x_tj x_tk = 0 modulo 2 for j<k.

Its n binary row words generate a doubly even code C: every codeword has
weight divisible by four. The row words have zero pairwise dot products,
and wt(u+v)=wt(u)+wt(v)-2|supp(u) intersect supp(v)| proves this assertion
for their whole span. Full affine span of the tuple is equivalent to both
rank(C)=n and the all-one word being outside C. A nonzero linear functional
constant on every tuple point is exactly a row relation or the all-one word.

Suppose f<=N=2n+2. Append zero columns to reach length N. This preserves the
phase conditions and full affine span. Since n=1 modulo four, N=4 modulo
eight. The all-one word 1_N has weight divisible by four and is orthogonal
to C. It is not in C. Therefore C+<1_N> is doubly even, self-orthogonal,
and has dimension n+1=N/2. It is self-dual.

Here is the required elementary obstruction. If a doubly even code D is
self-dual at length N, sum i^wt(x) over F2^N. On the one hand it equals
(1+i)^N. On a coset x+D, it equals

    i^wt(x) sum_(d in D) (-1)^(x.d).

This sum is zero unless x belongs to D-perp=D. The only contributing coset
is D, and its sum is |D|=2^(N/2). Thus (1+i)^N=2^(N/2), which requires
N divisible by eight. This contradicts N=4 modulo eight. Consequently no
zero-phase tuple of length at most 2n+2 has full affine span.

This is a classical doubly-even code argument. Missing full affine span
alone is not a representation-kernel lower bound. Section 3 supplies that
additional step.

## 3. A nonzero integer affine cancellation element

We use the following established part of Green's character theory. A
regular multiplicative character theta of F_(2^n)^* gives a genuine
irreducible complex character chi_theta of GL(n,2). Frobenius orbits give
the same representation. Its degree is

    d_n = product_(j=1)^(n-1) (2^j-1),

and its value at a transvection is -d_n/(2^(n-1)-1). These facts follow
from the identity and unipotent cases of Green's formula. See J. A. Green,
[The characters of the finite general linear groups](https://doi.org/10.1090/S0002-9947-1955-0072878-2),
Trans. AMS 80 (1955), 402-447, and the explicit statement in Dipendra
Prasad, [The Space of Degenerate Whittaker Models for General Linear Groups over a Finite Field](https://www.math.iitb.ac.in/~dprasad/imrn.pdf),
IMRN 2000 no. 11, Section 2, pages 581-582, Theorem 2.

Take all primitive characters theta of order 2^n-1, one representative
per Frobenius orbit, and sum their chi_theta. Call the resulting genuine
character Psi. Each orbit has length n: a smaller positive power 2^j
cannot equal one modulo 2^n-1. There are phi(2^n-1)/n such orbits. Green's
formula places their values in the corresponding cyclotomic field, and
Galois automorphisms permute this set. Hence Psi is rational valued.
Character values are algebraic integers, so Psi is integer valued.
Its degree Psi(1) is positive.

Let H be the pointwise stabilizer of a linear hyperplane. Over F2 its
size is 2^(n-1); every nonidentity element is a transvection. Thus

    sum_(h in H) Psi(h) = Psi(1) + (2^(n-1)-1) Psi(transvection) = 0.

For a representation with character Psi, the average of its H matrices
is the projection onto its H-fixed space. Its trace is zero, so this
projection is zero. Therefore, for every g,

    sum_(h in gH) Psi(h^-1) = 0.                         (1)

This argument converts two character values into all coset identities;
it does not assume that a zero character sum on H alone gives (1) for an
arbitrary class function. The genuine-representation condition is needed.

Define an element of the affine group algebra by

    A_n = sum_(t in F2^n) sum_(g in GL(n,2)) Psi(g^-1) [x -> gx+t].

The pointwise stabilizer of any affine hyperplane is a translation
conjugate of H. Its linear parts give the same hyperplane stabilizer in
GL(n,2), up to linear conjugation. Thus (1) gives zero coefficient sum
on every coset of every affine-hyperplane pointwise stabilizer.

If a tuple lies in a proper affine subspace, choose an affine hyperplane
that contains it. For any possible output tuple, the affine maps that
produce it form a coset of the tuple stabilizer. That coset is a union
of cosets of the hyperplane pointwise stabilizer. Therefore

    rho_f(A_n)e_tuple = 0                               (2)

for every such tuple. The coefficient of the identity affine map in A_n
is Psi(1)>0, so A_n is nonzero.

At n=9, d_n=19923090075 and phi(511)/9=48. Thus Psi(1)=956308323600 and
Psi(transvection)=-3750228720. Their stabilizer sum is zero because H has
255 nonidentity elements. No GL(9,2) enumeration is needed for this proof.
The verifier checks every hyperplane coset in GL(3,2) and GL(4,2) using
explicit instances of this integer character. These finite checks
corroborate the formula; they do not replace Green's theorem.

## 4. Fixed residuals and their first visible widths

Let D be the diagonal phase subgroup. For each residue r, put

    E_r = (1/|D|) sum_(c,a,b) i^(-r*c) [D_q],
    P_r = A_n E_r.

Finite Fourier orthogonality says that rho_f(E_r) is the projector onto
zero nonconstant phase tuples when f=r modulo four, and is zero at every
other residue. Sections 2 and 3 show that rho_f(P_r)=0 at each positive
matching width f<L_r. It also vanishes at every wrong residue. Thus one
fixed residual P_r vanishes at every positive width below L_r.

Write n=4k+1. Use k disjoint copies of the length-eight code with row basis

    11111111, 10101010, 11001100, 11110000,

then one row 1111 on four new coordinates and one final zero coordinate.
The n independent rows have length 8k+5=2n+3. All weights are divisible
by four and all pairwise dot products are even. Their columns form a
zero-phase tuple. The zero column and row rank n give full affine span.
Append zero points to reach L_r; this preserves the nonconstant character.

Only the identity affine map fixes this full-span tuple. Its diagonal
entry under rho_(L_r)(P_r) is exactly Psi(1)>0. Therefore P_r is nonzero
and is outside I_r. Its coefficients lie in Q(i), since Psi is integer
valued. This proves the lower kernel statement over Q(i) as well as C.

## 5. Upper bound and completeness of test sets

The pinned PR5529 argument realizes every nonconstant phase character at
every f>=2n+3 by a tuple with full affine span. It starts with zero and an
adapted binary basis, factors the nonalternating residual Gram form in at
most n columns, corrects the linear phase with two equal points, then pads
with zeros. Finite Fourier separation then gives ker rho_f=I_(f modulo 4).
Its original proof and constructor remain unchanged inputs to this package.

For a fixed residue r, the first width at least 2n+3 is L_r. The upper
bound and Section 4 give the claimed equivalence. The four central ideals
have zero intersection. Hence any test set containing one matching width
at or above each L_r decides all positive widths. Conversely, if a test
set lacks such a width in residue r, the nonzero P_r vanishes on every
one of its tests and fails at L_r. This also proves necessity for infinite
test sets, and gives the sharp maximum-width claim.

## Evidence and limits

The written argument proves the unbounded dimension family. Finite replay
checks the explicit code tuples through 129 axes, all four residue pads,
the exact Gauss-sum contradiction, 38094 small-group cosets, 512 outputs
of the retained upper constructor and four controls. Source files are
hashed before the retained constructor is loaded.

Green's character theorem and the complete PR5529 upper proof are cited
mathematical inputs. They are not proof-kernel checked in this package.
The GL(9,2) residual is defined by a finite formula and is not expanded.
No enumeration of all nine-axis phase characters is claimed. The proof
excludes Hadamards, width-dependent external coefficients, changing
program families and undeclared aliases. It supplies no physical caller,
precision, compiler, stock, movement or outer-transfer result.

Joseph Anglada's PR5542 gives the three-axis code/coset argument. Ali
Romman's PR5622 gives the four-axis affine version. Hiroki KUMAZAKI's
PR5522 and Mihir Srivastava's PR5521 supply the earlier sharpness/audit
line. PR5369 and PR5529 supply the grammar, upper bound and Fourier
interface. The new contribution is the cuspidal affine residual and its
use with the code obstruction to settle the nine-axis case and the whole
n=1 modulo four family. The classical code and character theorems are not
new claims. Retain Jose Manuel, ywz65, Chris R and the native source lineage.
