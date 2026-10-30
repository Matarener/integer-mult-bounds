# Two coordinate 3-cycles in every address dimension

This is a written proof with finite corroboration in [verify.py](verify.py).
It extends one step of the n = 3 and n = 4 results to every n. Those two
results are cited premises; they are not re-run here.

## 1. Model

Work in `M_R(F2[G])`, `G = GL_n(F2)`, as in Mihir Srivastava's #4939 and the
packages that follow it. Write `E_ij = I + e_i e_j^T` (i ≠ j) for the coordinate
CNOT with `x_i <- x_i + x_j`. Say that `E_ij` **writes** `i` and **reads** `j`.
A paid call is

    D(g, N) = I + ([g] + [e]) N,   g a coordinate CNOT,  N = u v^T,  v^T u = 1,

with `N` a rank-one idempotent in `M_R(F2)`. Free scalar `GL_R(F2)` maps are
allowed; their entries are multiples of `[e]`. Equality is formal: every group
coefficient must agree.

Let `c` be a coordinate 3-cycle on coordinates 0, 1, 2. Coordinates
`3, ..., n-1` are **spectators**. The question is the least number of paid calls
in a word whose product is `T = diag([c],[c])` at `R = 2`. The target fixes
every spectator row and column.

Two facts are used throughout.

* Each paid call is an involution. `([g]+[e])^2 = [g^2] + [e] = 0` because
  `g^2 = e` and the characteristic is two. So `D^2 = I`, and every word product
  is invertible.
* The augmentation `eps: F2[G] -> F2`, `[g] -> 1`, is a ring homomorphism. Applied
  entrywise it maps `M_R(F2[G])` to `M_R(F2)`. For every rank-one idempotent
  `N`, `I + N` has rank `R - 1`, because `(I+N)u = u + u(v^T u) = 0`.

## 2. A coordinate written exactly once

For a coordinate `k`, let `S_k = {h in G : e_k^T h = e_k^T}`: the elements that
leave row `k` unchanged. It is a subgroup. Let `pi_k` be the F2-linear
projection that keeps the group elements of `S_k` and deletes the others,
applied entrywise.

**Lemma 1.** Suppose exactly one call `t` of a word writes `k`. Write the
product as `P = A D_t B`. Then

    pi_k(P) = A (I + N_t) B.

*Proof.* Every call other than `t` has a label in `S_k`, so `A` and `B` have
support in `S_k`. Expand `D_t = (I + N_t) + [g_t] N_t`. The first part is a
scalar matrix. For `a, b in S_k` and `g_t = E_kj`,

    e_k^T a g_t b = e_k^T g_t b = (e_k^T + e_j^T) b = e_k^T + e_j^T b,

and `e_j^T b ≠ 0` because `b` is invertible. Hence every element in the support
of `A [g_t] N_t B` lies outside `S_k`. Because `S_k` is a subgroup, multiplying
by `A` and `B` keeps `A (I+N_t) B` inside `S_k`. Projection therefore
deletes exactly the second part. QED

**Corollary 2 (spectator writes).** In a word with product `T`, no spectator is
written exactly once.

*Proof.* `T` has support `{c}` and `c` fixes the spectator row, so
`pi_k(T) = T`. Lemma 1 gives `A (I+N_t) B = T`. Apply `eps`. The left side has
rank at most `R - 1 = 1`. The right side is `eps(T) = I`, which has rank two.
QED

**Corollary 3 (target writes).** In a word with product `T`, each of the
coordinates 0, 1, 2 is written at least twice.

*Proof.* `c` changes row `k` for `k = 0, 1, 2`, so `pi_k(T) = 0`. If no call
wrote `k`, every label would lie in `S_k`, so `pi_k(P) = P = T ≠ 0`. If exactly
one call wrote `k`, Lemma 1 gives `A (I+N_t) B = 0`. Then `eps(A)` and `eps(B)`
are invertible, so `I + N_t = 0`. That is impossible because `I + N_t` has
rank one. QED

**Reads.** The map `[h] -> [h^T]` is an anti-automorphism of `F2[G]`. Together
with matrix transposition it is an anti-automorphism of `M_R(F2[G])`. It sends
`D(g,N)` to `D(g^T, N^T)`, a legal paid call, and it reverses the word.
`E_ij^T = E_ji`, so a read becomes a write. The target becomes
`diag([c^{-1}],[c^{-1}])`, another coordinate 3-cycle that fixes every
spectator. Corollaries 2 and 3 therefore hold for reads too. No spectator is
read exactly once, and each target coordinate is read at least twice.

## 3. Removing idle spectators

**Lemma 4.** Let `k` be a spectator.

1. If no call writes `k`, the subspace `U = {x : x_k = 0}` is invariant under
   every label and under `c`. Restriction to `U` is a homomorphism. It sends
   every call that reads `k` to `D(e, N) = I` and keeps every other call. The
   result is a word of no greater length for the same target at dimension
   `n - 1`.
2. If no call reads `k`, the line spanned by `e_k` is invariant under every
   label and under `c`. The induced action on `F2^n / <e_k>` is a homomorphism.
   It sends every call that writes `k` to `I` and keeps every other call. The
   result is again a shorter-or-equal word at dimension `n - 1`.

*Proof.* A label `E_ij` maps `e_j` to `e_j + e_i` and fixes every other basis
vector. In case 1, no label has `i = k`, so `U` is invariant and the labels
`E_ik` act as the identity on `U`. In case 2, no label has `j = k`, so `<e_k>`
is invariant and the labels `E_kj` induce the identity on the quotient. The
3-cycle `c` fixes `e_k` and the coordinate `x_k`. Group homomorphisms extend to
the group algebras and to `M_R`, and `[e] + [e] = 0` turns a mapped call with
identity label into `I`. QED

Apply Lemma 4 repeatedly until neither case applies. Each step lowers the
dimension, so this stops. The final word realizes `T` at dimension `3 + s` and
has length `L' <= L`. Each of its `s` remaining spectators is written and read.
By Corollary 2 and its read form, each is written at least twice and read at
least twice.

## 4. The bound

**Theorem.** For every `n >= 3`, no word of length at most 9 realizes
`diag([c],[c])` in `M_2(F2[GL_n(F2)])`. A word of length 10 or 11 exists for some
`n` only if one exists at `n = 5` in which both spectators are written at
least twice and read at least twice, the three target coordinates are each
written and read at least twice, and the write counts (target, spectator) are
`(6,4)`, `(6,5)` or `(7,4)`.

*Proof.* Each call writes exactly one coordinate. In the final word of
Section 3, the writes to target coordinates number at least 6 by Corollary 3.
The writes to spectators number at least `2s`. So `L >= L' >= 6 + 2s`.

If `L <= 9`, then `s <= 1`, so the final word lives at dimension 3 or 4 and has
length at most 9. James Reed's #5005 (n = 3) and #5379 (n = 4) exclude every
length up to 11 there. If `L <= 11`, then `s <= 2`. The cases `s <= 1` are
excluded in the same way, so `s = 2`, dimension 5 and `L' in {10, 11}`. The
three listed write profiles are the solutions of `w_T + w_S = L'`,
`w_T >= 6` and `w_S >= 4`. QED

**Remark (one cross call each way).** In the residual case some call writes a
target coordinate while reading a spectator, and some call writes a spectator
while reading a target coordinate. If no call of the first kind existed, the
span of the spectator basis vectors would be invariant. The quotient by it
would delete all `w_S >= 4` spectator writes and leave a word of length at most
7 at `n = 3`, contradicting #5005. The second kind follows by transposition.

Upper bound: the 12-call word of #5005, which never touches a spectator,
realizes `T` for every `n >= 3`. Hence `10 <= cost <= 12` for every `n >= 5`.
Exact cost 12 for every `n` is equivalent to excluding the residual
five-coordinate case.

## 5. What the checks cover

`verify.py` checks the ingredients on concrete words: the involution property
of all 120 paid calls at `n = 5`, `R = 2`; `rank(I+N) = R-1` for every rank-one
idempotent at `R = 2, 3`; the identity of Lemma 1 on 150 random words at
`n = 5`; the restriction and quotient homomorphisms of Lemma 4 on 60 random
words each; the transpose anti-automorphism on 60 random words; an exhaustive
instance of Lemma 1's rank consequence on all 368,136 reduced words of length
at most 3 at `n = 4`, `R = 2` (629,928 single-write cases); the 12-call word at
`n = 5`; and the counting step. Two controls reject a corrupted projection
formula. Random words are checks of the written lemmas, not a proof of them.

## 6. Limits

* The residual `n = 5`, length 10 and 11 case is not searched. Exact cost 12
  for `n >= 5` therefore remains open.
* Only `R = 2` is concluded. Lemma 1 and the rank argument work for any `R`,
  including dirty registers, but no `R = 3` base case beyond #5292 is known.
* This is a formal-model statement. It supplies no native operation, tariff,
  supplier or κ change.
