# The span-(m+1) lemma in every address dimension

Produced by Nick Petalas. Apache-2.0. This is a written scoped proof with
an exact finite check of its combinatorial step. It is not independent human
review or proof-kernel verification.

## 1. Model

Fix an address dimension `m >= 1` and a register count `W >= 1`. Work in
the group algebra `R = F_2[M_m(Q)]` of the additive group of rational
`m x m` matrices, with formal symbols `[A][B] = [A+B]`. A paid call is

    D_N([A]) = I + ([A] - 1) N,   rank_Q A = 1,   N = x y^T,   y^T x = 1,

with `x, y` in `F_2^W`. A word of `k` paid calls is required to satisfy

    prod_{j=1}^{k} D_{N_j}([A_j]) = diag([C_1], ..., [C_W]),        (1)

with every `C_w` in `GL_m(Q)`. Equality is of every formal coefficient.
This is the scalar-idempotent abelian register model of eumemic's PR #288,
section 1.2, as stated by Ali Romman's PR #468 for `m = 3`
(`research/bit-three-register-lower-bound`, section 1). The normalization of
final scalar maps is the one recorded there. Only the dimension `m` changes.
Extra registers, clean or dirty helpers and free address maps between paid
calls are outside this note.

Let `S` be the rational span of the paid frames `A_1, ..., A_k`. Every
target lies in `S`: diagonal entry `w` of the expanded product is an
`F_2`-combination of symbols of subset sums of frames, so `C_w` is such a
sum. This is PR #468, section 3.

## 2. Statement

**Theorem.** If `dim S <= m + 1`, then `k >= mW`. Write the normalized
extra frame of section 3 as `u v^T` and set `K = supp(u) ∩ supp(v)`.

1. If `dim S <= m`, or `dim S = m + 1` and `|K| != 2`, the bound holds
   for arbitrary invertible targets.
2. If `dim S = m + 1` and `|K| = 2`, the bound holds for invertible
   lower-triangular targets, by PR #468's block flag argument.

In particular, for invertible lower-triangular targets, a paid-frame span of
dimension at most `m + 1` needs at least `mW` calls in every dimension `m`.
PR #468 proves this for `m = 3` (its span-four lemma).

The direct word attains `mW`: write each `C_w` as a sum of `m` rank-one
frames and use `m` calls with `N = E_ww`. For diagonal targets this word
also has frame span `m`.

## 3. Normalization

Choose a basis `B_i = u_i v_i^T`, `i = 1..s`, of `S` from the paid frames.
By Cauchy–Binet,

    det(sum_i c_i B_i) = sum_{|T| = m} (prod_{i in T} c_i) det U_T det V_T,

where `U_T, V_T` are the `m x m` matrices with columns `u_i, v_i`, `i in T`.
Because `S` contains an invertible target, this polynomial is nonzero, so
some `T` has `det U_T det V_T != 0`. If `s < m`, no such `T` exists, so
`s >= m`. Put `P = U_T^{-1}` and `Q = V_T^{-T}`. Then `P B_i Q = E_ii` for
`i in T`, after relabeling.

The map `A -> P A Q` is an automorphism of the additive group `M_m(Q)` that
preserves rank. It induces a ring automorphism of `R`. Applying it entrywise
to (1) gives an identity of the same form, with frames `P A_j Q` and
invertible targets `P C_w Q`. Lower-triangularity is not preserved. Section 5
does not need it, and section 6 restores it as PR #468 does.

If `s = m`, PR #468's low-span lemma, stated there for general `m`, gives
`k >= mW` for arbitrary invertible targets. From now on `s = m + 1`. Then
`S = {D + tB}`, with `D` diagonal and `B = u v^T` the remaining paid basis
frame.

## 4. Line projection

**Lemma A.** Let `b_0, ..., b_m` be a basis of `S` consisting of rank-one
matrices. Suppose every paid frame is a multiple of one `b_i`. Then
`k >= sum_w nnz(C_w) >= mW`, where `nnz` counts nonzero coordinates in
this basis.

*Proof.* Let `phi_i` be the `i`th coordinate functional on `S`. All
exponents in (1) lie in `S`, so `[A] -> [phi_i(A)]` is a ring homomorphism
from `F_2[S]` to `F_2[Q]`. Apply it to (1). A call whose frame lies on
another line becomes `I + ([0] - 1)N = I`. Let `k_i` be the number of calls
on line `i`. Their product has the form `I + X T Y^T` with `k_i` columns,
over the fraction field of a Laurent polynomial domain (PR #468, section 2).
Its difference from `I` therefore has rank at most `k_i`. The right side
minus `I` is `diag([phi_i(C_w)] - 1)`, of rank `#{w : phi_i(C_w) != 0}`.
A nonzero frame lies on at most one line, so `k >= sum_i k_i`. Each `C_w`
is a combination of `nnz(C_w)` rank-one matrices, so
`m = rank C_w <= nnz(C_w)`. ∎

## 5. The new cases `|K| >= 3` and `|K| <= 1`

**Lemma B (minor identity).** For distinct `i, k, l`, the minor of
`D + tB` on rows `{i, k}` and columns `{i, l}` equals `D_ii t u_k v_l`.

*Proof.* The entries are `D_ii + t u_i v_i`, `t u_i v_l`, `t u_k v_i` and
`t u_k v_l`, because `k != l` and `k, l != i`. Expanding gives the
identity. ∎

**Lemma C.** If `|K| >= 3`, every rank-one matrix in `S` lies on one of
the `m + 1` lines `Q E_00, ..., Q E_{m-1,m-1}, Q B`.

*Proof.* Let `M = D + tB` have rank one. If `t = 0`, `M` is a diagonal
rank-one matrix and lies on one `E_ii` line. Suppose `t != 0` and fix any
`i`. Because `|K \ {i}| >= 2`, there are distinct `k, l` in `K \ {i}`.
Then `u_k v_l != 0`, and Lemma B forces `D_ii = 0`. So `D = 0` and
`M = tB`. ∎

PR #468 uses this step at `m = 3` under the stronger hypothesis that
every coordinate of `u` and `v` is nonzero. In dimension `m >= 4`, the
condition `|K| >= 3` is weaker than full support. This covers frames with
zero coordinates, where PR #468's three-dimensional component bound no
longer applies.

**Case `|K| >= 3`.** Lemmas C and A give `k >= mW` for arbitrary
invertible targets.

**Lemma D.** Let `G` be the directed graph on `{0, ..., m-1}` with an arc
`i -> l`, `i != l`, when `u_i v_l != 0`. A vertex on a directed cycle has
an outgoing arc, so it is in `supp(u)`. It also has an incoming arc, so it
is in `supp(v)`. Every cycle therefore lies in `K`, and any two vertices of
`K` form a 2-cycle. Hence the nontrivial strongly connected components of
`G` are exactly `{K}` when `|K| >= 2`. There are none when `|K| <= 1`.

**Case `|K| <= 1`.** `G` is acyclic. A simultaneous row and column
permutation along a topological order makes every element of `S` upper
triangular. The transformed targets are upper triangular and invertible,
so each has `m` nonzero diagonal entries. A rank-one triangular matrix has
characteristic polynomial `x^{m-1}(x - tr M)`, and its diagonal entries are
its eigenvalues, so at most one is nonzero. Project with the diagonal entry
functional `psi_i`, as in Lemma A. At least `W` calls have
`psi_i(A_j) != 0`, and these call sets are disjoint across `i`, so
`k >= mW` for arbitrary invertible targets. This is the common-flag
principle of huxint's PR #203 and PR #468, applied after normalization.

## 6. The case `|K| = 2`

By Lemma D, `S` is block upper triangular after a permutation. It has one
`2 x 2` diagonal block on `K` and `m - 2` blocks of size one. PR #468,
section 3, proves `k >= 3W` from exactly this structure at `m = 3`. A
rank-one element has at most one nonzero diagonal block. Common flags
restrict to the diagonal blocks. The dimension-two flag bound gives `2W`
per two-block and `W` per one-block. The argument uses only block sizes at
most two and their sum, which is `m` here. This note cites that argument
and does not recheck it. It uses PR #468's lower-triangular target
hypothesis.

Without that hypothesis, the case can behave differently. The exact
control `u = v = (1, 1, 0)`, `D = diag(2, 2, 0)`, `t = -1` gives a rank-one
element `D + tB` off all the lines. So Lemma C fails at `|K| = 2`.

## 7. Finite check

`verify.py` checks the combinatorial step for every pair of nonempty
supports with `1 <= m <= 7`. If `|K| >= 3`, every index `i` has the
distinct witnesses `k, l` used in Lemma C. If `|K| = 2` or `|K| >= 3`,
the only nontrivial component is `K`. If `|K| <= 1`, the arc graph is
acyclic. It verifies Lemma B as a polynomial identity. It also runs an
exact integer grid of rank-one tests:

| m | coordinate set for u, v | D entries | t | pairs with `|K| >= 3` | matrices |
| --- | --- | --- | --- | --- | --- |
| 3 | {-1,0,1,2} | {-1,0,1,2} | {1,-1,2} | 729 | 137,781 |
| 4 | {0,1,2} | {-1,0,1} | {1,-1} | 1,536 | 245,760 |
| 5 | {0,1} | {-1,0,1} | {1,-1} | 106 | 51,304 |

No rank-one `D + tB` with `t != 0` and `D != 0` occurs. The grid is a
control, not the proof. Controls confirm that the rank test separates rank
one from rank two and that a `|K| = 2` pair has off-line rank-one elements.

## 8. Scope

This is a scoped proof in a formal group-algebra model. It gives no
construction, no native conversion, no supplier change and no new κ. It
does not cover frame span `m + 2` or more. It also leaves out non-triangular
targets when `|K| = 2`, extra clean or dirty registers, and free address
maps between paid calls.

## References

- eumemic, PR #288, section 1.2: scalar-idempotent abelian register model.
- Ali Romman, PR #468, `research/bit-three-register-lower-bound`: low-span
  lemma, span-four lemma at `m = 3`, block flag argument, projection tools.
- huxint, PR #203: common triangular-flag obstruction.
