# A square i-block cannot meet the mixed Q8 count boundary

## Statement

Work in the full formal group algebra `F2[Q8]`, with distinct elements
`1` and `z`, relations `i^2=j^2=z`, `z^2=1` and `ji=z ij`. Every role
starts with independent arbitrary dirty input. Free operations are binary
scalar GL changes of basis. Each paid call is

```text
D_l = I + (1+[g_l]) u_l v_l^T,   g_l in {i,j},   v_l^T u_l = 1,
```

with binary vectors. The endpoint is diagonal: `t_i` copies of `[zi]`,
`t_j` copies of `[zj]`, and the identity on every other role. The number
of restored dirty roles is any finite integer. Write `t=t_i+t_j`,
`n=n_i+n_j`, and write `n_g` for the number of paid calls labelled `g`.

**Square-block lemma.** If `t_i>=1` and `n_i=t_i`, then

```text
n_j >= 2 t_i.
```

Trace parity, recorded below, then forces `n_j` to the least integer that
is at least `max(t_j, 2 t_i)` and congruent to `t_j` modulo 2. The
symmetric statement holds with the labels exchanged.

**Ray theorem.** Let `k` be a positive integer. No exact word for `4k`
copies of `[zi]` and `k` copies of `[zj]` has length `11k`. Every exact
word for that shape therefore has length at least `11k+2`. The same holds
with the two target labels exchanged. The direct positive-generator word
still has length `15k`, so the exact minimum on this ray lies in
`{11k+2, 11k+4, ..., 15k}`.

**Shape (7,1).** The same lemma excludes every split with `n_i=7` and
`n_j<=13`. In particular the count-relaxation witness `(n_i,n_j)=(7,13)`
is unrealizable. It does not exclude the other three 20-call splits
`(9,11)`, `(11,9)` and `(13,7)`. No 20-call word is constructed or ruled
out. The direct word has length 24, so the exact minimum remains in
`{20,22,24}`.

This is a scoped obstruction inside the existing model. It is not a new
alphabet, a physical caller, a supplier admission, a multiplication
theorem, or a new kappa. The selected conditional value
`0.001672660197076918` is unchanged. Independent human and formal
proof-kernel review are unclaimed.

## Inherited equations

The chronological model is the one in
`research/q8-mixed-boundary-rank/PROOF.md` and
`research/q8-homogeneous-mixed-floor/PROOF.md`. Those proofs are pinned
inputs. The block expansion used here is written out so that the mixed
endpoint does not silently inherit the homogeneous relation `X_j Y_j=0`.

Conjugate each paid projector by the free scalar mixing accumulated
before it. Augmentation sends every paid factor and the endpoint to `I`,
so the remaining scalar factor is `I`. Let `X` have columns equal to the
active parts of the `u_l`, and let `Y` have rows equal to the active parts
of the `v_l^T`. Let `L` be the strictly lower-triangular part of the
full-role Gram, with later calls in later rows, formed before this
restriction. Dirty coordinates may contribute to `L`. They do not appear
in the active matrices `X` and `Y`.

Order the active coordinates as the `[zi]` targets followed by the `[zj]`
targets. The normalized endpoint gives complementary diagonal projectors
`P_i` and `P_j` with

```text
X_i Y_i = P_i,   X_j Y_j = P_j,   XY = I_t,
P_i + P_j = I_t,   P_i P_j = 0,
rank(P_i)=t_i,     rank(P_j)=t_j.
```

Write `E_g=im(P_g)`. Then `E_i` and `E_j` intersect trivially and span
the active space. The trace argument in the mixed-boundary proof gives
`n_i ≡ t_i (mod 2)` and `n_j ≡ t_j (mod 2)`, hence `n ≡ t (mod 2)`.
The same proof gives the cubic count inequalities

```text
2n + n_i >= 6t - t_i,    2n + n_j >= 6t - t_j,
```

and therefore `5n >= 11t`. The block floors `n_g >= t_g` are the
rank consequence `rank(X_g Y_g)=t_g` in
`research/q8-count-region-rank-floor/PROOF.md`. The nonzero-product
charge used below is the same proof's inequality: if `B` is `t × m` and
`D` is `m × t`, then

```text
rank(B) + rank(D) <= m + rank(BD).
```

Applied to each label, this is

```text
rank(X_g) + rank(Y_g) <= n_g + t_g.
```

## The two quadratic orientations, without grouping

Let `c(i,i)=c(j,j)=c(j,i)=1` and `c(i,j)=0`. For a later call `l` and an
earlier call `a`, the tau coefficient of that pair is
`c(g_l,g_a)` times the full-role dot `v_l^T u_a`. Both `[zi]` and `[zj]`
have tau coefficient 1, so the active tau coefficient of the endpoint is
`I_t`. The mixed-boundary proof records this as `XHY=I_t` for
`H=L+E_i L E_j`, where `E_i` and `E_j` are now the diagonal projectors on
call coordinates. That `H` is `L` with every chronologically earlier
`j`-call / later `i`-call entry deleted. It is still strictly lower
triangular, so `I+H` is invertible. Combined with `XY=I_t`,

```text
X(I+H)Y = 0.
```

Restrict the sum to labels. On an i-call row, `c(i,j)=0`, so the row of
`(I+H)Y` uses only earlier i-calls. In the chronological order of the
i-calls those rows are exactly `K_i Y_i`, where `K_i=I+L_ii` and `L_ii`
is the strict lower Gram among i-calls. Thus `K_i` is unitriangular and
invertible, whether or not dirty coordinates contributed to `L_ii`, and
whether or not j-calls sit between the i-calls. On a j-call row every
earlier call survives, and those rows are `L_ji Y_i + K_j Y_j`. Therefore

```text
X_i K_i Y_i + X_j(L_ji Y_i + K_j Y_j) = 0.          (Q)
```

The automorphism swapping `i` and `j` swaps the two inverse-generator
targets and replaces `c` by the table that deletes later-`j` / earlier-`i`
pairs instead. The same expansion yields

```text
X_i K_i Y_i + (X_i L_ij + X_j K_j) Y_j = 0.         (Q')
```

Neither identity uses `X_j Y_j=0`. That relation is special to a
homogeneous `[zi]` endpoint and is not assumed here.

## Proof of the square-block lemma

Assume `n_i=t_i>=1`. Then `X_i` is `t × t_i` and
`rank(X_i Y_i)=t_i`, so `rank(X_i)=rank(Y_i)=t_i`. In particular `X_i`
is injective and `im(P_i) ⊆ im(X_i)`. The two spaces have the same
dimension, so

```text
im(X_i) = E_i.
```

The same count shows that `Y_i`, which is `t_i × t`, is surjective.
Since `K_i` is invertible,

```text
rank(X_i K_i Y_i) >= rank(X_i) + rank(Y_i) - n_i = t_i.
```

The product also has rank at most `t_i`, so its rank is `t_i`. Its image
lies in `im(X_i)=E_i` and therefore equals `E_i`.

Equation (Q) says that this product equals `X_j` times a matrix, so
`E_i ⊆ im(X_j)`. Equation (Q') says that its rank is at most
`rank(Y_j)`, so `rank(Y_j) >= t_i`. The first-order identity
`X_j Y_j=P_j` gives `E_j ⊆ im(X_j)`. The sum `E_i+E_j` is direct, hence

```text
rank(X_j) >= t_i + t_j.
```

The nonzero-product charge on the j-block is then

```text
n_j + t_j >= rank(X_j) + rank(Y_j) >= (t_i + t_j) + t_i,
```

so `n_j >= 2 t_i`. Dirty coordinates never enter this last comparison:
they can change the entries of `K_i`, but not its invertibility, and the
images are images in the active coordinate space.

If instead `n_j=t_j>=1`, the label-swapping automorphism gives
`n_i >= 2 t_j`.

## The rays where 11t/5 is an integer

Let `t_i=4k` and `t_j=k` for a positive integer `k`. Then `t=5k` and
`11t=55k`, so the inherited inequality `5n>=11t` is `n>=11k`. Suppose
there is a word with `n=11k`. Then `5n=11t`. The two cubic inequalities
sum to `5n` on the left and `11t` on the right, so each is an equality:

```text
2n + n_i = 6t - t_i = 26k,    2n + n_j = 6t - t_j = 29k.
```

Hence `n_i=26k-22k=4k=t_i` and `n_j=29k-22k=7k`. The square-block lemma
requires `n_j >= 2 t_i = 8k`. But `7k < 8k`, a contradiction. There is
therefore no exact word of length `11k`.

The trace parity is `n ≡ t ≡ k (mod 2)`, and `11k` has that same parity,
while `11k+1` does not. The next admissible integer length is `11k+2`.

The direct word applies the matching positive generator three times on
each active coordinate and leaves every dirty spectator fixed. It uses
`3t=15k` calls and meets the endpoint in `F2[Q8]`. The verifier checks
this word for the representative shapes `(4,1)` and `(7,1)`, including
one restored dirty coordinate. The general direct-sum extension to `k`
copies is the same coordinatewise construction; it is not a search.

The exchanged ray `t_i=k`, `t_j=4k` is the image of this ray under the
automorphism, so it has the same length gap.

This is the simultaneous equality case asked for on the real boundary
`t_i=4 t_j`. Equality in `5n=11t` already forces the unique split
`(n_i,n_j)=(4k,7k)`, and that split is the square i-block forbidden above.
No further cubic-rank saturation has to be assumed.

## What remains at seven zi targets and one zj target

Here `t_i=7`, `t_j=1`, `t=8`. The inherited bound gives `5n>=88`, so
`n>=18`, and parity makes `n` even. The quadratic charge is not required
for the ray theorem, but it is the reason the published relaxation minimum
at this shape is 20 rather than 18, so it is recorded.

From (Q) and (Q'), `rank(X_i K_i Y_i)` is at most both `rank(X_j)` and
`rank(Y_j)`. Also `rank(X_i)` and `rank(Y_i)` are at least `t_i`, and
`K_i` is invertible, so

```text
rank(X_i K_i Y_i) >= 2 t_i - n_i
```

whenever the right side is positive; if it is negative then `n_i>2 t_i`
and `2 n_i+n_j > 4 t_i - t_j` holds for every `n_j>=0`. In the positive
case the two rank bounds and `rank(X_j)+rank(Y_j)<=n_j+t_j` give

```text
2 n_i + n_j >= 4 t_i - t_j.
```

The label swap gives the companion inequality. At `(7,1)` the first
inequality says `2 n_i+n_j >= 27`. The old cubic region still allows
`(7,11)`, total 18, because `2·7+11=25<27`. The strengthened integer
region has minimum 20. Its four parity-legal splits at total 20 are

```text
(7,13), (9,11), (11,9), (13,7).
```

The square-block lemma, with parity, requires `n_j>=15` whenever
`n_i=7`. Thus `(7,13)` is impossible, and so is every shorter square
i-block. The other three splits have `n_i>7`. The lemma does not touch
them, and this package does not claim that a 20-call word is impossible.

## What is not claimed

The factor `11/5` is not replaced by a new universal constant. Shapes
outside the two rays, including `(7,1)`, may still meet their own
relaxation minima. No word of length `11k+2` is constructed. No
eight-coefficient search of the surviving `(7,1)` splits is part of the
argument. An exploratory satisfiability encoding of those splits was not
retained: a timeout is not an exclusion. No physical layout, scalar route,
restoration, hosting, precision, or recursive invoice is priced. Unknown
physical costs are not zero. The selected frontier is unchanged.

## Credit

Nick Petalas's PR3570, PR3578, PR3589 and PR3736 retain the mixed cubic
identity, the homogeneous quadratic method, the mixed boundary ranks and
the preceding count region. The pinned proofs rederive those premises.
PR3536 retains the sign-sensitive quadratic chronology and PR3558 the
cyclic subspace method. The retained lineage of those packages includes
PR3517, Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna
Davis, steph4n-gh and the credited Q8 register sources. Standard
rank-nullity and Sylvester's inequality are not claimed as new.

Nick Petalas's open PR #4234 is the source of the question this package
answers in part: it proves the shape-sensitive relaxation, names
`(7,13)` as a minimizing count witness for seven `[zi]` targets and one
`[zj]` target, and leaves both a 20-call word and the equality case
`t_i=4 t_j` open. This package does not replay that enumeration and does
not depend on the unmerged tree. The square-block image collision, the
resulting empty equality case on both rays, and the exclusion of `(7,13)`
are the new steps.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0. No independent human or formal proof-kernel review is claimed.
