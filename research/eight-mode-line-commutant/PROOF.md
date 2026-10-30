# Exact line commutant of the eight-mode code

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Source and question

Use the actual physical normalizers in the PR5402 provider, as used by
PR5578, `current-provider.md`. The source has 112 main ports and eight modes.
Write M for its 112 by 8 real scalar matrix. The stored `mode_columns`
array is M transpose. It satisfies M transpose M = 56 I.
For each positive integer width f, put

    W_f = diag(K_p,i^(-1) tensor f) M diag(K_m,a tensor f) / 2,
    Z_f = diag(K_m,a^(-1) tensor f) M transpose diag(K_p,j tensor f) / 2.

A scalar coefficient is applied once. It is not raised to the power f.
For any complex 8 by 8 matrix E, define A_f(E) = W_f E Z_f. E can depend
on f. No symmetry, idempotence, invertibility or dyadic restriction is needed.

For a nonzero binary vector v in nine dimensions, let X_v translate an
address by v, and let

    C_v = alpha I + beta X_v,
    alpha = (1+i)/2, beta = (1-i)/2,
    Q_v,f = C_v tensor f.

The question is whether A_f(E) commutes with Q_v,f on the main bank.
The code I-A_f(E) commutes if and only if A_f(E) does.

## 2. Complete answer

Let chi = 511, the XOR of all nine coordinate axes. For every f >= 1:

- If v = chi, every E commutes. The scalar solution space has dimension 64.
- If v is any of the other 510 nonzero vectors, commutation implies E = 0.
  The scalar solution space has dimension zero.

Thus a nonzero projection onto any mixed mode subspace cannot make the
current central direction v=1 commute with its code. A different scalar
basis, an oblique projection, complex coefficients, or width-dependent scalar
coefficients cannot remove that condition. This also covers every coordinate
subset in PR5578, including the full eight-mode code.

The result identifies the only line Gaussian that remains available in this
fixed code family. It does not prove that all other decoders fail. In particular,
commutation is a condition of the decoder route, not a general lower bound on
paid queries.

## 3. A finite integer certificate with an all-width implication

Each source K is a real signed permutation and fixes the basis vector |0>
with coefficient +1. The verifier checks this on every address. For each
main pair (i,j) and mode pair (a,b), put

    T_ijab = K_p,i^(-1) K_m,a K_m,b^(-1) K_p,j.

Then

    A_f(E)_ij = (1/4) sum_ab M_ia M_jb E_ab (T_ijab tensor f).

Each T fixes |0>. Write T|v> = s|y>, where s is +1 or -1.
At width one the (u,0) entry of T C_v - C_v T is

    beta (s [u=y] - [u=v]).

At width f, use input |0> in every column, output |u> in the first column
and output |0> in each remaining column. The same entry is exactly

    beta alpha^(f-1) (s [u=y] - [u=v]).

To see the common factor, note that a permutation that fixes zero cannot send
v to zero. The (0,0) entries of both T C_v and C_v T are therefore alpha.
There are no unspecified phases or limits in this calculation.

For fixed v, a zero commutator therefore implies the following integer
linear equations in the 64 scalar entries of E, at every f >= 1:

    sum_ab M_ia M_jb (s_ijab [u=y_ijab] - [u=v]) E_ab = 0.

The omitted factor beta alpha^(f-1)/4 is nonzero. `WITNESSES.json` selects
64 such rows for each of the 510 noncharacteristic directions. The verifier
reconstructs every row from the two exact source recipes. Every resulting
64 by 64 integer matrix has rank 64 modulo the prime 1009. Its integer
determinant is thus nonzero, and its rank over the complex numbers is 64.
This proves E=0 separately for every f. A full scan of every possible row
is not needed for this exclusion.

For the actual central direction, rational elimination also computes the
nonzero determinant in `RESULT.json`. This uses a separate arithmetic path.
The proof does not require that determinant to have any specified value.

## 4. The characteristic case

The verifier checks K X_chi = X_chi K for all 120 source normalizers and
all 512 addresses, with signs. This implies that K, its inverse, every T,
and every A_f(E) commute with C_chi in each address column. It follows that
A_f(E) commutes with Q_chi,f for every E and f.

Together with Section 3, this proves both inclusion and exclusion for every
nonzero binary direction. The identity direction v=0 has C_0=I and imposes
no condition; it is not a nontrivial Gaussian query.

## 5. Reciprocal forms and scope

A matrix commutes with an invertible Q if and only if it commutes with Q
inverse. An invertible code commutes with Q if and only if its inverse does.
C_v is symmetric, so transposition gives the same zero-commutator condition.
The classification therefore also applies to these reciprocal tests. It does
not allow an operator to pass through another operator without that condition.

The proof binds the actual finite ordinary maps. It takes the source provider
endpoint as a premise. It does not reprove the native word, its physical
Gaussian child normalization, the full caller, precision, storage, compiler
or outer multiplier. No moment improvement or new kappa is claimed.
Address-dependent mode coefficients, changed W or Z, new provider words and
paid decoders outside this commutation route remain open.

## 6. Credit

Dugongue supplies PR5578 and the characteristic decoder proposal. Dillon
Amburgey supplies PR5402. Chris R / Clear1nsight supplies PR5407 and PR5413.
Ali Romman supplies PR5377/5383 cached relations. The exact normalizers retain
Cao Yifan's native word, Cinna Davis's code/helper/controller work, Dugongue's
code factorization, zxv's Clifford/compiler work, Jacob Alan Sussman's recursion,
Ryanson Jonathan and the full source lineage in `inputs/ATTRIBUTION.md`.
The new result is the complete 511-direction, arbitrary-mode-matrix
classification and its source-bound certificate. Modular rank and tensor-entry
arguments are standard methods.
