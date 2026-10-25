# Typed actual-width H and one rounded return

This is a finite, exact interface lemma for the first open question in
[discussion 1166, comment 19016699](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19016699).
It does not prove the multi-round stock bound, execute a production-size cube,
or change the selected exponent.

## Statement

Let `p >= 1` and `g >= 1`. A Gaussian numerator is a pair of integers `(re, im)`
in the closed unit disk, meaning `re^2 + im^2 <= 2^{2p}`. The represented value
is that pair divided by `2^p`. On a block of `N = 2^m` such gaussians, `m >= g`,
fix `g` distinct address bits. Write `H0 = [[1, 1], [1, -1]] / 2`, and let
`H` be `H0` tensored on those bits and the identity on every other coordinate.

Evaluate `H` exactly, then apply one truncation `Q_p` toward zero onto the
`p`-grid. Store the input and the returned words as two's-complement integers
of width `w = p + 2`, least-significant bit first. Bridge each returned
component to a most-significant-bit-first scan of the same width.

Then:

1. The exact numerator, in units of `2^{-(p+g)}`, is an integer of absolute
   value at most `2^{p+g}`. Signed width `p + g + 2` holds every such
   numerator, and width `p + g + 1` does not: the constant input `2^p` attains
   `2^{p+g}` on the aligned character.
2. `Q_p` returns integers in `[-2^p, 2^p]`, still on the disk, in width `w`.
   Each real or imaginary component is wrong by strictly less than `2^{-p}`,
   so the Euclidean error is strictly less than `sqrt(2) 2^{-p}`.
3. `Q_p` commutes with a signed permutation of the coefficients. Truncation by
   floor division does not, because `(-1) // 2 = -1` while toward-zero sends
   `-1` at denominator `2` to `0`.
4. The bit bridge preserves each integer. Reading the least-significant-bit-first
   encoding as if it were most-significant-bit-first changes any
   non-palindromic word.
5. One call, with no layout permutation, performs `2 g N` real additions or
   subtractions, `2 N` truncations, and `6 N (p + 2)` bit reads together with
   the same number of bit writes. Two word tapes are rewound to their first
   bit. A record permutation, when used, adds four word transfers per Gaussian
   (read and write of both components).

The old outer constructor admits a root only when
`plan.dimension_exponent == (1, 40)`. The frozen active-width planner computes
`K = floor(selected^{1/500})` and does not assign `dimension_exponent`. The
typed plan check uses the matched floor and the cardinality

```text
gaussians = outer_rows * 2^{left + selected * K + right} * coefficients
```

instead of that guard.

## Why the width and the error are exact

The unnormalized Walsh sum on `g` bits is `sum_x chi(x, y) A_x`. Each `|A_x|`
is at most `2^p`, and there are `2^g` characters, so the sum is at most
`2^{p+g}`. Equality holds for the constant input `A_x = 2^p` at the trivial
character. A signed word of width `t` represents `[-2^{t-1}, 2^{t-1} - 1]`.
Width `p + g + 1` stops at `2^{p+g} - 1`. Width `p + g + 2` reaches
`2^{p+g+1} - 1`, which contains both `2^{p+g}` and `-2^{p+g}`.

Dividing by `2^g` toward zero leaves a remainder of absolute value at most
`2^g - 1` in units of `2^{-(p+g)}`. That is strictly less than one `p`-grid
step. The same bound on both components gives Euclidean error strictly less
than `sqrt(2) 2^{-p}`. Toward-zero moves each component toward the origin, and
`H0` has `L1` row norm one, so a disk input returns a disk output. This is the
same endpoint shape as Jose Manuel's normalized `H0` statement; the new content
is the typed width, the single truncation, and the bit-scan invoice.

## Matched bits, not another arithmetic oracle

Nick Petalas's frozen `OuterLayer.__init__` requires
`dimension_exponent == (1, 40)`. Jose Manuel's frozen `ActiveWidthPlan.compute`
sets `d` from the selected count and `K` from `floor_power(d, 1, 500)`. Those
two source texts do not join: the planner never writes the exponent the
constructor demands.

On every common round of the ten small layouts below, the matched root bits

```text
right + rho + t K,  0 <= t < g,
rho = (h - b) mod K,  b = (ell - 1) mod K
```

are exactly the bits of height `h` in the `K`-layout. For three short axes,
`ell = 3` and `K = 1`, height `0` occupies bits `{0, 1, 2}`. The same names in
the pre-layout order occupy `{0, 2, 4}`.

The degree-`2` calibration `d = 4`, `g = 3` has `floor(d^{1/2}) = 2` and
`floor((d - 1)^{1/2}) = 1`. It is a stand-in for the production identity
`floor(k^{500}^{1/500}) = k` and `floor((k^{500} - 1)^{1/500}) = k - 1`, not a
legal outer cube. On 32 addresses with the single nonzero numerator `(8, 0)` at
address `0` and `p = 3`:

- bits `{0, 1, 2}` return `(1, 0)` at address `2`;
- bits `{0, 2, 4}` return `(0, 0)` there.

The matched layout of the 64-address three-short cube fixes this origin
impulse, and the height-`0` root bits are `{0, 1, 2}`, so the same return
survives that permutation. The layout is nevertheless nontrivial: a
nonconstant disk pattern is moved, at `256` word transfers.

For `k = 2` and `k = 3` the production floors and both `p`-thresholds are
checked as exact integers, including the caller's multiples of six. At `k = 2`
those admitted precisions are `2^{20000} + 2` and `(2^{500} + 1)^{40} + 5`.
The address-extent ratio between `K = k` and `K = k - 1` is `2^{k^{500} - 1}`.
No tape of that size is allocated. A feasible plan with selected width `3`,
`K = 1`, left `2`, right `1` and four coefficients has `256` gaussians. The
typed check admits it. The `(1, 40)` guard rejects it, and `K = 2` fails the
matched floor.

## Invoice boundary

The counts above are one typed round. They do not include descriptor updates,
previous-output reset, borrowed restoration, private erasure, or a fixed
cube buffer carried across rounds. Clear1nsight's sufficient multi-round
allowance `Q <= C M R (r w + A + p^3) + poly(p)` is still a criterion, not a
supplied contract. This package stops at that point.

The ten layouts are the geometries already used by the matched-layer checker:
`(ell, long flags, K)` equal to `(2, (F,), 1)`, `(2, (T,), 1)`,
`(3, (F, F), 1)`, `(3, (T, F), 1)`, `(3, (T, T), 1)`, `(3, (F, F, F), 1)`,
`(3, (T, F, T), 1)`, `(3, (F, F, F, F), 2)`, `(3, (T, F, F, F), 2)`, and
`(4, (T, F), 2)`. Eighteen common-round bit identities are checked there.

The `g = 1`, `p = 3` disk is exhaustive: `197` numerators and `38,809` ordered
pairs, each compared with the explicit two-point matrix. The constant and
negative-constant inputs check the sharp numerator. A separate `g = 3`, `p = 4`
constant block checks the same bound one tensor higher.

## What was not run

No production T74 root, no PR3617 diagonal, no all-round lifecycle, no selected
cold replay, and no execution at `ell >= 45,812,984,491`. The frozen planner
and outer constructor are hashed and read as text. They are not imported:
their modules are not on this branch.
