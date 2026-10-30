# Chebyshev inverse locality under the retained conditioning contract

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof. The Chebyshev identities and
normal-equation approximation method are classical. The new contribution is
the explicit replacement of the Gaussian caller's locality parameters under
its existing conditioning hypotheses. No global literature priority is claimed.

The general approximation-based inverse-decay method also predates this
application. Credit Stephen Demko, William F. Moss and Philip W. Smith,
[Decay rates for inverses of band matrices, 1984](https://doi.org/10.1090/S0025-5718-1984-0758197-9).
The argument below gives the explicit residual and exact section-row interface
needed here; it does not claim a new general inverse-decay theorem.

## The polynomial

Let H be an invertible finite complex square matrix with

    ||H||_2 <= K,    ||H^-1||_2 <= K,    K > 1.

Write A=H*H. Its eigenvalues lie in [K^-2,K^2]. For any integer d>=1 put

    c = (K^4+1)/(K^4-1),
    t(x) = (K^4+1-2K^2 x)/(K^4-1),
    R_d(x) = T_d(t(x))/T_d(c),
    q_(d-1)(x) = (1-R_d(x))/x,
    B_d(H) = q_(d-1)(H*H) H*.

Here T_d is the Chebyshev polynomial of the first kind. Since t(0)=c,
R_d(0)=1. Thus q_(d-1) is a polynomial of degree at most d-1, with no pole
at zero. In particular this definition does not require a matrix inverse.

The classical identity

    T_d((z+z^-1)/2) = (z^d+z^-d)/2

and |T_d(t)|<=1 on [-1,1] follow from the recurrence T_0=1, T_1=t,
T_(j+1)=2t T_j-T_(j-1). They are also recorded in
[NIST DLMF, equation 18.5.1](https://dlmf.nist.gov/18.5.E1).
These identities are premises from classical polynomial theory, not new claims.

## Error for arbitrary nonnormal matrices

The identity x q_(d-1)(x)=1-R_d(x) gives, in the indicated order,

    B_d(H)-H^-1 = -R_d(H*H) H^-1.

Indeed A^-1 H*=H^-1. The spectral theorem applies to the Hermitian A,
regardless of whether H is normal. Since t maps [K^-2,K^2] to [-1,1],

    ||B_d(H)-H^-1||_2 <= K/T_d(c).

Take z=(K^2+1)/(K^2-1)>1. Then c=(z+z^-1)/2, so

    1/T_d(c) = 2/(z^d+z^-d) <= 2 z^-d
              <= 2 exp(-2d/K^2).

For the last inequality put u=K^-2 in (0,1). Integrating
2/(1-u^2)>=2 from 0 to u gives
log((1+u)/(1-u))>=2u. Therefore log z>=2/K^2. This proves

    ||B_d(H)-H^-1||_2 <= 2K exp(-2d/K^2).

No row or column dominance, symmetry of H, Gaussian entry formula or
translation invariance is used in this implication.

## Exact locality and principal sections

Let the indices carry the linear or circular physical distance used by the
caller. Suppose H_ij=0 when the distance between i and j exceeds W.
The same is true of H*. A monomial (H*H)^j H* contains 2j+1 factors,
and each step moves at most W. Hence B_d(H) has physical bandwidth at most

    r = (2d-1)W.

Let S be any principal index set, H_S the corresponding principal matrix,
and i in S. If the distance from i to every omitted index is greater than r,
then the row of B_d(H_S), extended by zero outside S, equals row i of B_d(H)
exactly. Every path contributing to a monomial stays in S: an exit would
reach an omitted index in at most 2d-1 steps of length at most W. The same
coefficients are used in both polynomials, including the same K and d.

This is equality of polynomial rows, not equality of exact inverse rows.
For an inverse-error assertion on H_S, that section must itself satisfy
the norm and inverse-norm hypotheses with the same K. The locality assertion
alone does not require H_S to be invertible. A separately rerounded section,
different K, or a Schur complement is not covered by this row identity.

## Substitution at the Gaussian caller

Use the precise hypotheses of Cinna Davis's
[HALO.md](../unconditional-batched-crt/HALO.md), pinned in SOURCES.json:
p is an integer at least two, W<p, and H and each section used for an inverse
have both norms at most p^10. Set

    K=p^10,    d=p^22.

Then

    ||B_d(H)-H^-1||_2 <= 2p^10 exp(-2p^2) < p^10 exp(-p^2),

because exp(p^2)>2 for p>=2. Furthermore

    r <= (2p^22-1)(p-1) < 2p^23 <= p^24.

Thus a row at distance at least p^24 from every omitted index has exact
polynomial agreement. This replaces the historical Neumann degree p^42
by p^22 and permits the conservative halo p^24 in place of p^48, with a
strictly smaller error than the old p^10 exp(-p^2) majorant. Both the global
matrix and every actual inverted section retain their original assumptions.
The argument does not establish those assumptions for a new matrix.

The predecessor locality work, including Nick Petalas's #4217 and Mihir
Srivastava's #4501, supplies the distinction between polynomial locality,
section inverses and ordered nonnormal error identities. Their Neumann
polynomials and finite examples are not audited or replayed here. The new
polynomial changes the approximation method while retaining the input matrix
class and conditioning contract.

## Exact coefficient construction

For integer K>=2 put D=K^4-1 and L=(K^2+1)^2. Define integer polynomials

    N_0(x)=1,
    N_1(x)=K^4+1-2K^2 x,
    N_(j+1)(x)=2(K^4+1-2K^2 x)N_j(x)-D^2 N_(j-1)(x).

Induction gives N_d(x)=D^d T_d(t(x)), so R_d(x)=N_d(x)/N_d(0).
N_d(0)>0. If N_d(x)=sum a_j x^j, the inverse polynomial's coefficients
are exactly -a_(j+1)/a_0. No numerical root, transcendental coefficient or
unknown inverse entry is needed to construct them.

For completeness, ||N_j||_(coefficient 1-norm) <= (3L)^j. The initial cases
hold since ||N_1||=L. Since D^2<L^2, the recurrence bounds the next norm by

    2L(3L)^j + L^2(3L)^(j-1) = (7/9)(3L)^(j+1).

Thus coefficient numerator and denominator bit lengths are O(d log K).
With d=p^22 and K=p^10 this is polynomial in p. Naive exact recurrence and
local polynomial evaluation therefore give polynomial offline setup, as
required of a locality witness. This is not a practical runtime benchmark
or a charged physical coefficient-page implementation.

## Scope

This proves one conditional approximation and locality improvement. It
supplies no optimized global core geometry, complete tape/precision bill,
rounded implementation, native supplier admission, new kappa, or complete
multiplication theorem. The selected record and all five assumptions remain
unchanged. Coefficient rounding and finite-precision recurrence stability
require their own analysis before replacing a physical implementation.

The finite verifier corroborates identities on bounded rational matrices.
The universal quantifiers above rest on this written proof. Independent
human and formal proof-kernel review are unclaimed.
