# The admissible count region and its boundary ranks

## Model

Unchanged from PR3570/PR3578/PR3589. Work in the full formal group algebra
`R = F2[Q8]` with distinct elements `1` and `z` and relations

```text
i^2 = j^2 = z,   z^2 = 1,   ji = z ij.
```

Every role carries independent arbitrary dirty input. Binary scalar `GL`
mixing is free. A paid factor is

```text
D_l = I + (1 + [g_l]) u_l v_l^T,   g_l in {i, j},   v_l^T u_l = 1,
```

with binary `u_l, v_l`. The endpoint is diagonal, with `t_i` copies of `zi`,
`t_j` copies of `zj` and the identity on every other role. Write
`t = t_i + t_j` and `n = n_i + n_j`, where `n_g` counts the `g`-labelled
calls. The number of restored dirty roles is any finite integer.

Let `X` have columns `u_l` and `Y` rows `v_l^T`; `X_g`, `Y_g` are the
`g`-labelled blocks and `P_g` the diagonal projector onto the `t_g` active
`g`-target coordinates.

## Inherited necessary conditions

PR3589 proves

```text
2n + n_i >= 6t - t_i,     2n + n_j >= 6t - t_j,     hence 5n >= 11t,
```

from the four boundary ranks `rank(X_i), rank(Y_i), rank(X_j), rank(Y_j) >=
r = 3t - n` and the rank identity `rank(X_g) + rank(Y_g) <= n_g + t_g` with
`rank(X_g Y_g) = t_g`. The same package records the trace parities
`n_i = t_i (mod 2)` and `n_j = t_j (mod 2)`. These are necessary conditions;
neither is re-proved here.

## The block rank floor

**Lemma.** `n_g >= t_g` for `g = i` and `g = j`.

**Proof.** The first-order identities of the model give `X_g Y_g = P_g`. Since
`X_g` is `t x n_g` and `Y_g` is `n_g x t`,

```text
t_g = rank(P_g) = rank(X_g Y_g) <= min(rank X_g, rank Y_g) <= min(n_g, t).  ∎
```

The last inequality is the only role of the ambient `t`; the floor itself is
`n_g >= t_g`, which is the statement that a label block must contain at least
one call per target of that label.

**The admissible region.** At size `n` for shape `(t_i, t_j)` the admissible
label splits are the pairs

```text
n_i + n_j = n,  n_i >= t_i,  n_j >= t_j,
n_i = t_i (mod 2),  n_j = t_j (mod 2),
2n + n_i >= 6t - t_i,  2n + n_j >= 6t - t_j.
```

The first two parity conditions and the two count inequalities are inherited;
the two rank floors are the new necessary conditions. The region minimum is
the least `n` admitting a pair.

**Remark (the floor is not vacuous).** Parity and the two count inequalities
alone admit `(n_i, n_j) = (0, 10)` for shape `(4,0)` at `n = 10` and
`(n_i, n_j) = (1, 9)` for shape `(3,1)` at `n = 10`. Both are removed by the
floor. For shape `(2,2)` at `n = 10` parity and the two count inequalities
already force `n_i, n_j >= 2`, so the floor adds nothing there; the resulting
four splits are `(2,8), (4,6), (6,4), (8,2)`.

## Boundary equality

**Lemma.** Suppose `2n + n_g = 6t - t_g` for a label `g` and `r = 3t - n > 0`.
Then

```text
rank(X_g) = rank(Y_g) = r,
dim(im Y_g cap ker X_g) = r - t_g,
```

and `X_g` is injective when `r = n_g`.

**Proof.** Equality in the count inequality is `n_g + t_g = 2r`. PR3589's
four-rank step gives `rank(X_g) >= r` and `rank(Y_g) >= r`, and the rank
identity gives `rank(X_g) + rank(Y_g) <= n_g + t_g = 2r`. Hence both ranks
equal `r`.

For the dimension, apply the rank-nullity step PR3589 records: for
`B: F2^m -> F2^t` and `D: F2^t -> F2^m` with `a = rank B`, `b = rank D` and
`p = rank(BD)`,

```text
b - p = dim(im D cap ker B) <= m - a.
```

Here `B = X_g`, `D = Y_g`, `m = n_g`, `a = b = r` and `p = t_g`, so the left
side is `r - t_g` and the equality case of the intermediate step is not
needed: the dimension identity holds for the actual maps. Injectivity is
`rank(X_g) = r = n_g` with a `t x n_g` block. ∎

**Consequences at the ten-call boundary of the open `t = 4` shapes.** With
`r = 3t - n = 2`:

```text
shape (2,2), split (2,8):  i-side equality, rank(X_i) = rank(Y_i) = 2 = n_i,
                           X_i injective,  im Y_i cap ker X_i = 0.
shape (2,2), split (4,6):  no equality on either label.
shape (3,1), split (7,3):  j-side equality, rank(X_j) = rank(Y_j) = 2,
                           dim(im Y_j cap ker X_j) = 1.
shape (4,0), split (6,4):  no equality on the i-label; the homogeneous
                           pair of PR3578 is the sharp statement there.
```

The rank floor and the equality statement are arithmetic consequences of
data PR3589 already uses. They add no new hypothesis to the model.

## What is not claimed

Nothing here constructs a ten-call word or excludes one at any role count.
The `{10,12}` minima of PR3570, PR3578 and PR3589 remain open; the package
narrows the label splits only. The explicit `F2` fixture is rank data, not a
word: it satisfies the block rank identities but no endpoint equation. The
three-target value nine is quoted from PR3536 and its retained PR3471
exclusion, not re-derived. No physical caller, invoice, supplier,
multiplication theorem, kappa or selected-frontier change is claimed.

## Credit

Nick Petalas/PR3570, PR3578 and PR3589 supply the model, the two count
inequalities, the four boundary ranks and the rank-nullity step used above;
PR3536 supplies the three-target minimum, PR3471 the retained three-role
exclusion. The block rank floor, the exact region computation and the
boundary equality statement are the new content. Independent human and
formal proof-kernel review are unclaimed.
