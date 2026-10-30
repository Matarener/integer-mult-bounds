# Exact twelve-call minimum

## Statement

Let `H = UT_3(F_4)`, with `F_4 = F_2[w]/(w^2+w+1)` and

```text
(a,b,c)(a',b',c') = (a+a', b+b', c+c'+a b').
```

The group has order 64. The four paid labels

```text
X_1=(1,0,0), X_w=(w,0,0), Y_1=(0,1,0), Y_w=(0,w,0)
```

are involutions. Write `Z_1=[X_1,Y_1]=(0,0,1)`, `Z_w=[X_w,Y_1]=(0,0,w)`, and `Z_{w^2}=[X_w,Y_w]=(0,0,w^2)`. These central values satisfy `Z_{w^2}=Z_1 Z_w` and `1+w+w^2=0`.

Work in the matrix ring over the group algebra `F_2[H]`. For `r >= 3` and a rank-one idempotent `N` in `M_r(F_2)`, a paid call is

```text
D_N(g) = I + ([g]+[1]) N,    g in {X_1, X_w, Y_1, Y_w}.
```

Each call costs one. There is no free clean role, copy, erase, or uncharged inverse. Scalar `GL_r(F_2)` mixing may be inserted, but it normalizes away: conjugation preserves rank-one idempotents, and augmentation sends every paid factor and the target to the identity, so the residual scalar map is the identity. It is enough to bound pure words in the paid factors.

The target is the diagonal operator

```text
diag([Z_1], [Z_w], [Z_{w^2}], [1], ..., [1])
```

on arbitrary dirty register inputs. The exact minimum number of paid calls is **12**.

## Attaining word and the previous schedule

Apply, in time order, with `E_{tt}` the coordinate projector:

```text
E_00: X_1, Y_1, X_1, Y_1
E_11: X_1, Y_w, X_1, Y_w
E_22: X_w, Y_w, X_w, Y_w
```

Each block is four calls. Disjoint supports do not interact, and every spectator coordinate is fixed. Because each label is an involution, the address multiplier on coordinate `t` is the length-four commutator of that block:

```text
X_1 Y_1 X_1 Y_1 = Z_1,
X_1 Y_w X_1 Y_w = Z_w,
X_w Y_w X_w Y_w = Z_{w^2}.
```

The bill is 12 calls: six `X`-type and six `Y`-type. Letter counts are `n(X_1)=4`, `n(X_w)=2`, `n(Y_1)=2`, `n(Y_w)=4`.

The schedule recorded with the two-register minimum used a six-call composite on the third output,

```text
X_1, X_w, Y_1, X_1, X_w, Y_1 = Z_{w^2},
```

together with four calls for `Z_1` and four calls for `Z_w` through `Y_1` only. That word is correct and costs **14**. It does not use `Y_w`. The twelve-call word replaces that composite by the primitive commutator `[X_w,Y_w]`.

## Nilpotent expansion

Realize `H` by its defining matrices over `F_4` and expand scalars through the regular representation `F_4 -> M_2(F_2)`. Each group element becomes a `6×6` binary matrix. For a paid label `g`, the nilpotent `E(g)=ρ(g)+I` has a single off-diagonal block:

- `X_1` and `X_w` occupy the `A` block (rows `0..1`, columns `2..3`) with `F_4` coefficients `1` and `w`;
- `Y_1` and `Y_w` occupy the `B` block (rows `2..3`, columns `4..5`) with coefficients `1` and `w`.

Direct multiplication of these four nilpotents gives:

- `E(X)E(Y)` is the pure corner `α(X)β(Y)` in rows `0..1`, columns `4..5`;
- `E(Y)E(X)`, `E(X)E(X)`, and `E(Y)E(Y)` are zero;
- every product of three nilpotents is zero.

Therefore, for calls applied in time order `g_1,...,g_n` with matrices `N_1,...,N_n`,

```text
T = D(g_n) ... D(g_1)
  = I + sum_k E(g_k)⊗N_k
      + sum_{i<j} E(g_j)E(g_i)⊗(N_j N_i).
```

The length-two sum is supported only on pairs where call `i` is `Y`-type, call `j` is later and `X`-type, and the corner coefficient is `α(g_j)β(g_i)`.

The image of the target under `ρ` has vanishing `A` and `B` blocks and corner

```text
I_2⊗(E_00+E_22) + M_w⊗(E_11+E_22),
```

where `M_w` is multiplication by `w` and the displayed diagonal matrices are the `r×r` projectors onto the first three coordinates (zeros on spectators). Write `P=E_00+E_22` and `Q=E_11+E_22`. Any word whose full group-algebra endpoint is the target must realize this corner and must have zero linear blocks, because `ρ` is a group homomorphism. The corner identities are necessary; the twelve-call upper bound is checked separately in the full group algebra, not in this `6×6` quotient.

## Rank bound

Zero linear `A` and `B` blocks mean

```text
sum_{X-calls} α_s N_s = 0,    sum_{Y-calls} β_t N_t = 0
```

in `M_r(F_4)`. Factor `N_s=u_s v_s^T` with `v_s^T u_s=1`. For the `X` calls let `α_s in {1,w}` have `F_2` coordinates `(α_{s0},α_{s1})`, and view `α_s u_s` as the column `(α_{s0} u_s, α_{s1} u_s)` in `F_2^{2r}`. If `U` has those columns and `V` has rows `v_s^T`, then `UV=0`, so

```text
n_X >= rank(U) + rank(V).
```

Here `rank(V)=dim span{v_s}`. Because `1` and `w` land in complementary summands,

```text
rank(U) = dim span{u: label X_1} + dim span{u: label X_w}
        >= dim span{u: all X calls}.
```

The same identities hold for the `Y` calls.

Columns of each corner component lie in `span{u: X calls}`, and rows lie in `span{v: Y calls}`, because a contributing term has the shape `u_X (v_X·u_Y) v_Y^T` after the later/earlier assignment above. Thus

```text
span{e_0,e_1,e_2} ⊆ span{u_X} ∩ span{v_Y}.
```

The contragredient representation `(ρ(g)^{-1})^T` reverses the corner order: the same target corner is produced by later `Y` calls after earlier `X` calls, with columns in `span{u_Y}` and rows in `span{v_X}`. Hence all four spans have dimension at least 3, `rank(U)>=3`, and `rank(V)>=3`. Therefore `n_X>=6` and `n_Y>=6`, so every realizing word costs at least `12`.

The twelve-call word meets both inequalities with equality of the summed ranks. The minimum is exactly 12 for every finite `r>=3`, including arbitrary restored dirty spectators.

## What is not claimed

The alphabet is only the four involutions above. Labels `X_{w^2}` and `Y_{w^2}` are outside the argument, because a coefficient `w^2=(1,1)` no longer sits in a single complementary summand. The result is not a bit-supplier embedding, a hosting or precision bill, or a change of `κ`. The selected decimal remains `0.001672660197076918`.
