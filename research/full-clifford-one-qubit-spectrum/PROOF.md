# Exact one-qubit full-Clifford tensor spectrum

Prepared for MatShep with substantial OpenAI Codex assistance. Apache-2.0.
This is an author-checked algebraic proof with a finite exact certificate,
not independent human or proof-assistant acceptance.

## 1. Object and statement

Let `U_g`, `g=1,...,24`, represent the full projective one-qubit Clifford
group with Gaussian-dyadic entries, and let

    H_f(g,h) = (tr(U_g* U_h)/2)^f,    f a positive integer.

Here `*` is conjugate transpose. This is the Gram matrix of
`2^(-f/2) vec(U_g^(tensor f))`. Representative phase changes conjugate
`H_f` by a diagonal unitary and do not change its spectrum. Put

    s = 2^(-floor((f-1)/2)).

Its complete spectrum is the following multiset (multiplicities add when
values coincide):

| Width parity | Eigenvalue | Multiplicity |
|---|---|---:|
| odd | `1-s^2` | 16 |
| odd | `1+2s^2-3s` | 4 |
| odd | `1+2s^2+3s` | 4 |
| even | `1-s^2` | 4 |
| even | `1-s` | 9 |
| even | `1+s` | 9 |
| even | `1+2s^2-3s` | 1 |
| even | `1+2s^2+3s` | 1 |

Consequently, for every `f>=5` and arbitrary complex coefficients `b_g`,

    (3/8) sum_g |b_g|^2
      <= 2^(-f) ||sum_g b_g U_g^(tensor f)||_HS^2
      <= (15/8) sum_g |b_g|^2.

Both constants are optimal uniformly on this width range and attained at
each of widths 5 and 6. The Gram spectral condition number is at most 5,
with equality at both widths; the corresponding synthesis map has
condition number at most `sqrt(5)`. The eigenvalues converge to one.

This answers the one-qubit part of the best-spectral-constant question in
Ali Romman's PR5526. MatShep's PR5549 already supplies the sharp independence
threshold 5; that rank threshold is prior work.

## 2. Finite group and certificate

Use `S=diag(1,i)` and
`V=((1+i,1-i),(1-i,1+i))/2`. The verifier stores `2U` as four Gaussian
integer pairs. Closure under right multiplication by these two generators
has 96 exact matrices. All are unitary signed-Pauli normalizers, with 24
different signed actions. Quotienting by `1,i,-1,-i` gives 24 classes.

These exhaust the full projective Clifford group: the image of X has six
signed-Pauli choices and its anticommuting Z image has four. A signed action
determines a matrix up to scalar. A unit scalar in `Z[i,1/2]` is a Gaussian
unit: after clearing dyadic denominators, parity reduction in
`a^2+b^2=4^k` leaves only the four possibilities. Thus the exact group and
phase quotient are the stated ones, as in PR5526/5549.

Write `t_gh=tr(U_g* U_h)`. Each off-diagonal row has six entries of squared
modulus 2, eight of squared modulus 1, and nine zeros. Define zero-diagonal
Hermitian matrices `A_r,B_r`, for `r=1,2,3,4`, by retaining respectively
`t_gh^r` on the squared-modulus-2 and squared-modulus-1 positions.
The exact Gaussian values satisfy

    t^4=-4 on A positions,    t^4=1 on B positions.

Hence, for every integer `k>=0`,

    H_(r+4k) = I + 2^(-r-4k) [(-4)^k A_r + B_r].       (1)

This entrywise identity supplies the all-width step; testing finitely many
widths alone would not supply it.

The exact joint spectral certificate is:

| r | A eigenvalue | B eigenvalue | Joint dimension |
|---:|---:|---:|---:|
| 1 | +6, -6 | 4 | 4 each |
| 1 | 0 | -2 | 16 |
| 2 | +12, -12 | 8 | 1 each |
| 2 | +4, -4 | 0 | 9 each |
| 2 | 0 | -4 | 4 |
| 3 | +12, -12 | 4 | 4 each |
| 3 | 0 | -2 | 16 |
| 4 | +24, -24 | 8 | 1 each |
| 4 | +8, -8 | 0 | 9 each |
| 4 | 0 | -4 | 4 |

The table has a small independently checkable certificate, rather than a
floating-point diagonalization. For odd r set `P=(B+2I)/6`, `Q=I-P`,
`K=6*2^((r-1)/2)`. Its projectors are `Q` and `(P +/- A/K)/2`.
For even r set

    P8 = B(B+4I)/96,
    Pm4 = B(B-8I)/48,
    P0 = I-P8-Pm4,
    K8 = 3*2^(r/2+1),    K0=2^(r/2+1).

Its projectors are `Pm4`, `(P8 +/- A P8/K8)/2`, and
`(P0 +/- A P0/K0)/2`. For each r the verifier checks that A and B commute;
each listed projector is Hermitian and idempotent; they sum to I; its trace
is the listed dimension; and left multiplication by A and B gives the
listed eigenvalues. Distinct joint eigenpairs of commuting Hermitian
matrices have orthogonal eigenspaces. These rational matrix identities
therefore prove the complete table.

Substitution in (1) proves the spectrum in Section 1 for every positive
width. A separate Newton-trace characteristic-polynomial calculation at
widths 1 through 10 corroborates it without using the projectors. Literal
tensor vectors independently check every Gram entry at widths 4, 5 and 6.

For `f>=5`, `0<s<=1/4`. The smallest and largest eigenvalues in the table
are `(1-s)(1-2s)` and `(1+s)(1+2s)`. The former increases and the latter
decreases as s decreases in this interval, giving 3/8 and 15/8 at s=1/4.
All nonzero spectral subspaces have their stated multiplicities, so the
bounds and condition number are attained. The saved rational eigenvectors
give explicit extremizers at widths 5 and 6. At width 4 a saved nonzero
null vector prevents extending a positive uniform lower bound to that width.

## 3. Sharp missing-class Hilbert-Schmidt distance

For `f>=5`, fix a target class g and allow every other class with arbitrary
complex scalar coefficients. The best normalized squared distance is

    delta_f = min_(c_g=1) c* H_f c = 1/(H_f^(-1))_gg.    (2)

Indeed Cauchy-Schwarz for the H inner product gives
`|c_g|^2 <= (c*Hc)(H^(-1))_gg`. Equality is attained at
`c=H^(-1)e_g/(H^(-1))_gg`. The other coefficients give the negative of
the optimal approximation to the target.

Projective left multiplication permutes the classes and changes phases.
It conjugates H by a monomial unitary, so the diagonal entries of its
inverse are equal. They are therefore `tr(H^(-1))/24`. Summing the
reciprocals of the spectrum gives

    delta_f = (1-s^2)(1-4s^2)/(1-2s^2),       f odd;
    delta_f = 2(1-s^2)(1-4s^2)/(2-7s^2),     f even.    (3)

In particular `delta_5=45/56` and `delta_6=9/10`. The verifier checks the
full inverse, every inverse diagonal and every omitted-class extremizer at
widths 5 through 8, and constructs the literal tensor residual at 5 and 6.

For completeness the uniform lower bound needs no extrapolation from these
four values. Equation (2) is equivalent to `H_f >= delta_f e_g e_g*`.
Since `H_(f+1)=H_f Hadamard H_1`, the Schur product theorem and the unit
diagonal of `H_1` imply
`H_(f+1) >= delta_f e_g e_g*`. Thus `delta_(f+1)>=delta_f`.
The exact value at width 5 proves the optimal uniform floor **45/56**.
Allowing fewer than the other 23 classes cannot decrease this distance.
The normalized Hilbert-Schmidt inequality also implies worst-case operator
error at least `sqrt(45/56)`, but no sharpness of that operator-norm bound
is claimed. A Hilbert-Schmidt extremizer need not be operator-norm optimal.

## Scope and remaining obligations

All coefficients at one width may depend on that width. Scalar-phase copies
must be combined projectively with their actual f-th-power phases. There
are not 96 independent columns at a single width. The result is an exact
one-qubit algebraic statement, not a larger-qubit extrapolation, physical
native circuit, paid-return construction, supplier admission, precision or
tape result, new kappa, selected-frontier update or multiplication theorem.
No selected cold replay is required or claimed for this isolated package.

The Pauli normalizer, Schur product theorem, spectral projectors,
least-squares identity and group covariance are classical. No global
literature-priority claim is made. Credit Ali Romman's PR5526 quantitative
framework and explicit open question, MatShep's PR5549 enumeration/rank
threshold, DLamdata's PR5547 core audit and josecarlosgonzalezroque-design's PR5570 bridge
audit, with their retained predecessor and native/controller lineage.
