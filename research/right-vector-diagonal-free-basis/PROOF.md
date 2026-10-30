# Free basis changes do not shorten a right-vector diagonal

## Model

Let `K` be a field and `R` an associative unital `K`-algebra with `K` central.
`R` need not be commutative, finite or local. Fix a register count `n >= 0`.
A paid factor is

```text
F = I + u y^T,    u in R^n,    y in K^n.
```

A free map is any `S` in `GL_n(K)`. A word is

```text
W = S_0 F_1 S_1 F_2 S_2 ... F_L S_L,
```

with `L` paid factors and free maps anywhere, including at both ends. Its
target is `diag(d_1, ..., d_n)` with `d_i` in `R`. Put

```text
t_K(d) = #{ i : d_i is not in K^x }.
```

For `K = F_2` the unit group is `{1}`, so `t_K(d)` is the count `t` of entries
different from 1 used by `research/f2-right-vector-diagonal-minimum`.

**Theorem.** The minimum number of paid factors in a word equal to
`diag(d)` is exactly `t_K(d)`, for every `n` and every `d` in `R^n`.

This answers that package's first open question: free `GL_n(F_2)` changes of
basis between paid factors never realize a diagonal with fewer than `t` factors.

## Normal form

Put `A_j = S_0 S_1 ... S_{j-1}` and `S = S_0 S_1 ... S_L`. Then

```text
W = F'_1 F'_2 ... F'_L S,     F'_j = A_j F_j A_j^{-1}.
```

Since `A_j` has entries in `K`,

```text
F'_j = I + (A_j u_j) (A_j^{-T} y_j)^T,
```

and `A_j^{-T} y_j` lies in `K^n`. So each `F'_j` is again a paid factor.
Conversely every product `F'_1 ... F'_L S` is a word. Thus the reachable
endpoints of length `L` are exactly `Q S`, with `Q` a product of `L` paid
factors and `S` in `GL_n(K)`.

## Column bound

Let `Q = F'_1 ... F'_L` and `Q_j = F'_1 ... F'_j`, `Q_0 = I`. Telescoping,

```text
Q - I = sum_j Q_{j-1} (F'_j - I) = sum_j c_j y'_j^T,    c_j = Q_{j-1} u'_j in R^n,
```

where `y'_j` lies in `K^n`. For `w` in `K^n`, `(Q - I) w = sum_j (y'_j . w) c_j`
is a `K`-combination of the `L` fixed vectors `c_j`. The `K`-linear map
`w -> (Q - I) w` from `K^n` to `R^n` therefore has image of `K`-dimension at
most `L`. This is the column argument of `research/f2-right-vector-diagonal-minimum`,
written for an arbitrary field. Note the right-hand factor `y'^T` multiplies
`w` before `c_j`; `K` central makes `(y' . w) c_j = c_j (y' . w)`.

## Kernel lemma

Suppose `W = D = diag(d)`. Then `Q = D T` with `T = S^{-1}` in `GL_n(K)`.
Let `w` in `K^n` satisfy `(D T - I) w = 0`, that is,

```text
d_i (T w)_i = w_i     for every i.
```

Both `(T w)_i` and `w_i` lie in `K`. Fix `i` with `d_i` not in `K^x`.

* If `(T w)_i != 0`, then `d_i = w_i (T w)_i^{-1}` lies in `K`. Since `d_i`
  is not in `K^x`, `d_i = 0`, and then `w_i = d_i (T w)_i = 0`.
* If `(T w)_i = 0`, the equation gives `w_i = 0`.

So the kernel lies in the coordinate subspace `{ w : w_i = 0 for d_i not in K^x }`,
whose dimension is `n - t_K(d)`. Rank-nullity over `K` gives

```text
dim_K (D T - I) K^n >= t_K(d).
```

## Lower bound

Combining the two displays, `t_K(d) <= dim_K (Q - I) K^n <= L`.

## Matching construction

Let `E = diag(e)` with `e_i = d_i` when `d_i` is in `K^x` and `e_i = 1`
otherwise. `E` is a free map. For each `i` with `d_i` not in `K^x`, the factor
`I + (d_i - 1) e_i e_i^T` is paid: its right vector `e_i` is in `K^n`.
Increments on distinct matrix units multiply to zero, so the product of these
`t_K(d)` factors is `diag(f)` with `f_i = d_i` off `K^x` and `f_i = 1` on it.
Then `diag(f) E = diag(d)`. The word has `t_K(d)` paid factors.

## Corollaries and boundaries

* `K = F_2`, any `F_2`-algebra: the exact minimum is `t`, with or without free
  `GL_n(F_2)` maps. This includes every group algebra `F_2[G]` and the narrower
  legal alphabet `I + (g - 1) x y^T` with binary `x, y`, `y^T x = 1`, of the
  `elementary-abelian-diagonal-minimum` and Q8 lineages. Free scalar mixing
  does not lower the diagonal count in the full nonidentity-label alphabet.
  Restricted label sets (for example only `{i, j}` in `F_2[Q8]`) can force
  more factors; that is outside this statement.
* Over a larger field, free maps absorb scalar diagonal entries. Over `F_3`,
  `diag(2, 2)` is itself a free map and costs no factor.
* The `K`-valued right vector is necessary. In `F_2[z_1, z_2]/(z_1^2, z_2^2)`
  the single factor `I + (z_1, z_2)^T (z_2, z_1)` equals
  `diag(1 + z_1 z_2, 1 + z_1 z_2)`, so `t = 2` drops to one factor
  (the witness of `research/f2-right-vector-diagonal-minimum`).
* Free maps must have entries in `K`. The kernel lemma uses that `T w` is
  `K`-valued; with `R`-valued free maps the statement is not asserted.

No native frame, hosting, routing, precision or recursive cost is priced. The
selected multiplication exponent is unchanged.

Produced by Nick Petalas. The column expansion, the right-vector alphabet and
the sharpness witness are Wentao Li's `research/f2-right-vector-diagonal-minimum`.
Apache-2.0.
