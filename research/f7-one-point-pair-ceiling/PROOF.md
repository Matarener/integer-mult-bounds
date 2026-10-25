# Coset-wide one-point pair ceiling

## Statement

Work in `F_2^7`. Let `Q = 64` be the size of each weight-parity coset. For integers
`s, t` with `0 <= s <= Q` and `1 <= t <= Q`, write

```
B0 = C(s,2) + C(t,2) - (Q-1),
need = ceil((s*t - Q) / 2).
```

The split survives the basic pair test when `s*t >= Q`, `B0 >= 0`, and there
exist integers `a, b >= 0` with `a + b <= B0` and `B0 + a*b >= need`. Equivalently,
`B0 + floor(B0/2)*ceil(B0/2) >= need`.

Let `E` be an `s`-point subset of the even-weight coset and `O` a `(t-1)`-point
subset of the odd-weight coset. Let `S = sum_x A_x B_x` be the pair product of
that partial pair of sets, and for an odd point `p` not in `O` let `f(p)` be the
product added by inserting `p`. Then

```
max_p (S + f(p)) >= need.
```

In particular the strict pruning test `max_p (S + f(p)) < need` deletes no such
branch. Both orientations are included: the missing point may lie on either side.
The parts-at-most-11 window, which contains every ordered length-22 split with
both parts at most 11 and the length-20 representatives other than `(8,9)`, is
the row table in `verify.py`.

This is a necessary-condition bound on sets. It is not a prefix-walk search, not
a two-point bound, and not a determination of `f(7)`.

## Pair product and the one-point increment

For a nonzero even mask `x`, `A_x` (respectively `B_x`) counts unordered pairs
inside `E` (respectively `O`) with difference `x`. For an odd mask `y`, `r_y`
counts ordered cross pairs from `E x O` with difference `y`. The identity

```
sum_y C(r_y, 2) = 2 S
```

is the double count in `research/f7-weight-parity-census-correction/MATH.md`
section 3: each even pair and odd pair with the same difference determines two
cross-pair collisions. Consequently `sum_y r_y^2 = 4S + |E|·|O|`.

Adding an odd point `p` not in `O` creates one new odd pair `{p, q}` for each
`q` in `O`. These differences `p xor q` are nonzero and pairwise distinct, and
`E` is unchanged, so the pair product increases by exactly

```
f(p) = sum_{q in O} A_{p xor q}.
```

The completed product is `S + f(p)`.

## Two sums of f

Summing over the whole odd coset, each fixed `q` makes `p xor q` run through
every even vector exactly once. The zero mask contributes nothing, and the
remaining masks contribute `C(|E|, 2)`. Hence

```
sum_{p odd} f(p) = |O| · C(|E|, 2) =: alpha.
```

Summing only over `p` in `O`, each unordered odd pair `{p, q}` contributes
`A_{p xor q}` once to `f(p)` and once to `f(q)`, so

```
sum_{p in O} f(p) = 2S.
```

The outside sum is `alpha - 2S`. If it is negative, no such pair of sets exists.
If `M = Q - |O|` outside points remain and the outside sum `T` is nonnegative,
those `M` nonnegative integers have maximum at least `ceil(T / M)`. Therefore

```
max_p (S + f(p)) >= S + ceil((alpha - 2S) / M)
```

whenever `T >= 0` and `M >= 1`. For `M = 1` the single outside value equals `T`,
so the completed product equals `alpha - S` exactly.

## Flattening lower bound

`sum_y r_y = |E|·|O| = N` and `sum_y r_y^2 = 4S + N`. Among nonnegative integer
vectors of length `Q` with sum `N`, the sum of squares is minimized when the
parts differ by at most one. If that minimum is `sigma`, then `4S = sum r^2 - N
>= sigma - N`, so

```
S >= S_min = ceil((sigma - N) / 4).
```

The flat vector need not itself satisfy `sum r^2 ≡ N (mod 4)`. The ceiling still
lower-bounds every realizable `S`, because every realizable sum of squares is at
least `sigma` and the corresponding `S` is an integer.

An upper bound used only for the one-outside-point case is the opposite extreme:
one bin holds all `N` crosses, so `S <= (N^2 - N) / 4`.

## Monotonicity for at least two outside points

Let `h(S) = S + ceil((alpha - 2S) / M)` for integers `S` with `alpha - 2S >= 0`.
Increasing `S` by one decreases the numerator by two. For `M >= 2` and numerator
`T >= 2`,

```
ceil(T/M) - ceil((T-2)/M) <= 1,
```

so `h` does not fall. Write `T = qM + r` with `0 <= r < M`.

- If `r >= 2`, then `T - 2` has remainder `r - 2` and the same quotient, and the
  ceilings differ by at most one.
- If `r = 1`, then `T - 2` has quotient `q - 1` and remainder `M - 1`, and both
  ceilings equal `q` and `q + 1` in that order.
- If `r = 0`, then `ceil(T/M) = q` and `T - 2` has quotient `q - 1` and remainder
  `M - 2`. For `M > 2` the new ceiling is `q`. For `M = 2` the remainder is `0`
  and the new ceiling is `q - 1`.

In every case the drop is at most one, so `h(S+1) >= h(S)`. The weakest value on
the feasible range is therefore `h(S_min)`. The verifier also checks the drop on
every residue for every `M` from 2 through 64.

For `M = 1`, `h(S) = alpha - S` decreases, and the weakest value is `alpha`
minus the largest conceivable `S`. That case is `t = Q`, far outside the
parts-at-most-11 window (`M >= 54` there). It is included in the full rectangle
so the boundary is not omitted.

## Finite certificate

For every basic-identity survivor with `n = 7` and both parts at most 64, the
bound just described is at least `need`. There are 3820 such survivors. The same
closed form was evaluated for `n = 3, 4, 5, 6` over the whole coset rectangle;
none fell below `need`. Those smaller checks are arithmetic, not a substitute
for the set identities.

The set identities, the outside-sum split, the averaging step, and one fresh
completion increment were checked on every even/odd subset pair in `F_2^3` and
`F_2^4`. The collision identity `sum C(r_y, 2) = 2S` on `F_2^4` is already
recorded by PR #3827; it is rechecked here only as a lemma of this argument.
The `f` sums and the completion increment are the part used below.

## Equality at (9, 9)

Here `need = 9`, `B0 = 9`, and the basic test survives. With one odd point
missing, `|O| = 8`, `alpha = 288`, `M = 56`, `N = 72`, `sigma = 88`, and
`S_min = 4`. Then `T = 280` and `ceil(T/M) = 5`, so `h = 9`.

The even set

```
{0, 3, 5, 9, 10, 33, 34, 40, 43}
```

and the odd set produced by the greedy below,

```
{1, 4, 16, 21, 64, 69, 81, 84},
```

realize `S = 4` with `f(p) = 5` at every odd `p` outside the odd set. Every
legal one-point completion therefore has pair product exactly 9. The greedy
scans the odd coset in increasing order and keeps a candidate only when
`(S, max outside f, index)` strictly improves. The verifier reruns it and
recomputes every completion from pair counts. Replacing `84` by `2` raises the
ceiling from 9 to 17.

`(7,11)` and `(11,7)` also have `h(S_min) = need` under ceiling division. No
realized set is claimed for those two rows. Replacing the ceiling by the floor
drops both arithmetic bounds from 7 to 6, so the integer lift is necessary for
this writeup. `(9,9)` is an exact division and is unchanged by that swap.
`(8,9)` and `(9,8)` do not reach this test: `B0 = 1` and `need = 4`, so
`B0 + a*b <= 1`.

## What the maximum does not say

The maximum is over the whole odd coset. A prefix walk may add only a neighbor
of the current vertex. That restricted maximum is at most the coset-wide maximum,
so a neighbor test can still fall below `need` on a branch where the coset-wide
test cannot. This package does not search walks.

A two-point window is the next partial test. One greedy sample on `(9,9)` reached
17, which is above `need` and is not a lower bound.

The `(9,9)` witness is a parity-legal pair of sets, not a prefix walk, so it is
not a counterexample to a walk-level exclusion. PR #3818 claims a different
union-support exclusion of `(9,9)`. PR #3731 claims census exclusions of
`(11,7)`, `(10,8)`, and `(11,8)`. Nothing here confirms or revisits those claims.
PR #3821 and PR #3699 already record the word
`01021323`; the fixture in `verify.py` only recomputes the split `(4,4)`, the
bit-0 split `(6,2)`, the excess 8, and the budgets 5 and 9 from MATH.md.
