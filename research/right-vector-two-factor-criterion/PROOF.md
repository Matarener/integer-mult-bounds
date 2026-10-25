# Proofs

`K` is a field and `R` an associative unital `K`-algebra with `K` central. A
paid factor is `P(u, y) = I + u y^T` with `u` in `R^n` and `y` in `K^n`; a free
map is any `S` in `GL_n(K)`, used anywhere in a word. `cost(M)` is the least
number of paid factors in a word equal to `M` (infinite if none exists), and

```text
delta(M) = min over T in GL_n(K) of dim_K (M T - I) K^n.
```

Facts used from #4243 and #4099: `cost(M) >= delta(M)`, and every word can be
rewritten as `Q S` with `Q` a product of the same number of paid factors,
because `S P(u, y) S^{-1} = P(S u, S^{-T} y)`.

## Lemma 1 (merging)

`P(u, y) P(v, c y) = P(u + c v + c u (y^T v), y)` for `c` in `K`. Expand:
`(I + u y^T)(I + c v y^T) = I + u y^T + c v y^T + c u (y^T v) y^T`, and
`y^T v` is an element of `R`. Also `P(u, 0) = P(0, y) = I`.

## Theorem A (one factor, every n, every R)

`cost(M) <= 1` if and only if `delta(M) <= 1`, and then `cost(M) = delta(M)`.

*Proof.* `cost >= delta` gives one direction. If `delta(M) = 0`, then
`M T = I` and `M = T^{-1}` costs 0. If `delta(M) = 1`, then
`(M T - I) K^n = K w` for some `w` in `R^n`, so `(M T - I) e_j = c_j w` with
`c` in `K^n`, that is `M T = I + w c^T = P(w, c)`, and `M = P(w, c) T^{-1}`.

## Theorem B (two factors, n = 2, every R)

`cost(M) <= 2` if and only if some `G, H` in `GL_2(K)` give `N = G M H` with
`N12` in the right ideal `N11 R`.

*Proof.* (If.) Write `N12 = N11 C` and put `A = N11`, `B = N21`,
`D = N22 - N21 C`. Then

```text
F1 = P((A - 1, B), e1) = [[A, 0], [B, 1]],
F2 = P((C, D - 1), e2) = [[1, C], [0, D]],
F1 F2 = [[A, A C], [B, B C + D]] = N,
```

so `M = (G^{-1} F1 G)(G^{-1} F2 G) G^{-1} H^{-1}`, and each conjugate is a
paid factor.

(Only if.) Write `M = P(u1, y1) P(u2, y2) S`, padding with `P(0, y) = I`. If
`y1, y2` are dependent, Lemma 1 merges the two factors into one with a nonzero
`y` (or both are `I`); replace the second by `P(0, y2')` with `y2'`
independent. So `y1, y2` is a basis. Choose `G` with `G^{-T} y_i = e_i`. Then
`G M S^{-1} G^{-1} = P(u1', e1) P(u2', e2)`, which is
`[[A, 0], [B, 1]] [[1, C], [0, D]] = [[A, A C], [B, B C + D]]` for some
`A, B, C, D` in `R`. Its `(1, 2)` entry is `A C`, in `A R`. Take
`H = S^{-1} G^{-1}`.

## Corollary C (matrix algebras)

Let `R = M_m(K)` and view `M` as a `2m x 2m` matrix. Then `cost(M) <= 2` if
and only if there are nonzero `phi` in `(K^2)^*` and `t` in `K^2` with

```text
rank (phi ⊗ I_m) M = rank (phi ⊗ I_m) M (t ⊗ I_m).
```

*Proof.* In `M_m(K)`, `Z` lies in `A M_m(K)` exactly when the column space of
`Z` lies in that of `A`. Let `phi` be the first row of `G` and `t, s` the
columns of `H`. Then `N11 = (phi ⊗ I) M (t ⊗ I)`,
`N12 = (phi ⊗ I) M (s ⊗ I)`, and since `H` is invertible the column space of
`[N11 N12]` is that of `(phi ⊗ I) M`. So `col N12 ⊆ col N11` is the stated
rank equality. Every nonzero `phi` is a first row and every nonzero `t` a first
column.

## Theorem D (local algebras, n = 2)

Let the non-units of `R` form an ideal `J`. Every target `M` with an entry
outside `J` (in particular every invertible `M`) has `cost(M) = delta(M)`.

*Proof.* Permutation matrices `G, H` move a unit to position `(1, 1)`. Then
`N11 R = R`, so Theorem B gives `cost(M) <= 2`. If `delta(M) <= 1`, Theorem A
gives equality. Otherwise `2 = delta(M) <= cost(M) <= 2`.

## Corollary E (quotients and F2[S3])

If `rho: R -> R'` is a unital `K`-algebra homomorphism, then
`cost_R(M) >= cost_R'(rho(M))`, because `rho` maps paid factors to paid factors
and free maps to free maps. Since `delta(M) <= n` always, every target over
`F2[S3]` whose image under the surjection `rho: F2[S3] -> M_2(F_2)` is one of
the 72 cost-3 targets of #4265 costs at least 3 while `delta <= 2`. `rho`
extends the isomorphism `S3 = GL_2(F_2)` given by the action on the three
nonzero vectors of `F_2^2`; `verify.py` checks that it is a surjective unital
algebra map and lifts a three-factor word to an explicit target of cost
exactly 3.
