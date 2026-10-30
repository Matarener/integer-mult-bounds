# Inverse 1-norm of #4319's normalized Gaussian Schur section

**Claim type: a certified finite computation on one section. No new κ.** It
answers the open question of
[PR #4319](https://github.com/CrocSwap/integer-mult-bounds/pull/4319) and
rechecks that PR's infinity-norm bracket by a different route. It is not an
all-size inverse bound.

## Object

The section is the one #4319 uses: `p = 19`, `β₀ = −1/2`, bandwidth 2 and
`t_i = i` on the path `0..9`. The interiors `3..6` are eliminated. The
survivors are `0, 1, 2, 7, 8, 9`, and each Schur row is divided by its
diagonal, giving `N`.

#4319 proved `18/5 < ‖N⁻¹‖_∞ < 361/100` and left one question open: "Nothing
here sums the absolute values down the columns of the inverse." The 1-norm
matters because `INVERSE-CONDITIONING.md` bounds the 2-norm by
`√(‖·‖₁ ‖·‖_∞)`. Its 1-norm ceiling `1/δ + 2bρ/δ²` is the large one. At the
tight gap of #4317 it is 3938.

## Results

Every value is certified with exact rationals, to within `7·10⁻⁸⁷`.

| Norm of `N⁻¹` | Value | Ceiling (#4317) |
| --- | --- | --- |
| infinity, attained at row `0` | `3.600635404331…` | 27 |
| 1, attained at column `2` | `2.813821688397…` | 3938 |
| 2 | between `1.6265` and `3.1830` | 321 |

- **The 1-norm is below the infinity norm.** The bandwidth term
  `2bρ/δ²` is what makes the lemma's 1-norm ceiling about 1400 times the
  true value on this section.
- **The same holds on the full path.** The unsectioned 10-vertex matrix has
  `‖A⁻¹‖₁ = 4.3868…` and `‖A⁻¹‖_∞ = 6.0623…`.
- **#4319's bracket holds.** `18/5 < 3.6006354… < 361/100`.
- **2-norm bounds.** The upper bound is `√(‖·‖₁ ‖·‖_∞)`. The lower bound is
  the largest column Euclidean norm.

**Control.** The principal restriction `A_KK` drops the interior
elimination, and with it the filled entry from vertex 2 to vertex 7. Its
inverse has infinity norm below 3, so it misses #4319's bracket. The bracket
therefore depends on the Schur complement.

## Method and independence

The verifier imports nothing from #4319 and differs from it in three ways.

1. **Entries.** It builds each entry from `GAUGEFREE-INTERIORS.md`'s original
   form, `N_{i,i+h} = exp(−a[(ρh + β_i)² − β_{i+h}²])`, rather than the gauge
   form. It also checks exactly that the two forms agree.
2. **No Schur complement.** By the quotient identity, `S⁻¹` is the survivor
   block of `A⁻¹`, so `N⁻¹ = (A⁻¹)_KK · diag(S)`. The diagonal of `S` comes
   from inverting that block.
3. **Error control.** It inverts the rational midpoint exactly. One
   perturbation bound, `‖X̂‖²‖Δ‖/(1 − ‖X̂‖‖Δ‖)`, then covers the entry radii,
   in place of interval elimination.

Its enclosures are also its own:

- π from Machin's formula with alternating-series bounds;
- `exp` by halving, then Taylor with a remainder, then squaring with outward
  rounding;
- entries snapped outward to `10⁻⁹⁰`.

It confirms `α = 3`, that is `π < log 304 ≤ 9π/4`.

## Not covered

- Any other section, prime or bandwidth, and the all-size row-gap claim of
  `GAUSSIAN.md`.
- Whether `#4100` needs the 2-norm on this section or only the lemma's
  ceiling at its callers.

## Reproduce

```sh
python3.12 -B research/gaussian-section-inverse-norms/verify.py
```

It prints `PASS_GAUSSIAN_SECTION_INVERSE_NORMS` in about 6 seconds, using only
the standard library. The three notes it reads are on main and pinned by
SHA256 in [SOURCES.json](SOURCES.json), with phrase checks.

## Open next questions

1. **Does the 1-norm stay below the infinity norm on longer paths and
   sections?**
   - *Why it matters:* if it does, the lemma's 1-norm ceiling is loose
     uniformly, and the 2-norm bound could drop from `√(1/δ · 2bρ/δ²)` to
     about `1/δ`.
   - *First step:* run the same quotient-identity computation for path
     lengths 11 to 40.
   - *Blocked by:* nothing; a proof would need a column analogue of the row
     gap.

## Credit

The section, the bracket and the open question are jwr's (#4319 and the
#4305–#4318 chain). The kernel and the conditioning lemma are in `#4100`'s
`GAUSSIAN.md`, `INVERSE-CONDITIONING.md` and the vendored
`GAUGEFREE-INTERIORS.md`. Prepared by Ryanson Jonathan with substantial
Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
