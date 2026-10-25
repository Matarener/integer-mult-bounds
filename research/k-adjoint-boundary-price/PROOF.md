# One K/adjoint round trip on register 333

## Pinned boundary

PR #4002 freezes forty recipe descriptors and sixteen warps on four binary
maps. One of those maps is the credited source witness

```text
G = (1, 2, 8, 32, 44, 128, 59, 66, 489).
```

The new-version sign-+1 warp with those columns has entrance
`(266, 138, 74, 30, 1)`, terminal `(426, 96, 24, 6, 1)`, and coverage rows
for providers `base` and `extra` at register `333`, index `4`. The matching
sign-−1 descriptor swaps that entrance and terminal. This package prices that
pair and no other warp.

## Operators

Columns are images of the standard basis. Write `P_G|x> = |Gx>`,
`Z_t|x> = (-1)^{t·x}|x>`, and `D|x> = i^{wt(x)}|x>`. The source canonical
lift and the normalized section are

```text
K_G|x> = i^{q(Q_G)(Gx)}|Gx>,
J_G|x> = i^{wt(Gx)-wt(x)}|Gx>,
Q_G = I + G^{-T} G^{-1}.
```

The quadratic value is the source polar form modulo 4. PR #4002 proves
`K_G = J_G Z_{t_G}` with

```text
(t_G)_j = [q(Q_G)(G e_j) - wt(G e_j) + 1]_4 / 2,
```

and the cocycle

```text
K_H K_G = K_{HG} Z_{t_G + G^t t_H + t_{HG}}.
```

Masks add by XOR. Those identities are used here only for this `G`.

## The round trip

Direct inversion gives

```text
G^{-1} = (1, 2, 28, 4, 79, 8, 130, 32, 431),
t_G = 144, t_{G^{-1}} = 68.
```

The identity has tag 0, so

```text
K_{G^{-1}} K_G = Z_{144 + G^t 68} = Z_{256}.
```

`256 = 2^8`, so the character is the single coordinate sign on bit 8. It is
not the identity: the states with that bit set, 256 of the 512 addresses,
pick up phase `2` modulo 4, which is a factor `-1`.

The same permutation round trip under `J` is `J_{G^{-1}} J_G = J_I`. The
section phase of `J_I` is `wt(x) - wt(x) = 0`. Substituting `J` for `K` on
this pair therefore deletes `Z_256` and disagrees on those 256 states. The
binary permutation of either product is the identity, so the deleted object
is only that central character.

## What the recipe already records, and what it does not

The sign-+1 descriptor stores `phase = 3` and

```text
linear_Z4 = (1, 2, 2, 0, 2, 2, 3, 2, 2).
```

That Z4 vector is not the coboundary mask `144`. Paying the published
`linear_Z4` field does not display `Z_256`, and deleting the coboundary is a
separate change.

The descriptor's `rank` field is `0`. This note does not read that field as a
free child. Helper return, routing and tape are absent, so those charges are
unknown. Unknown charges are not zero. The sign itself is an exact factor
`±1`, so this boundary adds no further denominator.

The uncompensated `J` pair is consequently not a zero-cost rewrite of the
`K` pair. This is not a complete supplier invoice, a scalar-addition saving,
or a change of selected κ.

The old-version descriptors on the same register use the same columns with a
shorter entrance. They are not part of this pair.
