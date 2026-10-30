# Proof: fixed-point versus pinned exponential bounds

**Scoped written proof with an exact finite certificate. No new κ.**

## The two engines

Fix a rational `y` with `0 <= y <= 1/2`. Write `P = 256`, `δ = 2^-256`,
`θ = 2^-264`, `σ = P + 48 = 304` and `u = 2^σ`. For a rational `x`, `down(x)`
is the largest multiple of `δ` that is at most `x`, and `up(x) = -down(-x)`.

**Pinned series** (`research/complex-local-word-ceiling/ceiling.py`, `exp`).
Put `t_0 = 1`, `t_k = t_(k-1) y / k`, `s_k = t_0 + ... + t_k` and
`V_k = s_k + 2 t_k y / (k+1)`. Let `K` be the least `k >= 1` with
`t_k y < θ`. The engine returns

```text
lo_p = down(s_K),   hi_p = up(V_K).
```

**Fixed-point series** (`research/ceiling-exp-fixed-point/fast_exp.py`, `series`).
The lower call uses `γ = floor(y u) / u`, `τ_0 = 1` and
`τ_j = floor(u τ_(j-1) γ / j) / u`. It stops at the least `j = J >= 1` with
`γ = 0` or `τ_j γ < θ`. This matches the code's test
`term * coefficient < 2^(2σ - P - 8)` with `term = u τ_j`. It returns
`lo_f = down(S)`, `S = τ_0 + ... + τ_J`, because the final right shift by
`σ - P` is a floor at `δ`.

The upper call uses `γ' = ceil(y u) / u` and
`τ'_j = ceil(u τ'_(j-1) γ' / j) / u`. It stops at the least `J' >= 1` with
`γ' = 0` or `τ'_j γ' < θ`, adds `ρ = ceil(2 u τ'_(J') γ' / (J'+1)) / u`, and
returns `hi_f = up(S' + ρ)` with `S' = τ'_0 + ... + τ'_(J')`.

The loop limit of 10,000 is never reached. Fact 2 and Lemma 4 give
`J <= K <= 50` and `J' <= K + 1`.

## Theorem

For every rational `y` in `[0, 1/2]`:

1. `lo_f <= exp(y) <= hi_f`.
2. `lo_f` is `lo_p` or `lo_p - δ`.
3. `hi_f` is `hi_p - δ`, `hi_p` or `hi_p + δ`. The value `hi_p - δ` needs
   `J' = K + 1`: the fixed-point upper loop must take one more term than the
   pinned loop.

Each of the three nonzero differences allowed by items 2 and 3 occurs:
`verify.py` exhibits `lo_f = lo_p - δ`, `hi_f = hi_p + δ` and
`hi_f = hi_p - δ` at explicit rationals. So the two engines are not equal on
`[0, 1/2]`. Neither bound of the fixed-point engine is uniformly wider than
the pinned one: its upper bound can be strictly tighter.

At `y = 0` both engines return `(1, 1)`. Assume `y > 0` below.

## Two facts

**Fact 1.** `t_k <= 1`, and for `k >= 1`, `t_(k+1) / t_k = y/(k+1) <= 1/4`.
Hence `t_(k+1) + t_(k+2) + ... <= (4/3) t_(k+1)` for `k >= 1`, and for every
`k >= 0`

```text
exp(y) - s_k = Σ_(j>k) t_j <= t_(k+1) / (1 - y/(k+2)) <= 2 t_(k+1) = 2 t_k y/(k+1),
```

so `s_k <= exp(y) <= V_k`. Also `V_(k+1) - V_k = t_(k+1)(2y/(k+2) - 1) <= 0`,
so `V_k` is nonincreasing in `k`.

**Fact 2.** `K <= 50`. Indeed `t_50 y <= 2^-51 / 50!` and `50! > 2^214`.

## Lemma 1: lower soundness and order

By induction `0 <= τ_j <= t_j`, because `γ <= y` and the floor only lowers.
Thus `S <= s_J <= exp(y)` and `lo_f <= exp(y)`. At `j = K`,
`τ_K γ <= t_K y < θ`, so the fixed-point loop has stopped by then: `J <= K`.
Hence `S <= s_J <= s_K` and `lo_f <= lo_p`.

## Lemma 2: lower gap

Let `e_j = t_j - τ_j >= 0`. Since `γ > y - 1/u` and a floor loses less
than `1/u`,

```text
τ_j > (t_(j-1) - e_(j-1)) (y - 1/u) / j - 1/u,
e_j < e_(j-1) y/j + t_(j-1)/(j u) + 1/u <= e_(j-1)/2 + 2/u,
```

so `e_j < 4/u` for all `j`, and `s_J - S < 4J/u <= 200/u`.

If `J = K`, then `s_K - S < 200/u`. Otherwise `J < K`. If `γ = 0`, then
`y < 1/u`, `t_1 y = y^2 < θ` and `K = 1 <= J`, a contradiction. So the loop
stopped because `τ_J γ < θ`, and

```text
t_J y = τ_J γ + τ_J (y - γ) + e_J y < θ + 1/u + 2/u.
```

By Fact 1, `s_K - s_J <= (4/3) t_J y/(J+1) <= (2/3)(θ + 3/u)`. In both cases
`s_K - S < (2/3)θ + 202/u < δ`. Then `lo_p - δ <= s_K - δ < S`, and
`lo_p - δ` is a multiple of `δ`, so `lo_f = down(S) >= lo_p - δ`. Lemma 1
gives `lo_f <= lo_p`, which proves item 2.

## Lemma 3: upper soundness and order

By induction `τ'_j >= t_j`, because `γ' >= y` and the ceiling only raises.
Since `γ' > 0`, the fixed-point loop does not stop at any `j < K`: there
`τ'_j γ' >= t_j y >= θ`. So `J' >= K`. Also
`ρ >= 2 τ'_(J') γ'/(J'+1) >= 2 t_(J') y/(J'+1)`, hence

```text
S' + ρ >= s_(J') + 2 t_(J') y/(J'+1) = V_(J') >= exp(y)
```

by Fact 1. So `hi_f >= exp(y)`, which with Lemma 1 proves item 1.

## Lemma 4: upper comparison

Let `e'_j = τ'_j - t_j >= 0`. With `γ' < y + 1/u <= 0.6` and a ceiling
adding less than `1/u`,

```text
e'_j < e'_(j-1) (y + 1/u) + t_(j-1)/(j u) + 1/u <= 0.6 e'_(j-1) + 2/u,
```

so `e'_j < 5/u`. At `j = K + 1`, using `y/(K+2) <= 1/6`,

```text
τ'_(K+1) γ' < (t_(K+1) + 5/u)(y + 1/u) <= t_K y · y/(K+2) + 7/u < θ/6 + 7/u < θ,
```

so `J' <= K + 1`, and with Lemma 3 `J'` is `K` or `K + 1`. The excess of the
fixed-point upper value over `V_(J')` is

```text
S' + ρ - V_(J') < 5 J'/u + 2 (5/u)(0.6)/(J'+1) + 2 t_(J')/(u (J'+1)) + 1/u < 270/u,
```

using `J' <= 51`. Fact 1 gives `V_(J') <= V_K`, so `S' + ρ < V_K + δ` and
`hi_f <= hi_p + δ`.

For the other direction, `S' + ρ >= V_(J')`. If `J' = K`, this is `V_K`, so
`hi_f >= hi_p`. If `J' = K + 1`, then
`V_K - V_(K+1) = t_(K+1)(1 - 2y/(K+2)) <= t_(K+1) < θ/6 < δ`, so
`S' + ρ > V_K - δ` and `hi_f >= hi_p - δ`. This proves item 3, including
the statement that `hi_f = hi_p - δ` needs `J' = K + 1`.

## Witnesses

Each witness is a dyadic rational `y = n / 2^e` in `(0, 1/2]`, listed in
`verify.py` with its full numerator:

| Name | `e` | `y` ≈ | `K` | `J` | `J'` | `lo_f - lo_p` | `hi_f - hi_p` |
|---|---:|---|---:|---:|---:|---:|---:|
| `lower_below` | 417 | 1/3 + 5.8e-78 | 46 | 46 | 46 | `-δ` | `0` |
| `upper_above` | 419 | 1/3 + 5.8e-78 | 46 | 46 | 46 | `0` | `+δ` |
| `upper_below` | 400 | 0.0303609 | 30 | 30 | 31 | `0` | `-δ` |

The first two place `s_K` just above a multiple of `δ` and `V_K` just below
one, so the fixed-point rounding loss or gain crosses that grid point. The
third places `t_30 y` just below `θ` (so the pinned loop stops at `K = 30`,
while the rounded-up product keeps the fixed-point upper loop going). It also
places `V_30` just above a multiple of `δ`, so the one-term improvement
`V_30 - V_31 ≈ t_31` crosses it. The witnesses were found by exact bisection;
the verifier only checks them.

## Scope

The theorem compares two fixed programs at `P = 256` on rational arguments in
`[0, 1/2]`. It does not change either engine, the ceiling search, its
published bracket or κ. It does not decide whether the selected ceiling
search ever visits an argument where the engines differ beyond the screen
that #3662 already compared.
