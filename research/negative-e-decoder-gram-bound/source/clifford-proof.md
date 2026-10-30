# Pointwise tensor faithfulness for Clifford and stabilizer maps

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

This is an algebraic result. It supplies no physical implementation or new
kappa. The classical ingredients are stabilizer normal forms, symplectic
residual forms, character orthogonality and the Gram row bound. The new
contribution in this repository is their quantitative pointwise consequence.

## 1. Statements

Let C_n be the unitary n-qubit Clifford matrices with entries in Z[i,1/2].
Its scalar subgroup is {I,iI,-I,-iI}. Choose one representative U_g for
each projective class. Indeed a unit Gaussian-dyadic scalar satisfies
a^2+b^2=4^k with integers a,b. Repeated parity reduction leaves only a
Gaussian unit. Set D=2^n. For n>=1 and every integer f>=4n+4,

    (1/9) sum_g |b_g|^2
      <= D^(-f) ||sum_g b_g U_g^(tensor f)||_HS^2
      <= (17/9) sum_g |b_g|^2.                         (1)

The coefficients are arbitrary complex numbers at this one width. Thus all
the projective tensor operators are linearly independent at every such f.
Any subset has the same bounds. The choice of representative phase does not
change the bounds. The proof also applies to the usual Clifford group with
arbitrary unit scalar phases, after projective classes are combined.

For a fixed residual in the exact dyadic group algebra, the following are
equivalent:

1. Every exact-operator coefficient is zero.
2. The residual vanishes at every positive width.
3. It vanishes at the four widths 4n+4,...,4n+7.

If M is the squared coefficient norm after equal exact operators are
combined, at least one of these four normalized squared norms is >= M/9.
Four tests are necessary for this exact group with arbitrary complex scalar
coefficients. This is a sufficient width bound, not a sharp width threshold.
For n=0 the group is the four scalar phases; widths 1,2,3,4 suffice.

There is a broader result. A nonzero stabilizer map from a binary input
space to a binary output space is a matrix whose vectorization, up to a
nonzero scalar, is a pure stabilizer state. Let N be the total number of
input and output axes. Normalize these vectors to unit length and choose
one per projective class. At every f>=2N+6 their tensor Gram matrix has

    (2/5) I <= Gram_f <= (8/5) I.                     (2)

This includes rectangular maps and Pauli projections. For arbitrary
unnormalized representatives A_g, (2) means

    ||sum_g b_g A_g^(tensor f)||_HS^2
      >= (2/5) sum_g |b_g|^2 ||A_g||_HS^(2f).         (3)

The statements at a single width allow different finite words, different
scalar coefficients and different subsets at each width. They do not infer
all-width equality of a changing family from four tests. Products must
still have the stated columnwise Clifford or stabilizer-map form.

There is a robust consequence. If a unitary Clifford target T is absent
from a set of projective classes S, then for f>=4n+4,

    D^(-f) ||T^(tensor f)-sum_(g in S) b_g U_g^(tensor f)||_HS^2
        >= (1/9)(1+sum_g |b_g|^2) >= 1/9.            (4)

Its operator norm error is therefore at least 1/3. This is a worst-case
unit-input error bound, not a guarantee about the error on each input.
Later widths use the stronger constants in Section 4. In particular the
lower bound on normalized squared error tends to one as f increases.

## 2. Count the stabilizer overlaps

A projective N-qubit stabilizer state has a computational-basis support
which is an affine binary subspace. In coordinates t on its k-dimensional
support, its amplitudes have the form

    2^(-k/2) i^(a.t + 2 sum_(j<l) b_jl t_j t_l),

up to a common phase, where a_j is in Z/4 and b_jl is binary. To see this,
use the diagonal stabilizers to obtain the affine support. Each independent
translation stabilizer fixes an amplitude ratio. Its Pauli phase is an
affine sign on the support. These ratios give linear terms modulo four and
even quadratic terms. Commutation gives consistent mixed differences.
Conversely these amplitudes have N independent commuting Pauli stabilizers:
support-annihilating Z operators and the k translation operators with these
ratios. Thus the description is exact, not an enlarged family.

Fix the state |0^N>. A state has a nonzero overlap of modulus 2^(-k/2)
with it exactly when its support is a k-subspace containing zero. Normalize
its amplitude at zero to be positive. The remaining phase polynomial is
unique. There are

    A_(N,k) = [N choose k]_2 2^(k(k+3)/2)             (5)

such states, including A_(N,0)=1. Here

    [N choose k]_2 = product_(j=0..k-1)
                         (2^(N-j)-1)/(2^(k-j)-1).

There are k coefficients with four choices and k(k-1)/2 coefficients with
two choices. This proves the exponent in (5). The other states have zero
overlap. Clifford conjugation is transitive on pure stabilizer states, so
the same distribution holds about every projective stabilizer state.

Transitivity can also be seen directly: a basis change puts the support
on coordinate axes, a translation removes its offset, diagonal Clifford
phases remove its phase polynomial, and Hadamards send its uniform support
to zero. This argument does not use a counting formula for the Clifford
group.

It follows that the absolute off-diagonal row sum of the f-fold tensor
Gram matrix of all these states is exactly

    S_(N,f) = sum_(k=1..N) A_(N,k) 2^(-kf/2).        (6)

An arbitrary subset has no larger row sum. This count concerns projective
states. Repeating scalar-phase copies would make a pointwise Gram singular.

## 3. The Clifford first-overlap improvement

Vectorize U/sqrt(D) to obtain its unit Choi state on 2n qubits. It is a
stabilizer state: the Bell state is a stabilizer state and Clifford action
on one half preserves that property. Projectively different matrices give
different projective Choi states. Formula (5), with N=2n, therefore bounds
their overlap counts.

For k=1 the Clifford count is exactly

    B_(n,1) = 2(2^(2n)-1) = A_(2n,1)/2.             (7)

Here is a separate proof which retains the signs. Let S be the symplectic
Pauli action of U, and L=ker(S-I). In the Hermitian Pauli basis, conjugation
has trace |tr U|^2. Its contribution at a fixed label v is its sign epsilon(v).
On L these signs form a character: conjugation cancels the same Pauli
multiplication phase on both sides. Thus |tr U|^2 is either zero or
2^dim(L).

For a fixed S, its projective Clifford lifts differ by the 2^(2n) Paulis.
They multiply the sign on L by every character of L, each with multiplicity
2^(2n-dim(L)). Therefore exactly 2^k lifts have nonzero trace when
rank(S-I)=k. Their normalized trace modulus is 2^(-k/2).

A rank-one symplectic displacement is a transvection. Indeed, write
(S-I)x=ell(x)a for nonzero a. Symplecticity gives
ell(x) omega(a,y)+ell(y) omega(x,a)=0. Nondegeneracy then forces
ell(x)=omega(x,a) over F_2. Every nonzero a gives one such map. There are
2^(2n)-1 choices, and each has two nonzero-trace lifts. This proves (7).

For clarity, a second count gives the same general upper bound without
Choi states. Put W=im(S-I), dim W=k. Then ker(S-I)=W-perp. The residual
form B((S-I)x,w)=omega(x,w) is well-defined, nonsingular and satisfies
B(u,v)+B(v,u)=omega(u,v). For fixed W there are at most
2^(k(k+1)/2) bilinear forms with this fixed symmetrization. Each nonsingular
one determines S uniquely: solve B((S-I)x,w)=omega(x,w) for every w in W.
There are [2n choose k]_2 possible W and 2^k nonzero-trace Pauli lifts.
Their product is exactly A_(2n,k). No equality is asserted for k>=2.

The Choi and residual-form arguments are different derivations of the same
upper bound. The checks enumerate signed Pauli actions and literal Choi
vectors separately.

## 4. Uniform rational row bounds

Set d_k=product_(j=1..k)(2^j-1). The subspace count satisfies

    [N choose k]_2 <= 2^(k(N-k)) /
                           product_(j=1..k)(1-2^(-j)).

At f=2N+4, its term in (6) is at most 1/d_k. The Clifford first term is
at most 1/2 by (7). Its whole off-diagonal row sum is consequently at most

    1/2 + 1/3 + 1/21 + 1/315
        + (1/9765)/(1-1/63) < 8/9.                  (8)

The tail starts at k=5. Each subsequent term has ratio at most 1/63.
The bound is independent of n. Terms with k>2n were added only to bound
the finite sum from above. At all larger widths the row sum can only fall.

For all stabilizer states use f=2N+6. Each term is at most 2^(-k)/d_k,
so the full row sum is at most

    1/2 + 1/12 + 1/168 + 1/5040
        + (1/312480)/(1-1/126) < 3/5.               (9)

Again this is a rational bound on the complete infinite tail. The executable
also provides the sharper finite sums for any specified axis count and any
even width. For an odd width it uses the preceding even width. A failed
sufficient bound is no decision, not evidence of linear dependence.

If a Hermitian matrix has diagonal one and absolute off-diagonal row sums
at most s, then its eigenvalues lie in [1-s,1+s]. One direct proof bounds
each pair by 2|b_i b_j| <= |b_i|^2+|b_j|^2 in its quadratic form.
Apply this to the Gram matrices and (8)-(9). This proves (1)-(3).
Apply (1) to the residual with target coefficient one to obtain (4).
The inequality ||R||_HS <= sqrt(D^f)||R||_op gives its operator norm claim.

There are useful stronger bounds at a slightly later width. At
f=4n+4+2s the Clifford row bound is at most

    2^(-s-1) + sum_(k>=2) 2^(-sk)/d_k.              (10)

For s=2 this is <3/20. For s=6 it is <1/126.
Thus four consecutive widths starting at 4n+8 have a 17/20 lower bound;
four starting at 4n+16 have a 125/126 lower bound. The same geometric-tail
argument proves these constants. These are sufficient constants, not
optimal spectral values.

## 5. Exact phases and the four-width theorem

For the Gaussian-dyadic group write every exact matrix uniquely as i^j U_g,
where g is its projective class and j=0,1,2,3. For a fixed residual define

    beta_(g,r) = sum_(j=0..3) c_(g,j) i^(jr).

At any f>=4n+4 with f=r modulo four, (1) says that the residual is zero
exactly when all beta_(g,r) vanish. This is the exact pointwise kernel:
only the unavoidable scalar-phase relations remain. Four consecutive
widths supply all four residues. Fourier inversion then makes every
c_(g,j) zero.

Parseval gives (1/4) sum_(g,r)|beta_(g,r)|^2=M. Averaging (1) over the
four tested widths proves the M/9 claim. Formula (10) gives the two stronger
four-width constants stated above. Apply the argument to each entry of a
complete input-to-output register matrix; every dirty role must be retained.

For each r the residual sum_(j=0..3) i^(-rj)[i^j I] vanishes at every width
outside r modulo four and is 4I in that residue. Thus three widths cannot
be a universal fixed-residual test. The same argument gives eight necessary
residues if a chosen finite normalized Clifford lift includes eighth-root
scalar phases. The four-test conclusion is for the repository's exact
Gaussian-dyadic group, not that larger central extension.

## 6. Quantifiers, applications and exclusions

At a single specified f>=4n+4, the coefficient vector may be chosen after
f. Its entries may be arbitrary complex numbers. Its finite support and
the finite word that produces it may also depend on f. There is no term
count in the theorem. Thus an equality at that width can be read as an
identity in the projective phase quotient of the group algebra. A scalar
phase is evaluated as its f-th power, not discarded.

This gives an explicit threshold for future applications of the retained
finite-alphabet tensor-separation arguments. It replaces an unspecified
large width or a projective-group-size bound when the entire operator
alphabet in the argument is contained in this fixed n-axis Clifford group.
For n=9 the pointwise threshold is 40 and the four test widths are 40..43.
For n=17 they are 72 and 72..75. At n=64 they are 260 and 260..263.
The prior full-Clifford fixed-residual tests are 69..76, 133..140 and
509..516 respectively. These comparisons are theorem bounds, not measured
execution speedups.

The [retained passive application](APPLICATION.md) meets the full alphabet
premise. It gives a uniform width-72 obstruction and an operator error bound
of 1/3 under that exact passive contract. Its sources and both mandatory
clarifications are retained as byte-pinned inputs.

For stabilizer maps, terms which differ by any nonzero scalar must first be
combined with that scalar raised to f. Their coefficients may then depend
on f. Formula (3) does not identify scaled copies at all widths, and it does
not give four tests for arbitrary nonunitary scalings.

This does not by itself strengthen an additional-call bound at a caller
cut with already paid observations. That needs its correct initial module,
source versions, ownership and cost ledger. Nor does it show that any
particular paid-history theorem's whole alphabet consists of Clifford
maps. A nominal matrix or a sum of Cliffords is not automatically a
Clifford or a stabilizer map. Each application must check that premise.

Arbitrary non-Clifford matrices, nonlinear/rounded operations, operators
which act across tensor columns, unpriced physical routing, and omitted
dirty returns remain outside the result. No all-size multiplication
assumption is declared discharged by this algebraic theorem alone.

## 7. Verification and attribution

The registered verifier checks the finite counting identities by separate
state and signed-Pauli enumerations, the rational tail bounds, literal Gram
matrices, complete native register examples and deliberate invalid inputs.
The written proof supplies the all-dimension and all-width quantifiers.
Finite computation is corroboration; it is not a formal-kernel proof or
independent human acceptance.

The retained tensor-Gram package supplies the exact native grammar, compact
quadratic sums and complete register frontend. Its original trace filter,
code invariant, one-axis sharpness and provider results remain its work.
The monomial tensor-cutoff package remains a stronger cutoff for its smaller
class. Chris R and the retained paid-history authors supply the earlier
finite-alphabet applications. Krzysztof Wojt and Nick Petalas supply the
repository's related residual-form and partial-Pauli statements.

Classical stabilizer descriptions follow Dehaene and De Moor,
[*Clifford group, stabilizer states, and linear and quadratic operations
over GF(2)*](https://arxiv.org/abs/quant-ph/0304125). The finite symplectic residual-form
method is classical Wall-form theory. No general counting, Gram, Fourier,
stabilizer-simulation or literature-priority claim is made. Exact repository
pins and the role of each source are in SOURCES.json and README.md.

## Open next questions

Find the least pointwise threshold and best spectral constant for this
group, with the phase residue kept explicit. Test one actual complete
caller against the new pointwise kernel, retaining its available history
and complete bill. Extend the exact native frontend to a source-bound
nonunitary stabilizer caller only when its projections and scalar factors
are supplied. None of these follow-ups is claimed complete here.
