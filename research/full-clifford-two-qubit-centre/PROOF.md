# Sharp two-qubit full-Clifford tensor threshold and conditioning

Let G be the group of all two-qubit unitary Clifford matrices with entries in
Z[i,1/2]. Its scalar subgroup is Z={I,iI,-I,-iI}. Choose one representative U_a
of each projective class a in G/Z, and, for positive integer f, put

    H_f(a,b) = (tr(U_a^* U_b)/4)^f.

This is the Gram matrix of the unit Hilbert-Schmidt vectors
U_a^{tensor f}/2^f. Changing representatives conjugates H_f by a diagonal
unitary, so its spectrum, rank and condition number are intrinsic.

**Theorem.** There are 11,520 classes. Their pointwise tensor-independence
threshold is exactly 9. For every f>=9,

    (315/1024) I <= H_f <= (9855/4096) I.

Both constants and the resulting uniform Gram condition bound 219/28 are
optimal, attained at f=9. The condition number of the synthesis map itself
is the square root of this Gram condition number.

## 1. Authenticate the finite alphabet

Use S=diag(1,i), V=((1+i,1-i),(1-i,1+i))/2 on either qubit, and CNOT with
basis map (a,b)->(a,b+a). The verifier stores 2U as a pair of 4-by-4 integer
matrices, enumerates their generated group by exact multiplication, and
checks all 46,080 elements are unitary. It checks that the five generators
normalize the signed two-qubit Pauli matrices and that quotienting by the
four scalar phases gives 11,520 distinct matrices.

This exhausts the full projective Clifford group, rather than a selected
subalphabet. An ordered symplectic basis of F2^4 has
15*8*3*2=720 choices: choose a nonzero first vector, a vector pairing to one,
then a nonzero vector and its partner in their two-dimensional orthogonal
complement. Each symplectic action has at most 2^4 signed Pauli actions.
An operator's signed Pauli action determines it up to scalar, because the
Pauli matrices span the full matrix algebra. Thus there are at most
720*16=11,520 projective normalizers; the enumeration attains this bound.

A scalar in Z[i,1/2] of modulus one is a Gaussian unit: write it as
(a+bi)/2^k and repeatedly use a^2+b^2=2^(2k) modulo four to divide a,b by
two. At k=0 only the four units remain. The enumerated four lifts therefore
also exhaust the Gaussian-dyadic scalar kernel. No eighth-root scalar is
silently identified with one.

## 2. Reduce the Gram to the centre, retaining scalar residue

On all of G, define the unnormalized matrix

    C_f(x,y) = tr(x^* y)^f.

Its kernel is a central function of x^-1 y. Hence C_f is central convolution
in the finite group algebra, a semisimple algebra over C. Its eigenvalues
occur already in its action on class functions: each simple matrix block
has one central scalar, represented by its central idempotent. This is the
standard finite-group regular representation, not a numerical approximation.

The verifier obtains all 59 conjugacy classes by closure of conjugation by
the five generators. For class representatives x_j and classes K_k, the
matrix on class functions is exactly

    M_f(j,k) = sum_{y in K_k} tr(x_j^* y)^f.             (1)

Every sum is recomputed from the literal integer matrices. No class table or
character table is imported. The range has scalar character
v(ix)=i^(-f) v(x). Orbiting the classes by multiplication by i and retaining
this character reduces (1) to R_f of dimensions 21,11,16,11 for f modulo
four equal to 0,1,2,3. Incompatible shorter scalar orbits contribute zero.
The verifier checks the entire 59-row invariance equation M_f B=B R_f.

The other scalar sectors are zero. Grouping the four lifts of each
projective representative gives C_f/4^f as an outer product of a four-component
phase vector of squared norm four with itself, tensored with H_f. Consequently the nonzero
scalar-sector spectrum of C_f is exactly 4*4^f times the spectrum of H_f,
with the same multiplicities. There is no additional factor of four in
the projective multiplicities.

## 3. An exact certificate, including regular multiplicities

For each f=1..12, CERTIFICATE.json records the independently regenerated R_f
and a list L_f of distinct integer eigenvalues. The verifier uses unbounded
Gaussian-integer arithmetic to check

    product_{lambda in L_f} (R_f-lambda I) = 0.         (2)

The roots are distinct. Therefore the spectral projectors are the exact
polynomials

    P_lambda = product_{mu != lambda}
                      (R_f-mu I)/(lambda-mu).          (3)

Equations (2)-(3) certify the full spectrum without trusting the exploratory
symbolic eigensolver. The centre action is faithful on the corresponding
central ideal, so these identities also hold for central convolution in
the full regular representation.

For completeness, the regular multiplicity is

    m_lambda = 11520 * (P_lambda)_(0,0).                (4)

Here index zero is the identity scalar orbit. Projecting delta_I to the
scalar sector gives B e_0/4. A central convolution operator has full regular
trace 46080 times its identity coefficient, so its spectral projector has
trace (46080/4)*(P_lambda)_(0,0), giving (4). The verifier evaluates the
integer numerator and denominator of (3), checks exact division, positive
integral multiplicities, their sum 11,520 and the unit-diagonal Gram trace.

The resulting exact ranks for f=1..12 are

    16,136,816,3426,9104,11384,11504,11519,11520,11520,11520,11520.

At f=9 the full projective spectrum is:

| Eigenvalue | Multiplicity |
|---|---:|
| 315/1024 | 16 |
| 2205/4096 | 400 |
| 2835/4096 | 1296 |
| 6615/8192 | 1600 |
| 3465/4096 | 400 |
| 16065/16384 | 4096 |
| 4725/4096 | 2000 |
| 5535/4096 | 1296 |
| 3375/2048 | 400 |
| 9855/4096 | 16 |

All are positive, giving the stated endpoints at nine. There are ten
distinct eigenvalues in an eleven-dimensional central block; a central
multiplicity of two is combined in the regular multiplicity 2000.

## 4. Propagate the bounds and prove sharpness

The identity H_(f+1)=H_f Hadamard H_1 and the Schur product theorem imply

    a I <= H_f <= b I  =>  a I <= H_(f+1) <= b I,

because H_1 is positive semidefinite with diagonal one. Thus the two exact
endpoints at nine bound every f>=9. Their positive multiplicities make
each endpoint and their ratio 219/28 sharp for this uniform range.

There is a particularly short explicit witness against width eight.
The character d(g)=det(g) is +/-1 for every enumerated lift and is invariant
under scalar multiplication by i. The verifier computes by the 24-term
determinant formula, separately from the centre spectral certificate,

    sum_{g in G} d(g) tr(g)^4  = 46080,
    sum_{g in G} d(g) tr(g)^8  = 0,
    sum_{g in G} d(g) tr(g)^12 = 103403520.             (5)

Multiplicativity of d makes the vector (d(g)) an eigenvector of C_f with
eigenvalue the corresponding sum. At width eight it is nonzero and null;
it descends to the 11,520 projective classes. Hence

    sum_a det(U_a) U_a^{tensor 8} = 0.

Its normalized squared Hilbert-Schmidt norm is zero by the Gram identity.
This witness is nonzero at width twelve; no all-width identity follows from
the width-eight cancellation. In particular it is already nonzero at four.
The rank table shows all smaller positive widths also fail independence;
alternatively positive definiteness at any smaller width would propagate
to eight, contradicting (5). The threshold nine is therefore sharp.

For a fixed residual in C[G], the four widths 9..12 suffice to decide its
vanishing at all positive widths: independence separates each projective
coefficient in one scalar residue, and the four-point Fourier transform
separates the four scalar lifts. This is only a sufficient window here;
no optimality among tests using several earlier widths is claimed.

## 5. Arithmetic and scope of the checks

All group and trace arithmetic uses NumPy int64 with explicit integrality,
entry and trace-magnitude checks. For f<=12, |tr(x^*y)|<=4 and every class
sum is bounded by 46080*4^12<2^40; the scalar-basis folds only use 0,+/-1,+/-i.
All relevant int64 intermediate bounds are below 2^63. Spectral polynomial
products and projector numerators then use unbounded Python integers.
There is no floating-point spectral calculation in the verifier.

The verifier also checks 64 literal tensor Gram entries at widths one
through four. Seven controls reject width-eight independence, stronger
spectral/condition constants, an altered class-block coefficient, discarded
imaginary trace phases and persistence of the null witness at twelve.
Normal and optimized/warning-strict modes execute the same checks without
removable assertions. The written finite-group and Schur arguments provide
the all-width step; this is not a proof-assistant kernel certificate.

No three-qubit result, general sharp 4n+1 theorem, physical implementation,
paid caller, supplier admission, precision/tape result, new kappa or selected
frontier change is claimed.

## Attribution

Ali Romman, PR5526, supplies the general pointwise Clifford/phase framework
and its open sharp-width/spectral question. MatShep's PR5549 and PR5594 solve
the one-qubit threshold and spectrum; their unreserved larger-qubit question
motivates this computation. DLamdata's PR5547 and
josecarlosgonzalezroque-design's PR5570 supply distinct scoped audits. Their
retained native/history/Clifford lineage is credited in NOTICE.md. Finite-group
centres, Pauli normalizers, character projectors, tensor Gram identities and
Schur products are classical. New two-qubit enumeration and certificates:
MatShep with substantial OpenAI Codex assistance; Apache-2.0.
