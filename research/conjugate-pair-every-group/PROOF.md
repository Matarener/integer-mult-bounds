# The conjugate-pair target needs four calls in every group

**Scoped written theorem in a formal group-algebra model; no new κ.**

## Model

Let `G` be any group, `F` any field and `x, y ∈ G` with `xy ≠ yx`. Fix a
width `r ≥ 2`. A paid factor is

```text
D_N(g) = I + ([g] - [e]) N,    g ∈ {x, y},
```

where `N ∈ M_r(F)` is a rank-one idempotent, `N = u vᵀ` with `vᵀu = 1`.
Over `F = F2` this is exactly the factor `I + ([g]+[e])N` of
[#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089). Roles
beyond the first two are arbitrary dirty spectators that must return to `[e]`.
The target is

```text
T = diag([xy], [yx], [e], …, [e])  ∈ M_r(F[G]).
```

**Theorem.** The minimum number of paid factors whose chronological product
equals `T` is exactly four.

The direct word `D_{E00}(x) D_{E00}(y) D_{E11}(y) D_{E11}(x)` attains `T` for
every `G`, `F` and `r ≥ 2`. The rest of this file excludes every shorter word.

## Expansion

Write `N̄ = I - N`. Then `D_N(g) = [g] N + N̄`. Hence, for labels
`g_1, …, g_k` and idempotents `N_1, …, N_k`,

```text
D_{N_1}(g_1) ⋯ D_{N_k}(g_k) = Σ_{U ⊆ {1..k}} [g_U] P_U,
P_U = X_1 ⋯ X_k,   X_i = N_i if i ∈ U, else N̄_i,
```

where `g_U` is the ordered product of the labels in `U`. Since the elements
`[w] E_ij` form an `F`-basis of `M_r(F[G])`, the word realizes `T` if and only
if, for every `w ∈ G`,

```text
Σ_{U : g_U = w} P_U = T_w,
```

with `T_xy = E00`, `T_yx = E11`, `T_e = I - E00 - E11` and `T_w = 0` otherwise.
These are well defined because `xy`, `yx` and `e` are distinct (below).

**Facts about the pair.** Each item follows by cancellation, and each
violation would make `x` and `y` commute:

* (F1) `x, y ∉ {e, xy, yx}` and `x ≠ y`;
* (F2) `xy, yx ∉ {e, x, y, x², y²}`;
* (F3) `x²y ≠ xy`, `xy² ≠ xy`, `y²x ≠ yx`, `yx² ≠ yx`, `xyx ∉ {xy, yx}`,
  `yxy ∉ {xy, yx}`, and `x³, y³` cannot both equal `xy` and `yx`.

For example, `xy = x²` gives `y = x`, and `xyx = xy` gives `x = e`.

## Words of length at most two

For `k ≤ 1` the only values `g_U` are `e` and one label, so by (F1) and (F2)
`T_xy = E00 ≠ 0` cannot be produced. For `k = 2`, the values are `e`, `g_1`,
`g_2` and `g_1 g_2`. By (F2) only `g_1 g_2` can equal `xy` or `yx`, and it
equals at most one of them. One of the nonzero coefficients `E00`, `E11` is
therefore missing.

## Words of length three

From `N² = N` and `N N̄ = N̄ N = 0`:

```text
N_1 P_U = P_U if 1 ∈ U, else 0;      N̄_1 P_U = P_U if 1 ∉ U, else 0;
P_U N_3 = P_U if 3 ∈ U, else 0;      P_U N̄_3 = P_U if 3 ∉ U, else 0.
```

So each sandwich `A T_w B`, with `A ∈ {N_1, N̄_1}` and `B ∈ {N_3, N̄_3}`, keeps
exactly the subsets `U` with `g_U = w` in one corner. The four corners are
`{∅, {2}}`, `{{1}, {1,2}}`, `{{3}, {2,3}}` and `{{1,3}, {1,2,3}}`. Also
`T_w = (N_1 + N̄_1) T_w (N_3 + N̄_3)`.

**Lemma 1.** `P_{1} = P_{2} = P_{3} = 0`.

*Proof.* In corner `(N_1, N̄_3)` the values are `g_1` and `g_1 g_2 ≠ g_1`, so
`N_1 T_{g_1} N̄_3 = P_{1}`; by (F1), `T_{g_1} = 0`. In the same way
`N̄_1 T_{g_3} N_3 = P_{3}` (values `g_3`, `g_2 g_3 ≠ g_3`) and
`N̄_1 T_{g_2} N̄_3 = P_{2}` (values `e`, `g_2 ≠ e`). ∎

**Lemma 2.** For `w ∈ {xy, yx}`, `N̄_1 T_w N̄_3 = 0`.

*Proof.* That corner has values `e` and `g_2`, neither of which is `w` by
(F1) and (F2). ∎

**Lemma 3.** `P_{12}` and `P_{23}` are not both nonzero.

*Proof.* Write `N_i = u_i v_iᵀ`. Then `P_{12} = u_1 (v_1ᵀu_2)(v_2ᵀ N̄_3)`,
`P_{23} = (N̄_1 u_2)(v_2ᵀu_3) v_3ᵀ` and `P_{2} = (N̄_1 u_2)(v_2ᵀ N̄_3)`. If both
are nonzero, then `v_2ᵀ N̄_3 ≠ 0` and `N̄_1 u_2 ≠ 0`. Their outer product
`P_{2}` is then nonzero, contrary to Lemma 1. ∎

Now go through the eight label patterns. Write `E_a = e_a e_aᵀ`.

**`xxx`, `yyy`.** The subsets of size at least two have values `x², x³`
(or `y², y³`). By (F2) and (F3) they cannot supply both `xy` and `yx`.

**`xyx`, `yxy`.** For `xyx`, `g_{12} = xy`, `g_{23} = yx`, `g_{13} = x²` and
`g_{123} = xyx`. By (F2) and (F3), only `{1,2}` has value `xy` and only `{2,3}`
has value `yx`. Using the corner split and Lemma 2, `E00 = T_xy = P_{12}` and
`E11 = T_yx = P_{23}`. Both are nonzero, contradicting Lemma 3. The pattern
`yxy` is identical with `E00` and `E11` exchanged.

**`xxy`, `yyx`.** For `xxy`, `g_{12} = x²`, `g_{13} = g_{23} = xy` and
`g_{123} = x²y ≠ xy`. The value `yx` can only come from `{1,2,3}`, so the word
fails unless `x²y = yx`; assume this. Put `a = 0`, `b = 1`; then
`T_xy = E_a` is carried by `{1,3}, {2,3}` and `T_yx = E_b` by `{1,2,3}` alone.
For `yyx` the same holds with `a = 1`, `b = 0` (and `y²x = xy` assumed).

* `E_b` lies only in corner `(N_1, N_3)`, so `E_b = N_1 E_b N_3
  = u_1 (v_1ᵀ E_b u_3) v_3ᵀ`. Hence `u_1` and `v_3` are nonzero multiples of
  `e_b`.
* `N_1 E_a N̄_3 = 0` because `{1,2}` has value `x²` (resp. `y²`). Therefore
  `N_1 E_a = N_1 E_a N_3 = P_{13} = u_1 (v_1ᵀ N̄_2 u_3) v_3ᵀ`, a multiple of
  `e_b e_bᵀ`. But `N_1 E_a = u_1 (v_1ᵀ e_a) e_aᵀ` is a multiple of `e_b e_aᵀ`.
  So `N_1 E_a = 0` and `N̄_1 E_a = E_a`.
* Lemma 2 gives `0 = N̄_1 E_a N̄_3 = E_a N̄_3`, so
  `E_a = E_a N_3 = e_a (e_aᵀ u_3) v_3ᵀ`, a multiple of `e_a e_bᵀ`. This is false.

**`xyy`, `yxx`.** For `xyy`, `g_{12} = g_{13} = xy`, `g_{23} = y²` and
`g_{123} = xy² ≠ xy`. Then `yx` can only come from `{1,2,3}`; assume
`xy² = yx`. With `a = 0`, `b = 1` (for `yxx`: `a = 1`, `b = 0`):

* As before, `E_b = N_1 E_b N_3`, so `u_1` and `v_3` are multiples of `e_b`.
* `N̄_1 E_a N_3 = 0` because `{2,3}` has value `y²` (resp. `x²`). Therefore
  `E_a N_3 = N_1 E_a N_3 = P_{13}`, a multiple of `e_b e_bᵀ`, while
  `E_a N_3 = e_a (e_aᵀ u_3) v_3ᵀ` is a multiple of `e_a e_bᵀ`. So
  `E_a N_3 = 0` and `E_a N̄_3 = E_a`.
* Lemma 2 gives `0 = N̄_1 E_a N̄_3 = N̄_1 E_a`, so
  `E_a = N_1 E_a = u_1 (v_1ᵀ e_a) e_aᵀ`, a multiple of `e_b e_aᵀ`. False.

Every pattern fails, so no word of length three realizes `T`. ∎

## What is used and what is not

The proof uses only the coefficient equations, `xy ≠ yx` and rank one of each
`N_i`. It uses no generation hypothesis, perfectness, element orders, support
filter or finite census. The noncommuting hypothesis is necessary: for
`y = x⁻¹` the target is `I` and is met by the empty word.

This is a formal group-algebra theorem. It prices no native address
operation and does not change the selected κ.
