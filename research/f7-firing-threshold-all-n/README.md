# The first all-sound length of the fixed L/2 substitution, for every n ≥ 5

**Claim type: a proof for every n ≥ 5, with finite checks and explicit
witnesses. No new κ.** The selected conditional κ stays
`0.001672660197076918`.

## Object

[PR #4322](https://github.com/CrocSwap/integer-mult-bounds/pull/4322)
(unpaidmoon) studies the fixed `L/2` substitution on prefix walks of `F_2^n`.
A nonzero mask fires on a universal simple restored word when

```text
base < excess <= base + d^2,     base(n, L) = (L/2)(L/2 - 1) - (2^(n-1) - 1).
```

It found that the firing set is empty from `L = 14` at `n = 4`, and it left
three questions open:

- the first all-sound length at `n = 5`;
- whether larger `n` repeat the collapse;
- whether "the firing set eventually becomes empty for every n" (it says
  neither of its results shows this).

[#4348](https://github.com/CrocSwap/integer-mult-bounds/pull/4348) answered
the first by census: the answer is 26.

## Theorem

For every `n ≥ 5`, the first even length at which no mask fires on any
universal canonical word is exactly

```text
L*(n) = 2^n - 2 floor(sqrt(2^(n-1) - 1)).
```

From `L*(n)` up to `2^n`, every functional is sound on **every** `L`-point
subset of `F_2^n`. At `L*(n) − 2` a weight-one mask fires on an explicit
word. Values:

| n | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 16 | 20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `L*` | 14* | 26 | 54 | 114 | 234 | 482 | 980 | 4006 | 65174 | 1047128 |

`n = 4` (marked *) is #4322's theorem: there the closed form would give 12,
but another split binds. `2^n − L*(n) ≈ 2^((n+1)/2)`. The answer at `n = 5`
agrees with #4348's census.

So the collapse recurs for every `n`, and only near-Hamiltonian lengths are
safe for large `n`.

## Proof

**1. Min-sumset cap.** For `A ⊆ F_2^k` with `|A| > 2^(d−1)`,
`|A + A| ≥ 2^d`.

By Kneser's theorem, `|A+A| ≥ 2|A+H| − |H|`, where `H` is the stabilizer of
`A+A`, of order `2^h`.

- If `h ≥ d`, then `|A+A| ≥ |H| ≥ 2^d`.
- Otherwise `A+H` has `a > 2^(d−1−h)` cosets, so
  `|A+A| ≥ (2a−1)2^h ≥ 2^d + 2^h`.

Equality holds for `A` inside a subgroup of order `2^d`.

A level set of a nonzero functional is an affine flat, and differences in
characteristic 2 are sums. So a `k`-point side has excess at most
`e(k) = C(k,2) − 2^⌈log₂k⌉ + 1`, and a split `(s,t)` has excess at most
`e(s) + e(t)`.

**2. The binding split.** Write `s = 2^(n−1)` and `L = 2(s − j)`.

For the split `(s, s − 2j)`, a full level set against the rest, with
`s − 2j > 2^(n−2)`, direct expansion gives

```text
base(n, L) − (e(s) + e(s − 2j)) = (s − 1) − j².
```

Take `L ≥ L*(n)`, so `j ≤ ⌊√(s−1)⌋`. For `n ≥ 6`, every split `(s', L−s')`
then has both parts in `(2^(n−2), 2^(n−1)]`. On that range `e` is
`C(·,2)` minus a constant, which is convex, so the split cap is largest at
the extreme split. Hence the cap is at most `base`, and nothing fires on any
subset. `n = 5` is covered by the full scan.

**3. Sharpness.** Take `j = ⌊√(s−1)⌋ + 1` and `t = s − 2j`. The walk is built
in two halves, using bit 1 as `x_1`:

- **The half `x_1 = 0`.** All of it is traversed along the reflected Gray
  cycle of the other `n − 1` bits, cut at its closing edge.
- **The half `x_1 = 1`.** A "ladder" path through exactly `t` points: the
  first `t/2` rows of the lower Gray cycle, on both values of the top bit.
- **The halves join** at the two ends of the cut edge.

The result is a simple closed walk of length `L*(n) − 2`, and it is
universal. For the mask `e_1`:

- the full side has excess `e(s)` exactly;
- the other side has `t > 2^(n−2)` points of one coset, so its sum set is
  the whole subgroup and its excess is `e(t)` exactly;
- the total exceeds `base` by `j² − (s−1) > 0` and is at most `base + j²`,
  so `e_1` fires. The canonical relabeling carries this to a mask of the
  canonical word.

## Checks in `verify.py`

| Check | Result |
| --- | --- |
| `|A+A| ≥ 2^⌈log₂|A|⌉` and the cap `e(k)` | exhaustive in `F_2^k`, `k ≤ 4` (all 65,536 subsets at `k = 4`); the cap is attained exactly |
| Cap threshold by a full split scan | 6, 14, then exactly the closed form for every `5 ≤ n ≤ 22` |
| `t > 2^(n−2)` at `L*` | every `6 ≤ n < 40` |
| Explicit word at `L*(n) − 2`, `n = 5..11` | simple, closed, universal; `e_1` fires; the canonical word fires its relabeled mask |
| Controls of length `L*(n)` | nothing fires: every mask for `n ≤ 8`, `e_1` for `n ≤ 11` |
| #3733's `(4,12)` on main | still fires, so the `n = 4` threshold 14 is attained |

## Not covered

- Which masks fire below `L*(n) − 2`, and whether the firing set is
  monotone below that.
- `(7, 18)` and `(7, 20)`. Those are far below `L*(7) = 114`, so this theorem
  says nothing there.
- Any change to a retained exclusion.

## Reproduce

```sh
python3.12 -B research/f7-firing-threshold-all-n/verify.py
```

It prints `PASS_F7_FIRING_THRESHOLD_ALL_N` in about 6 seconds, using only the
standard library.

## Open next questions

None for the first all-sound length; it is decided for every `n ≥ 4`.

## Credit

The model and the `n = 4` theorem are unpaidmoon's (#4322), building on Nick
Petalas's #3699 and #3733. Kneser's theorem is classical. Prepared by Ryanson
Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
