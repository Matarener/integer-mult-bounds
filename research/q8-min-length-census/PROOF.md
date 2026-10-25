# Attainment of the mixed-negative Q8 bound for t <= 2

## Model

Unchanged from PR3570/PR3578/PR3589. Work in the full formal group algebra
`R = F2[Q8]` with distinct elements `1` and `z` and relations

```text
i^2 = j^2 = z,   z^2 = 1,   ji = z ij.
```

Every role carries independent arbitrary dirty input. Binary scalar `GL`
mixing is free. A **paid factor** is

```text
D_l = I + (1 + [g_l]) u_l v_l^T,     g_l in {i, j},     v_l^T u_l = 1.
```

A **word** is an ordered sequence of paid factors acting on a `roles x roles`
matrix over `R`. The **endpoint** is diagonal, with `t_i` copies of `zi`,
`t_j` copies of `zj` and the identity on every other role. Write `t = t_i + t_j`
and `n` for the number of paid factors. Any finite restored dirty workspace is
permitted.

## Inherited lower bound and parity

PR3589 proves, for every exact word,

```text
2n + n_i >= 6t - t_i,        2n + n_j >= 6t - t_j,        hence 5n >= 11t.
```

It also records the inherited trace parity

```text
n_i = t_i mod 2,   n_j = t_j mod 2,   hence n = t mod 2.
```

These are **necessary** conditions. Neither is re-proved here.

## Statement

**Theorem.** For every mixed-negative endpoint with `t = 1` or `t = 2`, the
minimum number of paid factors over all role counts and all finite restored
dirty workspace is

```text
t = 1: 3        t = 2: 6.
```

**Proof.** Lower bound: PR3589 gives `5n >= 11t`. For `t = 1` this is
`n >= 11/5`, so `n >= 3` with no parity input needed. For `t = 2` it is
`n >= 22/5`, so `n >= 5`; the parity `n = t mod 2` then forces `n >= 6`. These
exclusions hold at every role count, because both premises of PR3589 are
role-free.

Upper bound: let `spine(g, a)` be the three paid factors with
`u = v = e_a` and label `g`. Because `u = v = e_a` has `v^T u = 1`, the factor
is legal. On the `a`-th role it acts as `I + (1 + [g])`, which multiplies that
role by `[g]`; on every other role it is the identity. Hence

```text
spine(g, a) applied three times  multiplies role a by g^3.
```

Direct computation in `R` gives `i^3 = zi`, `j^3 = zj` and `z^2 = 1`. For a
target list of length `t`, applying `spine` on the corresponding label to each
target role in turn gives the exact diagonal endpoint in `3t` calls. For
`t = 1` that is `3` and for `t = 2` that is `6`, matching the lower bound. ∎

The minimum is therefore attained, and for `t <= 2` the parity-rounded
`11t/5` constant cannot be improved.

## Sharpness consequences

- **The constant is sharp at `t = 1` and `t = 2`.** Any strictly stronger
  necessary function of `t` fails at these two points. This answers PR3589's
  open question "Is the uniform `11t/5` constant sharp?" in the affirmative for
  `t <= 2` only.
- **The bound is not attained for `t >= 3` by the witness family.**
  `t = 3` admits bound value `7` against a `9`-call witness; `t = 4` balanced
  admits `10` against a `12`-call witness. The minima stay in `{7,9}` and
  `{10,12}`.

## Independent finite cross-check

The five complete breadth-first searches in `verify.py` enumerate **every**
word on one and two roles up to lengths `2` and `5`, and find none reaching the
corresponding endpoint. State counts are `6`, `6` and `56,084`. Because the
theoretical lower bound is role-free, these receipts are an independent check
of the model implementation and of the witnesses, not the source of the
exclusion.

The verifier also checks all `64` Q8 group products against an independent
signed-unit table, so the group law used by the witnesses is not assumed from
the product routine it is meant to test.

## What is not claimed

Nothing here excludes a shorter word at `t >= 3`, decides the `t = 3` or
balanced `t = 4` minima, re-proves PR3589, supplies a physical implementation
or invoice, or improves the selected kappa `0.001672660197076918`. The
ten-call balanced four-target question remains open. A randomised search over
`4` to `8` roles is recorded in VALIDATION.md as a **search failure**: its
failure to find a word proves nothing.

## Credit

Nick Petalas/PR3589 supplies the bound and the parity; PR3570 the mixed cubic
identity; PR3578 the two-orientation boundary-rank method; PR3536 the
sign-sensitive quadratic chronology; PR3558 the cyclic subspace argument. Only
the witnesses, the complete small-case census and the sharpness consequence
are new here.