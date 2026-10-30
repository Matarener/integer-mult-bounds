# Sharp two-sided Schur-descendant closure near the identity

## Result

Let A=I+H be any finite square complex matrix and let 0<=rho<1.
If both induced norms satisfy

    ||H||_1 <= rho,       ||H||_infinity <= rho,

then every principal Schur complement of every principal restriction of A
is S=I+J with

    ||J||_1 <= rho,       ||J||_infinity <= rho.              (1)

The same rho is preserved: it does not grow to
rho+rho^2/(1-rho). Both constants are sharp, even for diagonal matrices
and a nonempty eliminated set. Any finite sequence of principal
restrictions, principal Schur eliminations and simultaneous row/column
permutations retains (1).

The result also holds for the component envelope based on
mu(z)=|Re(z)|+|Im(z)|. This stronger source-compatible statement preserves
the component-sum admission itself, not merely a consequence for usual
complex operator norms. No symmetry, positivity, triangularity,
Toeplitz structure or commuting blocks are needed for the closure theorem.

For the retained parity-triangular source at commit
`203d04313c0cb2b4a4663a5a2d4d407e5a5b6d20`, the local consequences at
rho=1/2 are descendant norm at most 3/2, inverse norm at most 2,
off-diagonal block norm at most 1/2, normalized K/ZK norm at most 1, and
completed shear/inverse norm at most 2. This note does not change the
source compiler, prefix allocation, grids, rounding proof or selected
frontier. Its author-owned compensated-generator implementation is a
separate active task.

## 1. Entrywise majorants and the scalar envelope

The proof works with either

    alpha(z)=|z|, or alpha(z)=mu(z)=|Re(z)|+|Im(z)|.

Both satisfy alpha(1)=1, alpha(-z)=alpha(z), the triangle inequality and
alpha(zw)<=alpha(z)alpha(w). For mu the product inequality follows by
expanding `(a+ib)(c+id)` and bounding
`|ac-bd|+|ad+bc|` by `(|a|+|b|)(|c|+|d|)`.

Apply alpha entrywise to a matrix. Write P=alpha(H), a nonnegative real
matrix. The two envelope bounds mean

    P 1 <= rho 1,       1^T P <= rho 1^T.                   (2)

For alpha=usual modulus these are exactly the induced infinity- and
one-norm conditions. For alpha=mu they define component row/column
envelopes, which dominate the usual induced norms and are
submultiplicative matrix bounds. The proof only uses their nonnegative
row/column budgets; it does not identify a component envelope with a
usual complex induced operator norm.

Let E be the eliminated index set and R the retained index set in an
arbitrary principal restriction, with E and R disjoint. Indices outside
E union R are discarded. Principal restriction only removes nonnegative
terms from (2), so the same budgets hold for every block used below.

The matrix I+H_EE is invertible by its Neumann series. Entrywise triangle
and product inequalities give

    alpha((I+H_EE)^(-1))
       <= sum_(k>=0) P_EE^k = (I-P_EE)^(-1) =: N.          (3)

All series converge, since P_EE has row and column norms at most rho<1;
in particular N is entrywise nonnegative. This uses absolute convergence
of the series, not an assertion that the complex inverse itself is
entrywise positive.

The Schur complement is

    S = I_R + H_RR - H_RE (I_E+H_EE)^(-1) H_ER.

Therefore

    alpha(S-I_R) <= Q := P_RR + P_RE N P_ER.                (4)

The next step retains the shared row/column budgets. Independently
bounding every block by rho loses this information and gives the looser
rho+rho^2/(1-rho) estimate.

## 2. Row and column budgets are preserved

From the eliminated rows of (2),

    P_ER 1_R + P_EE 1_E <= rho 1_E.

Consequently

    P_ER 1_R <= rho (I-P_EE)1_E,

because the difference between the right side and the preceding row
budget is `(1-rho)P_EE 1_E`, which is nonnegative. Multiplying by N>=0
yields

    N P_ER 1_R <= rho 1_E.                                (5)

Use this in (4) and then use the retained rows of (2):

    Q1_R <= P_RR1_R + rho P_RE1_E
          <= rho1_R - (1-rho)P_RE1_E
          <= rho1_R.                                      (6)

This proves the infinity-envelope assertion. It requires only the row
budget, rather than both budgets.

Transposing the entire nonnegative argument proves the column assertion.
Explicitly, the eliminated columns give

    1_R^T P_RE N <= rho1_E^T,

and hence

    1_R^T Q <= 1_R^T P_RR + rho1_E^T P_ER
            <= rho1_R^T - (1-rho)1_E^T P_ER
            <= rho1_R^T.                                  (7)

Combining (4), (6) and (7) proves (1), and also the displayed stronger
row/column slack inequalities. Row-only admission proves the row
conclusion; the column conclusion independently requires its column
admission. The two are not interchangeable for a nonsymmetric matrix.

If E is empty, S is just a principal restriction and the conclusion is
immediate. An empty retained set is harmless but has no nonempty output
norm to bound. Every nonempty retained complement is invertible, since
its defect has the same strict bound rho<1.

## 3. Arbitrary principal nesting and permutations

The theorem may simply be reapplied after each operation: its conclusion
is exactly its original hypothesis with the same rho. Thus it already
proves closure for any finite sequence of principal restrictions and
Schur eliminations. Simultaneously permuting rows and columns only
reorders the row and column sums, and preserves the identity, so it also
preserves both assertions.

For a description relative to the original matrix, write

    M_R = A[R,R] - A[R,E] A[E,E]^(-1) A[E,R].

Restricting M_R to B subset R gives the identical expression with R
replaced by B: it is the Schur complement after eliminating E in the
principal restriction on E union B. Previously eliminated indices are
retained in this description; they are not silently discarded.

If a further set F subset R is Schur-eliminated, block Gaussian
elimination, or the block inverse formula on E union F, gives the quotient
identity

    (A / E) / F = A / (E union F),                          (8)

on the remaining indices. Here each expression refers to the appropriate
principal restriction; all pivots are invertible by the same theorem.
For example, its new pivot is
`A_FF-A_FE A_EE^(-1)A_EF`, and substituting the block inverse of
`A[E union F,E union F]` gives exactly the twice-eliminated complement.
This justifies the source's descendant description while the direct
closure argument supplies the sharp bound. It does not require leading
sections or a fixed elimination order.

The assertion is about principal restrictions and simultaneous
permutations. A nonprincipal row/column selection need not preserve I.
An arbitrary similarity can enlarge one/infinity norms, so it is not
covered merely by calling it a change of basis.

## 4. Direct, inverse and Euclidean norms

For either envelope,

    ||S|| <= 1+rho,       ||S^(-1)|| <= 1/(1-rho).           (9)

The first follows by triangle inequality, the second by the Neumann
series for S=I+J. For usual complex Euclidean norms, the standard bound

    ||J||_2 <= sqrt(||J||_1 ||J||_infinity) <= rho

gives `||S||_2<=1+rho` and `||S^(-1)||_2<=1/(1-rho)` as well.
Component-envelope admission implies the required usual-modulus bounds,
so it also implies these Euclidean statements. This is a norm result,
not a claim that all prefix/suffix or coefficient/data-error allocations
in a complete circuit have been reoptimized.

Sharpness is elementary. In dimension three take
`H=diag(-rho,rho,0)`, and eliminate the last index. The retained defect
has both norms rho, the direct matrix has both norms 1+rho and its
inverse both norms 1/(1-rho). Thus none of these uniform constants can
be improved under these hypotheses alone.

## 5. Source parity descendants and local consequences

The retained source admits lower triangular Toeplitz T=L(f) when

    sum_j mu(f_j-delta_(j,0)) <= 1/2.

For a full lower triangular Toeplitz matrix this coefficient component
sum equals both its component column and row defect envelopes: the first
column and last row contain all coefficients. The executable
`triangular.py` performs precisely this admission and checks an arbitrary
permutation of all wire indices, including reversal. That relabeling is
a simultaneous input/output permutation; it does not grant an arbitrary
nonisometric similarity or a permutation on only one side.

After the even/odd parity permutation, the source identity is

    T_parity = [[E, ZO], [O,E]],
    K = O E^(-1),
    S = E-ZOK,

and its factorization is lower shear, block diagonal (E,S), upper shear
in matrix product order. The executable order is the reverse application
order: upper, middle, lower. E, O, E^(-1), K and the lower shift Z
belong to the same commuting truncated lower-Toeplitz algebra. Therefore

    E - O E^(-1)(ZO) = E - ZO(O E^(-1)) = E-ZOK.

This is exactly the principal Schur complement after eliminating the E
bank. This reordering is justified by that source algebra, not by a rule
for arbitrary noncommuting blocks. E itself is a principal
restriction. Both recursive children therefore meet the sharp original
rho bound in the component envelope, and remain Toeplitz under this
specific source algebra. The universal closure proof does not need their
Toeplitz property.

For any descendant M, its off-diagonal block O is a submatrix of M-I.
Thus its row and column component envelopes are at most rho. The E child
has inverse envelopes at most 1/(1-rho), giving

    ||K||_(1,infinity;mu) <= rho/(1-rho),
    ||ZK||_(1,infinity;mu) <= rho/(1-rho).                   (10)

The latter uses the fixed lower shift's row/column envelopes at most one.
An ideal completed shear and its inverse consequently have envelopes at
most `1+rho/(1-rho)=1/(1-rho)`. A middle block diag(E,S) has direct norm
at most 1+rho and inverse norm at most 1/(1-rho). At rho=1/2 these are:

| Local quantity | Bound here | Retained conservative bound |
|---|---:|---:|
| descendant M | 3/2 | 2 |
| descendant inverse | 2 | 2 |
| off-diagonal O | 1/2 | 2 |
| K and ZK | 1 | 4 |
| completed shear and inverse | 2 | 5 |

The retained bounds were valid conservative estimates; this result is a
strengthening, not a counterexample to that proof. It does not assert
that the old allocator, stored coefficients, data grids, physical
prefix/suffix bounds or the active compensated-generator program have
been changed or reverified.

## 6. Independent finite evidence and controls

`primary_verify.py` imports no predecessor arithmetic, compiler or receipt.
It implements Gaussian rationals directly with pairs of Fraction values,
uses Gauss-Jordan elimination with exact two-sided inverse checks, and
forms Schur complements directly from the block formula. All tested
envelopes use the exact rational component norm mu; no floating complex
moduli or numerical tolerance enter these tests.

The general census uses dense complex-rational matrices with exact
component row/column admission, sizes one through four and several rho
values. For every retained/eliminated/discarded labeling with nonempty
output, it checks the defect, direct and inverse bounds, the entrywise
positive-resolvent majorant and both stronger budget slacks. Separate
checks compare principal restriction and nested quotient identities with
the original matrix. Reversal preserves the input envelopes.

Handwritten Toeplitz/parity fixtures at dyadic sizes through eight check
the source block identities, descendant Toeplitz structure, E/S
recursion, O/K/ZK bounds and completed-shear inverse bounds. This is
independent exact testing of the stated algebraic interface; it does not
execute or authenticate the author-owned compiled gate program.

Controls keep limitations explicit:

- The diagonal example attains all three sharp constants.
- At rho=1 an admitted principal pivot may be singular.
- At rho=3/2, `A=[[1/4,3/4],[3/4,1/4]]` has defect norm 3/2, but
  eliminating the first index gives S=-2, defect norm 3>3/2.
- Row-only admission need not imply the column conclusion: with rho=3/4,
  `A=[[1,rho,0],[rho,1,0],[rho,0,1]]` has row defect norm rho, while
  eliminating index zero gives a descendant column defect norm 9/8.
- A nonprincipal one-by-one off-diagonal restriction of I is zero, and
  diagonal similarity can amplify an off-diagonal defect. These are
  outside the principal/permutation contract.
- Modulus-only admission is not component admission: for
  `z=(3+3i)/10`, `|z|^2=9/50<1/4` but `mu(z)=3/5>1/2`.
  Eliminating the second index of `diag(1+z,1)` leaves defect z.
  The modulus variant applies at rho=1/2, while the component variant
  does not meet its hypothesis. The retained triangular source explicitly
  admits the stronger component condition; no weaker full-factory
  normalization is silently substituted for it.

The all-size theorem is the written majorant/budget proof in Sections
1-3. Finite exact success is corroboration, not its universal proof and
not formal-kernel verification.

## Attribution and remaining obligations

Credit Jose Manuel (`jmbarrancoml`) for the retained rational rounded
parity-triangular source and its precision proof, and Vlado
Vojdanovski/PR1673 for the parity factorization, recursion, descendant
argument and circuit. Retain Chafik Boukhalfa/PR628 for phases and Cinna
Davis for the later caller, along with the source NOTICE/license lineage.
The original descendant description and inverse bound are predecessor
work. This contribution independently proves the invariant rho defect
bound in both modulus and component envelopes and states its local source
consequences. Substantial OpenAI Codex assistance; Apache-2.0. No human
review or formal-kernel acceptance is claimed.

## Open next questions

- An author may choose to use these local constants in a separately
  reviewed allocation change; no global precision or word-width savings
  are certified here.
- The full bounded-generator/caller composition, setup, coefficient
  delivery and physical tape lowering remain separate obligations.
- Retain exact source admission and simultaneous permutation hypotheses
  when applying the lemma. No new kappa or selected-frontier change
  follows from these norm estimates alone.
