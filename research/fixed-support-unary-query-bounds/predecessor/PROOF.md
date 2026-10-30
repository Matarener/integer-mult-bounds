# Fixed-support unary queries with arbitrary swap-algebra bridges

Independent local mathematical audit, 2026-10-19. This is an all-parameter
written proof, with a separate finite exact arithmetic witness. It is not a
formal-kernel proof or a claim about a larger native alphabet.

## Precise model and conclusion

Let K be a characteristic-zero field containing i (in particular Q(i)). Let
f >= 1, d = 4^f, X = K^d, and let N on X have N^2 = -I and eigenspaces
X_+, X_- of equal dimension r = d/2. On Y = X tensor X put

    S(x tensor y) = y tensor x,
    A = (N tensor I) S,       B = i A.

Then B^4 = I, S^2 = I, and SBS = B^-1. Let
R = K[S]/(S^2 - 1), acting on Y by this S. There are m >= n banks, each with
state in Y. Inputs to all banks are arbitrary and independent. Every bridge
in GL_m(R) is allowed at zero query cost, including bank-specific S operations.
A paid query applies A or A^-1 to exactly one bank. No other paid native
operator or free address/Pauli controller is admitted. The exact endpoint is

    diag(A^2 I_n, I_(m-n)),

so all extra banks are restored on every input, not assumed zero.

**The sharp query count is 2n, for every finite m >= n and every f >= 1.**
The direct word applies A twice to each of the n output banks, attaining 2n.
If each query has native arity 2f, its native rank mass is at least 4nf.
Native arity and physical admission of A are premises inherited from the
assigned carrier; this proof establishes the query count.
The balanced N spectrum is also an assigned premise. The finite witness below
uses its diagonal normal form; it does not re-audit the literal native recipe.

## Native constituent check

Write N x = +i x on X_+ and N x = -i x on X_-. On X_+ tensor X_+ one has
B = -S; on X_- tensor X_- one has B = S. Consequently all four one-dimensional
characters (B,S) = (b,s), b,s in {+1,-1}, occur:

| (b,s) | Native subspace | Multiplicity |
|---|---|---|
| (-1,+1) | Sym^2(X_+) | r(r+1)/2 |
| (+1,-1) | exterior^2(X_+) | r(r-1)/2 |
| (+1,+1) | Sym^2(X_-) | r(r+1)/2 |
| (-1,-1) | exterior^2(X_-) | r(r-1)/2 |

All are nonzero since r >= 2. For x in X_+, y in X_-, set
p = x tensor y and q = y tensor x. Then Bp = q, Bq = -p, Sp = q, Sq = p.
The basis w_+ = p-iq, w_- = q-ip gives the two-dimensional constituent

    rho(B) = diag(i,-i),      rho(S) = [[0,1],[1,0]].

This occurs r^2 times. Thus the specific evaluations below are restrictions
to actual invariant native subspaces, not unverified formal substitutions.
The lower bound uses only these restrictions and requires no inference from
equality in a quotient to equality of the original operators.

## Pulling bridges and fixing their total

Replacing A^epsilon by B^epsilon only adds the bank scalar i^(-epsilon),
which belongs to GL_m(R). Pull all bridges to the left. Every circuit becomes

    C = H(S) W,       W = F_k ... F_1,
    F_j = I + u_j (B^epsilon_j - I) v_j,

where u_j is an m-column over R, v_j an m-row over R, v_j u_j = 1, and
epsilon_j is +1 or -1. This follows by conjugating a one-bank query by the
cumulative bridge to its right; it does not move B through an R coefficient.

On each native character (B,S) = (1,+1),(1,-1), every F_j is I. The target
therefore forces H(+1) = H(-1) = J, where J = diag(-I_n,I_(m-n)). An R matrix
is determined by these two evaluations, since 2 is invertible. Hence H(S)=J
and the normalized endpoint is exactly

    W = diag(B^2 I_n, I_(m-n)).                         (1)

## Noncommutative chronological identity

Set d_j = B^epsilon_j - I, U = [u_1 ... u_k], V = [v_1; ...; v_k],
D = diag(d_1,...,d_k), and define the strictly lower triangular k by k block
matrix L by L_ab = v_a u_b for a>b and zero otherwise. Expanding the ordered
product, with all factors retained in their displayed order, gives

    W-I = U G V,
    G = D (I-LD)^-1 = D sum_(t=0)^(k-1) (LD)^t.        (2)

The finite sum is valid over the noncommutative operator algebra because LD
is strictly lower triangular. No global inverse of B-I is asserted. In a
representation where all d_j are invertible, (2) also gives

    G = (D^-1 - L)^-1.                                (3)

For example the two-query cross term is u_2 d_2 (v_2 u_1) d_1 v_1,
which fixes the orientation of L and G.

## Rank proof, including restored dirty banks

For s = +1,-1 let U_s,V_s be evaluation of the R entries at S=s, and write
a_s = rank(U_s), b_s = rank(V_s), with ranks over K. In rho, diagonalizing S
and regrouping rows and columns identifies rho(U) with U_+ direct-sum U_-
and likewise for V. Thus

    rank rho(U) = a_+ + a_-,
    rank rho(V) = b_+ + b_-.

By (1), rho(W-I) has rank 2n. Equation (2) implies

    a_+ + a_- >= 2n,       b_+ + b_- >= 2n.            (4)

Now restrict to the two actual characters chi_s with B=-1,S=s. Both choices
of epsilon give d_j=-2, so G_s is invertible: D_s^-1-L_s is lower triangular
with diagonal -1/2. Equation (1) has chi_s(W-I)=0, hence

    U_s G_s V_s = 0.

Because G_s is invertible, its image of im(V_s) has dimension b_s and lies
in ker(U_s), whose dimension is k-a_s. Therefore

    k >= a_s + b_s       for each s = +1,-1.           (5)

Summing (5) and using (4) yields 2k >= 4n, or k >= 2n.
When m=n, each U_s,V_s has rank n, so the originally proposed single-character
argument already suffices. With extra banks, individual ranks need not be n;
the two-character sum above supplies the needed uniform argument.

## Evidence and limits

`witness.py` uses only exact Gaussian rational arithmetic. At d=4 it checks
the balanced diagonal-N tensor/swap representation, explicit embeddings
of all required characters and the two-dimensional constituent, all D8 relations,
and the noncommutative formula against a direct five-query product for m=3.
The bridges have distinct S=+1 and S=-1 components. A deliberately reversed
resolvent ordering must fail. An attaining four-query word for n=2,m=3 is
checked in all five simple constituents. This is a finite identity witness,
not an exhaustive search over bridge matrices or query words.

The written proof, rather than this finite check, covers every f>=1, every
finite m>=n, all bridge coefficients in K, all query signs and all lengths.
It does not cover arbitrary Pauli/address monomials outside R, changing support,
other native queries, weakened observation endpoints, approximate equalities,
or a nonlinear/noninvertible bridge model. In particular a changed carrier
with A^4=-I is outside the theorem. No recursive moment improvement,
physical tape or precision theorem, global impossibility, or new kappa follows.
No historical source claim is used as a changed-construction certificate.

Reproduce the finite witness from `/Users/ross/git/math` with
`python3 .research-automation/runs/kappa-changed-endpoints-20261019T0153Z/fixed-support-audit/witness.py`.
Every witness condition uses an explicit `need`/`raise` check. Run `validate.py`
in the same directory to check normal and `-O` execution, identical outputs,
absence of assertion statements, and forced failures in both modes. Exact
commands, hashes and outcomes are saved in `VALIDATION.json`.
