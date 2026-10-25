# A column gap for the narrow Gaussian kernel

**Claim type:** a written lemma for one constant-phase run, plus a certified finite table at
`p = 19`. **No new κ.** This is not the full transfer to `GAUSSIAN.md`'s global rounded
reference `H`: cut entries, truncation and rounding are listed below as not covered.

It answers open question 1 of
[#4336](https://github.com/CrocSwap/integer-mult-bounds/pull/4336), which asked whether the inverse
1-norm stays below the infinity norm on longer paths. That PR noted that a proof needs a column
analogue of the row gap. This package supplies one.

## Why it matters

`INVERSE-CONDITIONING.md` has only a row gap `δ`. It bounds the 1-norm through the bandwidth:
`‖H⁻¹‖₁ ≤ 1/δ + 2bρ/δ²`, and then the 2-norm by `√(‖·‖₁‖·‖_∞)`. `GAUSSIAN.md` deliberately
"does not assume that a row norm bounds a column norm". For the narrow kernel, a column gap
`δ_col` gives `‖H⁻¹‖₁ ≤ 1/δ_col` directly, by the same Neumann argument applied to `‖E‖₁`. The
2-norm bound then improves to `1/√(δ δ_col)`. Under `GAUSSIAN.md`'s `b < p` and
`δ ≥ 1/(16p²)`, the bandwidth factor removed is at most about `√32 · p^1.5`.

## Lemma (one constant-phase run)

**Setting.** `GAUGEFREE-INTERIORS.md` §1 defines
`N_{i,i+h} = exp(−a[(ρh + β_i)² − β_{i+h}²])`, where `ρ = 1 + θ` and `β_{i+h} = β_i + θh`
inside a phase cell, with every `β ∈ [−1/2, 1/2)`.

**Column form.** Put `j = i + h`, so that `β_i = β_j − θh`. Then
`(ρh + β_j − θh)² − β_j² = (h + β_j)² − β_j² = h² + 2β_j h`. Hence
`N_{j−h, j} = exp(−a(h² + 2β_j h))`: column `j` depends only on `β_j`. The row form of Lemma 2.2,
`(1+2θ)h² + 2β_i h`, is the transposed statement.

**Bound.** Fix a column `j`. Its row `j − h` exists only if `β_j − θh ∈ [−1/2, 1/2)`.

- `h = 1` needs `β_j ≥ −1/2 + θ`, so `1 + 2β_j ≥ 2θ`.
- `h = −1` needs `β_j < 1/2 − θ`, so `1 − 2β_j > 2θ`.
- When both exist, the pair sums to `e^{−a}·2cosh(2aβ_j)`. This is convex in `β_j`, so on
  `[−1/2+θ, 1/2−θ]` it is at most `e^{−2aθ} + e^{−2a(1−θ)}`. When only one exists, it is at most
  `e^{−2aθ}`.
- For `|h| ≥ 2`, `|β_j| ≤ 1/2` gives `h² + 2β_j h ≥ |h|(|h| − 1)`. The tail is at most
  `2Σ_{k≥2} e^{−ak(k−1)} ≤ 2e^{−2a}/(1 − e^{−4a})`.

So every column of `E = I − N` satisfies

    ‖E‖₁ ≤ e^{−2aθ} + e^{−2a(1−θ)} + 2e^{−2a}/(1 − e^{−4a}) =: 1 − δ_col.

The row bound in `GAUSSIAN.md` is `e^{−2aθ} + 5e^{−2a}`. The leading term is the same, so
`δ_col` exceeds `1/(8p²)` eventually, as the row gap does.

**Consequences.**

- `‖N⁻¹‖₁ ≤ 1/δ_col`, from `Σ‖E‖₁^k`. No bandwidth term appears.
- A principal section keeps a subset of each column's entries, so it keeps the column gap.
- The unnormalized Schur inverse `S⁻¹` is a principal block of `N⁻¹`. Restriction does not
  increase the 1-norm, so `‖S⁻¹‖₁ ≤ 1/δ_col`.
- Truncating at a band `W` only removes entries.

The normalized section `diag(S)⁻¹S` multiplies inverse columns by `S_jj`. That step is covered
only by the finite table below.

## Certified table at `p = 19`

This uses #4319's parameters: `α = 3`, `θ = 1/(4p²)` and bandwidth 2. `verify.py` certifies
`δ_col ≥ 0.0384042426`, so `1/δ_col = 26.0388`. At the same gap, `INVERSE-CONDITIONING.md`'s
1-norm ceiling is 2633.96.

It covers 64 placements: every path length `n = 10..40` and `n = 100`, each at both ends of a
phase run. The start places `β₀ = −1/2`, as in #4319. The end places `β_{n−1} = 1/2 − θ`. Every
placement passes all of these:

- every entry satisfies the original, row and column forms exactly;
- every column sum lies within the lemma's bound;
- `‖A⁻¹‖₁ ≤ 1/δ_col`, with largest ratio `‖A⁻¹‖₁ δ_col = 0.1685`;
- `‖A⁻¹‖₁ < ‖A⁻¹‖_∞`, which answers #4336's question for these lengths;
- for the normalized 3+3 Schur section on `0, 1, 2, n−3, n−2, n−1`, the 1-norm is below the
  infinity norm, and the unnormalized `‖S⁻¹‖₁ ≤ 1/δ_col`.

| `n`, end | `‖A⁻¹‖_∞` | `‖A⁻¹‖₁` | section `‖·‖_∞` | section `‖·‖₁` |
| --- | --- | --- | --- | --- |
| 10, start | 6.062343 | 4.386837 | 3.600635 | 2.813822 |
| 40, start | 6.364412 | 4.386837 | 2.850751 | 2.813822 |
| 100, start | 6.364412 | 4.386837 | 2.850751 | 2.813822 |
| 40, end | 5.578656 | 4.000992 | 2.746838 | 2.711327 |
| 100, end | 5.578656 | 4.000992 | 2.746838 | 2.711327 |

The `n = 10` start row reproduces #4336's values. The 1-norm saturates at about 4.39, about 1/6
of `1/δ_col`. On these matrices the actual column gap equals the actual row gap.

**Method.** `π` and `exp` have their own rational enclosures, and entries are snapped outward to
`10⁻⁴⁰`. A float64 inverse of the midpoint is certified by the exact rational left and right
residuals: `‖A⁻¹ − X‖ ≤ r‖X‖/(1 − r)`, with entry radii folded into `r`. The 6×6 sections use an
exact inverse and a perturbation bound, as in #4336. The certified error is below `10⁻⁹`.

**Control.** Across a phase cut, `β_{i+h} = β_i + θh − 1` breaks the column form. The verifier
checks that, so the lemma's run hypothesis is load-bearing.

## Not covered

- **Cross-cut entries.** A global matrix spanning several phase runs has entries whose
  `β_{i+h}` wraps. Their column sums are not bounded here.
- **Truncation and rounding.** `GAUSSIAN.md` transfers its row gap to the truncated, rounded,
  hole-augmented `H`. The column-side transfer is plausible by the same argument, since a column
  has at most `2W + 1` entries, but it is not written here.
- **Other primes and bandwidths.** The table covers `p = 19`, bandwidth 2 only. The lemma itself
  is general within one run.
- **Callers.** Whether any #4100 guard changes, and any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-column-gap --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-column-gap
python3.12 -B research/gaussian-column-gap/verify.py
```

The last command prints `PASS_GAUSSIAN_COLUMN_GAP` in about 2.5 minutes, using only the standard
library.

## Open next questions

1. **Does the column gap survive phase cuts, truncation and rounding in `H`?**
   - *Why it matters:* only then does `‖H⁻¹‖₁ ≤ 1/δ_col` hold for the matrix the callers
     invert.
   - *First step:* write the cross-cut entries from the original form and bound their column
     sums. Then repeat `GAUSSIAN.md`'s truncation and rounding steps for columns.
   - *Blocked by:* the exact cross-cut definition in the PR1673/PR1758 sources.
2. **Does any caller's guard move?**
   - *Why it matters:* the 2-norm bound drops by a polynomial factor.
   - *First step:* list the callers of `INVERSE-CONDITIONING.md`'s 2-norm bound and the exponent
     each one uses.
   - *Blocked by:* nothing.

## Credit

- The kernel, the row form (Lemma 2.2) and the conditioning lemma are #4100's
  (`GAUGEFREE-INTERIORS.md`, `INVERSE-CONDITIONING.md`, `GAUSSIAN.md`), building on Vlado
  Vojdanovski's PR1673.
- The section and its parameters are jwr's (#4319 and its predecessor chain).
- #4336 posed the question.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
