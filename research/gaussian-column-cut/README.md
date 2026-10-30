# The ideal column bound survives a g=2 step

**Claim type:** a written lemma for the ideal narrow matrix `N`. **No new κ.**
This answers the ideal-matrix half of open question 1 in
[#4402](https://github.com/CrocSwap/integer-mult-bounds/pull/4402). It does not
bound the rounded reference `H`, and it does not edit the #4100 notes.

#4402 proved, inside one constant-phase run,

```text
||N-I||_1 <= exp(-2aθ) + exp(-2a(1-θ)) + 2 exp(-2a)/(1-exp(-4a)).
```

Its own control shows the run identity `β_{i+h} = β_i + θh` fails across a cut.
The same majorant nevertheless holds for every column once each step is only
`g ∈ {1, 2}`.

## Question

`LOG-A-PHASE-SCHUR-AUDIT.md` defines

```text
n_{i,h} = exp(-a[(ρh + β_i)^2 - β_{i+h}^2]),    ρ = 1+θ,    β_i = ρ i - q_i,
```

with diagonal 1, each `β_i ∈ [-1/2, 1/2)`, and each step `g_i = q_i - q_{i-1}`
in `{1, 2}`. A cut in this model is a step `g = 2`, not a separate entry law.
Does #4402's column majorant still bound a column that meets such a step?

## Lemma

Under that entry law, every column satisfies

```text
||N-I||_1 <= exp(-2aθ) + exp(-2a(1-θ)) + 2 exp(-2a)/(1-exp(-4a)).
```

The nearest sum is largest on a both-steps-1 column. A `g = 2` step makes the
nearest contribution smaller. Assume in addition that `p >= 2` is an integer,
`θ ∈ [1/(4p^2), 1/p^2]` and `4 log(16p) <= a <= 5 log(16p)`, where `log` is the
inverse of `exp` as in `GAUSSIAN.md`. Then the column gap is strictly larger
than `1/(8p^2)`. Zeroing positive off-diagonal entries, including a truncation
at bandwidth `< p`, does not increase the off-sum. An entrywise change of size
`ε` on the at most `2p-1` nonzeros keeps the gap above `1/(16p^2)` whenever
`2p ε <= 1/(16p^2)`.

These `a` and `θ` inequalities are hypotheses. The note's statement that they
hold eventually is not re-proved. The historical rounding budget is not
identified with this `ε`.

## Proof

The recurrence is `β_j = β_{j-1} + 1 + θ - g_j`. Substitute it into the two
nearest formulas from the audit:

```text
n_{j-1,+1} = exp(-a g_j (g_j + 2 β_j)),
n_{j+1,-1} = exp(-a g_{j+1} (g_{j+1} - 2 β_j)).
```

Since `θ <= 1/4 < 1/2`, the landing intervals are disjoint:

| Incoming `g_j` | Outgoing `g_{j+1}` | `β_j` |
| --- | --- | --- |
| 2 | 1 | `[-1/2, -1/2+θ)` |
| 1 | 1 | `[-1/2+θ, 1/2-θ)` |
| 1 | 2 | `[1/2-θ, 1/2)` |

On the middle interval write `t = 2|β|`. Then `t <= 1-2θ`, and the sum is
`exp(-a(1+t)) + exp(-a(1-t))`. For `0 <= t < m`,

```text
(e^{at} + e^{-at}) - (e^{am} + e^{-am})
    = (e^{at} - e^{am}) (1 - e^{-a(t+m)}) < 0,
```

so the sum increases with `t`. Its maximum is the endpoint `m = 1-2θ`, where
the two factors are `2θ` and `2-2θ`:

```text
exp(-2aθ) + exp(-2a(1-θ)).
```

On the incoming `g = 2` interval write `β = -1/2 + u` with `0 <= u < θ`. The
two factors become `2(1+2u)` and `2(1-u)`. Since `u >= 0` and `θ < 1`,
`1+2u > θ`, and since `u <= θ`, `1-u >= 1-θ`. Each term is therefore at most
the matching term of the middle endpoint, and the first is strictly smaller.
The outgoing `g = 2` interval `β = 1/2 - u` produces the same two factors.

For a positive offset `h`, the same recurrence gives `ρh + β_{j-h} = β_j + s`
with `s = q_j - q_{j-h} >= h`. The square difference is `s(s + 2 β_j)`. Because
`β_j >= -1/2` and `s >= h >= 1`,

```text
s(s + 2 β_j) >= s(s-1) >= h(h-1).
```

The negative offset is `s(s - 2 β_j)` with the column index's `β`, and
`β_j < 1/2` gives the same lower bound. Thus every `|h| = k >= 2` entry is at
most `exp(-a k(k-1))`. For `k >= 2`,

```text
k(k-1) - (4k - 6) = (k-2)(k-3) >= 0,
```

so `exp(-a k(k-1)) <= exp(-2a) exp(-4a(k-2))`. One direction sums to at most
`exp(-2a)/(1-exp(-4a))`, and both directions to twice that. This is the tail
in #4402. It no longer needs `β_{i+h} = β_i + θh`.

The pure-run exponent is not equal to the cut exponent. At `h = 1`, `s = 2`
and `β = 0` the cut exponent is 4 and the pure-run exponent is 1. The cut
entry is the smaller one. #4402's equality control remains in force.

## The gap for every integer p >= 2

Let `x = 2 log(16p) / p^2` and `U = (16p)^{-8}`. The hypotheses give
`2aθ >= x`, `2aθ <= 5x` and `exp(-2a) <= U`, so

```text
exp(-2a(1-θ)) <= U exp(5x),    4 exp(-2a) <= 4U.
```

Also `exp(-4a) <= U^2`. For `U^2 <= 1/2` the sharp tail is at most `4U`. At
`p = 2`, `U = 2^{-40}`, so this holds for every integer `p >= 2`. Therefore

```text
off-sum <= exp(-x) + U (4 + exp(5x)).
```

Now `(16p)^4 <= 32^{p^2}`. Equality holds at `p = 2`. For `p >= 2`,
`(p+1)/p <= 3/2` and `32^{2p+1} = 32^5 · 32^{2(p-2)}`, while
`(3/2)^4 = 81/16 < 32^5`. The inequality is therefore strict for `p >= 3`, and
`x <= log(32)/2`. Hence `exp(5x) <= 4096 √2`. Since `17^2 = 289 > 288 = 2·12^2`,
`√2 < 17/12` and `4096 √2 < 17408/3`. The added 4 gives

```text
4 + exp(5x) < 17420/3,    off-sum < exp(-x) + (17420/3) U.
```

The series `1 + 1 + 1/2 + 1/6 = 8/3` and the positive next term give `e > 8/3`.
Then `(8/3)^4 - (8/3)^2 - 1 = 3439/81 > 0`. The derivative `4x^3 - 2x` is
positive for `x > 1`, so `e^4 - e^2 - 1 > 0`, which is `exp(-4) + exp(-2) < 1`.
In particular `exp(-2) < 9/64 < 1/2`. Also `1/k! <= 1/2^{k-1}` for `k >= 1`,
strictly at `k = 3`, so `e < 3 < 32` and `log(32) > 1`. Thus `x > 2/p^2`.

From `e^y > 1 + y` for `y > 0`, `1 - exp(-x) > x/(1+x)`. The function
`t/(1+t)` is increasing, so `x/(1+x) > 2/(p^2+2)`. The slack is

```text
2/(p^2+2) - 1/(8p^2) = (15p^2 - 2) / (8p^2 (p^2+2)).
```

For `p >= 2`, `p^2 + 2 <= 2p^2`, and the denominator is at most `16p^4`. The
polynomial

```text
(15(p+1)^2 - 2)(p+1)^4 - (15p^2 - 2)p^4
    = 90p^5 + 225p^4 + 292p^3 + 213p^2 + 82p + 13
```

has positive coefficients. Combined with the integer comparison
`17420 · 16 · 2^4 = 4459520 <= 3(15·4 - 2)(32)^8`, this yields

```text
(17420/3) U <= (15p^2 - 2)/(16p^4)
```

for every integer `p >= 2`. The column gap is therefore strictly above
`1/(8p^2)`.

## Truncation and a sufficient rounding budget

Every off-diagonal entry is positive. Setting any of them to zero, including
every `|h| > W`, does not increase the off-sum. A positive diagonal alias is
not part of that off-sum; deleting it moves the diagonal toward the audit's
diagonal value 1. After those deletions the gap is still above `1/(8p^2)`.

`GAUSSIAN.md` has bandwidth `< p`, so a column has at most `2(p-1)+1 = 2p-1`
nonzeros. If each changes by at most `ε` and `2p ε <= 1/(16p^2)`, the diagonal
falls by at most `ε` and the off-sum rises by at most `(2p-2)ε`. The gap loss
is strictly less than `1/(16p^2)`, and the gap stays above

```text
1/(8p^2) - 1/(16p^2) = 1/(16p^2).
```

This is a sufficient budget. It is not a reading of the written precision, and
it is not `LOG-A`'s older `||H-N|| < 1/(16p)` estimate.

## Not covered

- Column sums of `A = diag(ahat) Ghat diag(ahat)^{-1}`. The audit gives
  `log(a_i/a_j) = a(i-j)(β_i+β_j)` inside one cell. Conjugation by a
  non-constant diagonal does not preserve column sums. Across cells the rounded
  matrix uses the downward dyadic entries, which are not `n_{i,h}`.
- A step `g >= 3`. The audit assumes every step is in `{1, 2}`.
- `||N^{-1}||_1`. #4402 already turns a column gap of this shape into
  `1/δ_col` inside a run. This package does not replay that inverse step and
  does not claim it for `H`.
- The exponent replacements in #4406. They still wait on the rounded matrix.
- Any new κ. The selected record remains `23/10000`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-column-cut --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-column-cut
```

The verifier is integer arithmetic only. Base `2a13eb1827784206202db90e5dc8327cf8a250db`,
priority revision 7, selection refresh κ = `23/10000`.

Overlap on 2026-10-21, including open PRs and discussion #1166: #4402 is the
predecessor and stops at a constant-phase run. #4403 and #4406 treat the
`p^10` guards and the conditional halo exponents. #4435 is the broad-forward
turning-point asymptotic. No searched item states this `g ∈ {1, 2}` column
majorant. A search miss is not a novelty certificate.

## Open next questions

1. **What is the column off-sum of the rounded within-cell matrix?**
   The callers invert `H`, whose within-cell block is
   `diag(ahat) Ghat diag(ahat)^{-1}`. The ideal bound does not transfer through
   that diagonal. The first step is to bound one column of
   `Ghat_{j-k} ahat_j / ahat_k` on a single cell, using the pinned log-ratio
   `a(i-j)(β_i+β_j)`, and then the downward entries used across a cell. The
   blocker is that ratio: it changes column sums, and the across-cell rule is
   not the ideal entry `n_{i,h}`.

## Credit

- The entry law and the row estimate are PR1673's, as quoted by #4100's
  `LOG-A-PHASE-SCHUR-AUDIT.md` and `GAUSSIAN.md`.
- The in-run column majorant, and the question this package continues, are
  Ryanson Jonathan's #4402.
- The gauge formula is the capped-gauge audit's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
