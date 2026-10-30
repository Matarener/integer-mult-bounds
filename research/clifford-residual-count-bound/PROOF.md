# A uniform Clifford Gram bound from nonsingular residual forms

kumagi, with substantial OpenAI Codex assistance. Apache-2.0.

This sharpens the sufficient constant in Ali Romman's
[pointwise-faithfulness proof](../clifford-pointwise-faithfulness/PROOF.md),
PR #5526, Sections 3–5. The tensor-width threshold and operator alphabet
are unchanged. This is a scoped algebraic result, not a multiplication
algorithm or an improvement to the selected κ.

## Statement

Let n >= 1, D = 2^n, and choose one unitary representative U_g of each
projective n-qubit Clifford class. For every integer f >= 4n+4, and arbitrary
complex coefficients b_g chosen at that width,

    α sum_g |b_g|²
      <= D^(-f) ||sum_g b_g U_g^(tensor f)||_HS²
      <= (2-α) sum_g |b_g|²,                         (1)

where

    α = 1491359 / 4161536 > 358367/1000000 > 1/3.

Thus (1/3) I <= Gram_f <= (5/3) I is a convenient weaker statement,
improving the predecessor's sufficient interval [1/9,17/9] at the same
width. It applies to subsets and is invariant under representative phases.
Neither α nor the width threshold is asserted to be spectrally optimal.

More generally, for an integer s >= 0 and f >= 4n+4+2s, the absolute
off-diagonal row sum is at most

    T_s = sum_(k>=1) 2^(-k(k+1)/2-sk).               (2)

Consequently [1-T_s,1+T_s] is a sufficient spectral interval.

## 1. Residual forms, with a fixed coordinate convention

Work over F_2. Let V have even dimension N = 2n and nondegenerate
alternating form ω(x,y) = x^T J y. For S in Sp(V), put W = im(S-I) and
k = dim W. The identity ker(S-I) = W-perp follows from

    ω(x,(S-I)y) = ω((S^(-1)-I)x,y).

Define B on W by

    B((S-I)x,w) = ω(x,w).                            (3)

It is well-defined by that kernel identity. If the left argument has zero
pairing with all w, then x is in W-perp and (S-I)x = 0; hence B is
nonsingular. Expanding S's preservation of ω gives

    B(u,v) + B(v,u) = ω(u,v).                        (4)

For example, with u=(S-I)x and v=(S-I)y, both sides of (4) reduce to
ω(x,Sy)+ω(Sx,y). This also fixes the convention: interchanging the two
arguments of B changes the reconstruction formula.

Choose an ordered basis of W and let E be its N by k column matrix. Write
B for the k by k matrix of the residual form in this basis. Then

    E^T J E = B+B^T,                                 (5)
    S = I + E B^(-T) E^T J.                          (6)

Indeed (3) says B^T a = E^T J x for (S-I)x = E a.
This proves uniqueness of S given (E,B).

Conversely, any injective E and nonsingular B satisfying (5) give a
symplectic S by (6), with displacement rank k. To check symplecticity,
expand S^T J S: the extra middle factor is

    B^(-T) + B^(-1) + B^(-1)(B+B^T)B^(-T) = 0.

The rank follows because E is injective and E^T J is surjective. This
converse is also checked in the finite enumeration, although only the
forward direction and uniqueness are needed for the upper bound below.

## 2. Count embeddings before forms

Let c_(N,k) count S in Sp(V) with rank(S-I)=k. Each S has exactly
|GL(k,2)| ordered bases for W, so the number of pairs (E,B) above is
c_(N,k) |GL(k,2)|.

Fix instead any nonsingular k by k matrix B. Construct the columns
e_0,...,e_(k-1) of E in order. After i independent columns have been
chosen, (5) imposes i linear equations on e_i:

    ω(e_j,e_i) = B_(j,i)+B_(i,j),   0 <= j < i.

The i linear functionals are independent by nondegeneracy of ω and
independence of the previous columns. Thus there are exactly 2^(N-i)
solutions before requiring e_i to lie outside their span, and at most
that many after. Diagonal equations are automatic in characteristic two.
Therefore, for every fixed B, the number of injective E is at most

    product_(i=0..k-1) 2^(N-i) = 2^(Nk-k(k-1)/2).

There are |GL(k,2)| possible nonsingular B. Dividing the resulting pair
bound by the number of bases gives

    c_(N,k) <= 2^(Nk-k(k-1)/2),   1 <= k <= N.        (7)

The cancellation is the improvement: singular forms are never included,
and the count is organized by B before E. In comparison, the predecessor
first chooses W and bounds by all forms with its prescribed symmetrization.
At k=1, (7) is slightly weaker than the exact 2^N-1 transvection count;
the improvement comes from the other ranks. No formula for |GL(k,2)| is
needed, and no independence between choices of E and B is assumed.

## 3. From rank counts to the Gram envelope

We retain the predecessor's signed-Pauli trace argument, restated here to
make the multiplicity and normalization explicit. For a Clifford U with
symplectic Pauli action S, let L=ker(S-I). Conjugation by U on the
Hermitian Pauli basis has trace |tr U|². Its signs at the fixed labels
form a character of L. Their sum is either zero or 2^dim L.

All projective lifts of a fixed S differ by the 2^N Paulis. Their signs
on L run through every character of L, with multiplicity 2^(N-dim L).
Consequently, for rank(S-I)=k, exactly 2^k projective lifts have nonzero
trace, with normalized trace modulus

    |tr U|/D = 2^(-k/2).

For k=0 only the identity projective class contributes; the other Paulis
have trace zero. Relative products U_g^* U_h give the same trace-modulus
distribution about every projective class. Therefore the exact absolute
row sum of the full tensor Gram matrix is

    R_(n,f) = sum_(k=1..N) 2^k c_(N,k) 2^(-kf/2).

Using (7) at f >= 2N+4+2s gives, term by term,

    2^k c_(N,k) 2^(-kf/2)
        <= 2^(Nk+k-k(k-1)/2-k(N+2+s))
         = 2^(-k(k+1)/2-sk).

Extending this finite nonnegative sum to infinity proves (2). Larger
widths, including odd widths, only decrease the absolute row sum.
For a Hermitian matrix with diagonal one and row sum at most t, bounding
each off-diagonal quadratic term by |b_g|²+|b_h|² gives the spectral
interval [1-t,1+t]. This proves the claimed Gram inequalities.

For an exact rational constant, keep k=1,...,5 in T_0. The first omitted
term is 2^(-21); the ratio of each later term to its predecessor is at
most 2^(-7). Hence

    T_0 <= sum_(k=1..5) 2^(-k(k+1)/2)
                + 2^(-21)/(1-2^(-7))
         = 2670177/4161536 < 2/3.

Subtracting from one gives α in (1). More generally the same cutoff gives
an explicit rational upper bound on T_s, with first omitted term
2^(-21-6s) and tail ratio at most 2^(-7-s). The verifier uses integer
arithmetic and exact fractions for these bounds.

## 4. Consequences and scope

If a unitary Clifford target T is absent from a set of projective classes
S, then at any f >= 4n+4,

    D^(-f) ||T^(tensor f) - sum_(g in S) b_g U_g^(tensor f)||_HS²
        >= α (1 + sum_g |b_g|²) >= α.

Thus its operator norm approximation error is at least sqrt(α), in
particular at least 1/sqrt(3). The implication uses
||A||_HS <= sqrt(D^f) ||A||_op. This is a worst-case unit-input error;
it is not a lower bound on every input's error.

The predecessor's fixed-residual four-width theorem also inherits α.
For its exact Gaussian-dyadic Clifford group, write each exact operator
as i^j U_g and let M = sum_(g,j) |c_(g,j)|² after equal exact operators
are combined. At residue r put β_(g,r)=sum_j c_(g,j)i^(jr). Parseval says
(1/4) sum_(g,r)|β_(g,r)|²=M. Apply (1) separately at the four widths
4n+4,...,4n+7 and average: at least one normalized squared residual norm
is >= α M. Vanishing at all four widths is still equivalent to all
coefficients being zero. The residual coefficients must be fixed across
these tests; pointwise (1) itself permits width-dependent coefficients.

Scalar-phase copies must be combined with the phase raised to f. The
projective Gram bound does not hold for repeated exact-phase copies as
separate columns. Four phase residues are specific to the predecessor's
Gaussian-dyadic scalar group; this is not a four-test theorem for arbitrary
unitary phases or nonunitary scalar multiples.

We do not change the threshold 4n+4, determine sharp one-/two-axis spectra,
improve the rectangular stabilizer-map theorem, or validate any new complete
caller. In particular this is not a new paid-call count, matched QQ16 bill,
physical routing bound, affordable supplier, or selected-frontier admission.
Applying the stronger error constant to an actual caller still requires
checking its full operator alphabet and retained state. No such new source
application is claimed here.

## 5. Evidence and attribution

The written argument proves the all-n statement subject to mathematical
review. The checker independently constructs signed Clifford actions from
literal H, S and controlled-X conjugations, and constructs symplectic maps
from every small residual subspace and nonsingular form. It compares the
entire sets for n=1,2, not just their cardinalities. It also checks trace
multiplicities, exact row sums, rational tails and invalid conventions.
Finite enumeration corroborates the proof; it does not establish its
universal quantifiers or constitute formal-kernel/human acceptance.

The residual-form method is classical. Ali Romman's #5526 supplies the
explicit residual/trace-lift framework and tensor Gram/four-width
consequences reused above; its attribution to earlier stabilizer and
finite-alphabet work remains in the pinned input. The contribution here
is the nonsingular-form-first double count and the resulting improved
uniform constants within this repository, not a literature-priority claim
for residual forms, Clifford counts, Gershgorin bounds or Fourier inversion.
