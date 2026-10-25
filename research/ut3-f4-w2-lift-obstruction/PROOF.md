# Six-label diagonal lift

## Statement

Let `H = UT_3(F_4)`, with `F_4 = F_2[w]/(w^2+w+1)` and

```text
(a,b,c)(a',b',c') = (a+a', b+b', c+c'+a b').
```

The group has order 64. The six paid labels

```text
X_1=(1,0,0), X_w=(w,0,0), X_{w^2}=(w^2,0,0),
Y_1=(0,1,0), Y_w=(0,w,0), Y_{w^2}=(0,w^2,0)
```

are involutions. Their commutators are `[X_a,Y_b]=(0,0,a b)`. In particular

```text
Z_1=[X_1,Y_1]=(0,0,1),
Z_w=[X_w,Y_1]=(0,0,w),
Z_{w^2}=[X_w,Y_w]=(0,0,w^2).
```

Also `[X_{w^2},Y_{w^2}]=(0,0,w)=Z_w`, because `w^2 w^2=w`.

Work in the matrix ring over `F_2[H]`. For `r>=3` and a rank-one idempotent `N` in `M_r(F_2)`, a paid call is

```text
D_N(g) = I + ([g]+[1]) N,
```

with `g` one of the six labels. Each call costs one. There is no free clean role, copy, erase, or uncharged inverse. A scalar factor from `GL_r(F_2)` may be inserted without charge. Conjugation preserves the set of rank-one idempotents. Augmentation `F_2[H] -> F_2` kills every paid factor, since `[g]+[1]` has even weight, and it kills the target below, so the residual scalar on a realizing word is the identity. It is enough to bound pure words in the paid factors.

The target is

```text
diag([Z_1], [Z_w], [Z_{w^2}], [1], ..., [1])
```

on `r` registers. Every realizing word has length at least **12**. Two explicit words attain 12. One of them uses both `X_{w^2}` and `Y_{w^2}`.

The four-label count on `{X_1,X_w,Y_1,Y_w}` is a different hypothesis. Its complementary-summand split uses coefficients in `{1,w}` only. The coefficient `w^2=(1,1)` meets both `F_2` coordinates, so that split does not prove the six-label statement. The argument below replaces it.

## Two attaining words

Coordinate projectors `E_{tt}` commute across `t`. On a single coordinate the address multiplier is the left product of the labels in time order. Both schedules below are four calls per register.

Mixed word, using `X_{w^2}` and only `Y_1`:

```text
E_00: X_1, Y_1, X_1, Y_1          = Z_1
E_11: X_w, Y_1, X_w, Y_1          = Z_w
E_22: X_{w^2}, Y_1, X_{w^2}, Y_1  = Z_{w^2}
```

The third block is `[X_{w^2},Y_1]=(0,0,w^2)`.

Both-new word, using `X_{w^2}` and `Y_{w^2}`:

```text
E_00: X_1, Y_1, X_1, Y_1                = Z_1
E_11: X_{w^2}, Y_{w^2}, X_{w^2}, Y_{w^2} = Z_w
E_22: X_w, Y_w, X_w, Y_w                = Z_{w^2}
```

Each word has `n_X=6` and `n_Y=6`. Spectators stay at the identity because their projector rows are zero.

## Nilpotent shape

Realize `H` by its defining matrices and expand `F_4` through the regular representation `F_4 -> M_2(F_2)`. Multiplication by `1`, `w`, and `w^2` becomes

```text
I_2,  [[0,1],[1,1]],  [[1,1],[1,0]].
```

All three matrices are symmetric, and the last one equals `I_2+M_w`. Each group element becomes a `6×6` binary matrix. For an axis label the nilpotent `E(g)=ρ(g)+I` has a single off-diagonal block: an `X`-label occupies rows `0..1`, columns `2..3`; a `Y`-label occupies rows `2..3`, columns `4..5`. Consequently, for every pair among the six labels,

- `E(X)E(Y)` is the pure corner `m_α m_β` in rows `0..1`, columns `4..5`;
- every other length-two product is zero;
- every product of three nilpotents is zero.

The same block arithmetic, transposed, holds for `σ(g)=ρ(g^{-1})^T=ρ(g)^T`. The only nonzero length-two products are `E^σ(Y)E^σ(X)`, and they sit in rows `4..5`, columns `0..1`.

For calls in time order `g_1,...,g_n` with idempotents `N_k`,

```text
ρ_*(D(g_n)...D(g_1))
  = I + sum_k E(g_k)⊗N_k
      + sum_{i<j} E(g_j)E(g_i)⊗(N_j N_i).
```

The quadratic sum is supported on pairs where call `i` is `Y`-type and later call `j` is `X`-type. A term `N_j N_i=u_j(v_j·u_i)v_i^T` has image in `span{u_X}` and row space in `span{v_Y}`. The contragredient expansion swaps the roles: image in `span{u_Y}` and row space in `span{v_X}`.

The target corner is `m_1` on register 0, `m_w` on register 1, and `m_{w^2}` on register 2. In the basis `{m_1,m_w}` that is `P=E_{00}+E_{22}` and `Q=E_{11}+E_{22}`. Both images, and both row spaces, equal `span{e_0,e_1,e_2}`. Therefore every realizing word satisfies

```text
dim span{u_X} >= 3,  dim span{v_Y} >= 3,
dim span{u_Y} >= 3,  dim span{v_X} >= 3.
```

The linear blocks must vanish. With `S_α` the sum of the `X`-call idempotents of coefficient `α`, the regular representation gives the two independent equations `S_1+S_{w^2}=0` and `S_w+S_{w^2}=0`. The same holds for `Y`.

## Diagonal-lift lemma

Write `α=α_0·1+α_1·w` in `F_2`. Form the `2r×n` matrix `U` whose columns are `(α_0 u, α_1 u)`, and the `n×r` matrix `V` whose rows are `v^T`. The linear equations are exactly `UV=0`, so

```text
n >= rank(U) + rank(V).
```

`rank(V)` is `dim span{v}`. The new point is that `w^2` does not let `dim span{u}` exceed `rank(U)`.

Let `L` be the column space of `U` inside `F_2^r ⊕ F_2^r`. Define `φ(x,y)=x+y` and let `Δ={(u,u)}`. Then `Δ` sits inside `ker φ`. Every type-`1` or type-`w` column `c` satisfies `φ(c)=u`, and every type-`w^2` column is `(u,u)`. Hence

```text
span{u} ⊆ φ(L) + π_0(L ∩ Δ),
```

where `π_0` reads the first summand. Dimension counting gives

```text
dim φ(L) + dim(L ∩ Δ)
  = dim L - dim(L ∩ ker φ) + dim(L ∩ Δ)
  <= dim L,
```

because `L ∩ Δ ⊆ L ∩ ker φ`. Therefore

```text
dim span{u} <= rank(U).
```

Adding the two rank inequalities,

```text
n_X >= dim span{u_X} + dim span{v_X} >= 6,
n_Y >= dim span{u_Y} + dim span{v_Y} >= 6.
```

Every realizing word costs at least 12, for every finite `r>=3`, with arbitrary restored spectators. Both words meet the bound.

The separated `{1,w}` span is not this count. On the mixed word the `X_1` and `X_w` shadows span only `span{e_0,e_1}`, dimension 2. The third direction is the `w^2` column `(e_2,e_2)`. It is invisible to a split that discards `w^2`, and it still costs one dimension of `L`. A direct sum of the three pure-type subspaces of `L` can overcount: `span{(e_0,0),(0,e_0)}` has dimension 2 while the three axis spaces each contribute dimension 1. That overcount is not used.

The same packing cannot hide three independent shadows in a rank-2 lift. In `r=3` every shadow has dimension at most 3, so a violating family would contain three pure columns with independent shadows and lift rank at most 2. All `C(21,3)=1330` triples, and all `82160` subsets of size at most 6, satisfy `dim span{u} <= rank(U)`.

## What is not claimed

This does not reprove the four-label minimum, and it does not use the fourteen-call composite. It does not allow non-idempotent factors, non-axis letters, or a bit-supplier embedding. `12α` is a formal per-call price in this alphabet. The selected decimal remains `0.001672660197076918`.
