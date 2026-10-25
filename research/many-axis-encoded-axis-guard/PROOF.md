# Encoded axis guard for the many-axis prime band

The source under review is `TensorPlan` from PR #3935, as vendored by PR #4029
at `726c9a3a1dc58d2b1223dd681eb712255be407c1` and pinned here by SHA-256
`474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3`.
PR #4029's prime-supply prose is the claim being checked. This note does not
reprove Fiori–Kadiri–Swidinsky and does not run an encoded Count machine.

## What the encoded method is

`TensorPlan.production_axis(self, s, t)` is a predicate on two live Counts.
Its only `self` fields are `d`, `target_halo` and `w`. In source order its
four `multiply_small` constants are `4`, `2`, `2`, `2`, and its three `need`
messages are the lower ratio, the upper ratio and the period. The body names
no tape operation: no `rewind`, `read_fixed`, `write_fixed`, `read`, `write`,
`append` or `clear`.

`TensorPlan.__init__` loads each source word with `read_fixed` before the
single `self.production_axis(s, t)` call, and a `rewind` occurs at a later
line. Oddness (`s.read() == 1`) and the near-one test `s < t < 2s` are gates
in `__init__`, not in `production_axis`.

So this method does not lower a sequential prime queue onto a tape. A producer
meets it only by placing an already-loaded odd Count `s` next to its target
`t`. Head return of the sources, flags and axis-row tapes is an `__init__`
obligation after the guard returns.

## The three predicates

Write `g = t - s`, with `t > s`, and write `d`, `H` and `w` for the three
fields. The constants above are exactly

```
4 d g > s,     (2d - 1) g < s,     s > 2 (H + 2 w).
```

The first two are equivalent to `t / (4d + 1) < g < t / (2d)`.

## The prime band sits inside the ratio and near-one gates

PR #4029 uses, for each target scale,

```
I(t, d) = (t (1 - 1/(3d)), t (1 - 1/(4d))].
```

For every integer `d >= 1` and every real `s` in that interval,
`t/(4d) <= g < t/(3d)`. Both comparisons are strict against the encoded
thresholds because `1/(4d) > 1/(4d+1)` and `1/(3d) < 1/(2d)`. At the closed
endpoint `g = t/(4d)`, one still has `4 d g = t > s`. Thus every such `s`
satisfies both ratio predicates. Since `s <= t (1 - 1/(4d)) < t` and, for
`d >= 2`, `s > t (1 - 1/(3d)) >= (5/6) t > t/2`, the near-one gate
`s < t < 2s` holds as well.

The band alone does not imply oddness. For `t = 16` and `d = 2` the integer
`s = 14` lies in `I(16, 2)`, passes both ratios and near-one, and is even, so
`__init__` rejects it before `production_axis`.

## Period, and why the factor 2 is necessary

Assume `d >= 2`, `ell >= 2`, `t` is `2^ell` or `2^(ell-1)`, and
`K = H + 2w <= 2^(ell-3)`. Every integer `s` in `I(t, d)` satisfies

```
s > t (3d-1)/(3d) >= 2^(ell-1) * 5/6 = 2^(ell-2) * 10/6 > 2^(ell-2) >= 2K.
```

The coefficient `5/6` is the `d = 2` case; larger `d` only raises it. The
inequality is strict, so the integer `s` is at least `2^(ell-2) + 1` when
`2K` equals that power of two. Prime abundance is not used.

The final encoded doubling is not optional. For `t = 1024`, `d = 4` and
`s = 939`, the point lies in the band and passes both ratios, and `s > 470`,
but `s > 2 * 470` fails. A lowering that keeps only `s > H + 2w` accepts a
source the method rejects.

## Product room, after the band

Let `D = d - 1`, matching PR #4029's reading that the internal `d` is one more
than the resampled axis count. For `x = 1/(3d)` and every integer `D >= 1`,

```
(1 - x)^D >= 1 - D x = (2D + 3) / (3D + 3) > 2/3,
```

so a product of `D` band ratios is strictly above `2/3` and the reciprocal
target/source product is strictly below `3/2`. This is the algebraic step only.
It does not count primes.

## What remains outside the method

`production_common` still carries the Gaussian policy, separation and restored
error margin, and it is invoked only after every axis guard returns. The
imported prime-count cutoff is untouched. No encoded tape scheduler is run.
