# Broad forward conditioning at the fine-prime θ

**Claim type:** a written re-derivation of one θ-dependence, plus rigorous floating-point bounds
on the actual phase-cell blocks at five primes. **No new κ.** It answers the open question of
Matarener's [#4356](https://github.com/CrocSwap/integer-mult-bounds/pull/4356): does
`FINE-PRIME.md` §2's conditioning bound stay polynomial at `θ = 1/(4p²)`?

## Object

`vendor/FINE-PRIME.md` reuses `FORWARD-SMALL-A-AUDIT.md` §1–2 at the smaller fine-prime θ:

    ‖K⁻¹‖ ≤ α e^{3b/4} c_b^{-4} / (1 − e^{−bρθ})² = O(α⁵ ρ² θ⁻² e^{aρ/3}).

Here `b = π/(α²ρ²)` and `c_b = Π(1 − e^{−2bρm})`. The blocks are
`K_{k,i} = α⁻¹ exp(−b₀(i − λk − c)²)`, on a contiguous interval of one phase cell with
`β'_k ∈ [−1/2, 1/2)`.

## Re-derivation of the θ-dependence

θ enters only through the reciprocal gap `1/(1 − e^{−bρθ})`. Since
`x = bρθ = πθ/(α²ρ) < 1` and `1 − e^{−x} ≥ x/2` on `[0, 1]`, that gap is at most
`2α²ρ/(πθ)`. The other factors do not involve θ:

- `e^{3b/4} ≤ e^{3π/(4α²)}`;
- `c_b^{-4} ≤ e^{aρ/3}`, by §1's logarithmic series bound.

So the bound is

    ‖K⁻¹‖ ≤ (4/π²) α⁵ ρ² e^{3π/(4α²)} e^{aρ/3} θ⁻²,

valid for every θ in `(0, 1]`. At `θ = 1/(4p²)`, `θ⁻² = 16p⁴`. With `a ≤ 5 log(16p)`, the
factor `e^{aρ/3}` is at most `(16p)^{5ρ/3}`, so the whole bound is polynomial in `p`. This is
`FINE-PRIME.md`'s claim, and the answer to #4356's question is **yes**. The argument does not
re-audit `BILATERAL-LDU.md`'s base inequality, whose θ-dependence §1 says is unchanged.

## Measured norms

`verify.py` builds the blocks at `p = 5, 7, 11, 13, 19`, with `α = 3` from the formula at all
five. It covers three starting phases, `β'₀ ∈ {−1/2, −1/4, 0}`, and every dyadic length up to the
whole remaining cell.

For `‖K⁻¹‖_∞` and `‖K⁻¹‖₁` it gives rigorous upper bounds from float64 residuals. Those bounds
use the standard `γ_{n+2}` rounding bound and fold in the error of each computed entry. The
2-norm is a plain float value.

| `p` | θ | ceiling | `‖K⁻¹‖_∞ ≤` | `‖K⁻¹‖₁ ≤` | `‖K⁻¹‖₂` | ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 1/100 | 4.78e7 | 1505.9 | 1265.2 | 1092.8 | 3.2e-5 |
| 7 | 1/196 | 1.76e8 | 2192.7 | 1702.4 | 1506.8 | 1.3e-5 |
| 11 | 1/484 | 1.04e9 | 3643.3 | 2625.0 | 2367.4 | 3.5e-6 |
| 13 | 1/676 | 2.02e9 | 4385.7 | 3094.1 | 2803.1 | 2.2e-6 |
| 19 | 1/1444 | 9.14e9 | 6634.2 | 4513.2 | 4118.2 | 7.3e-7 |

The ratio column is the larger rigorous norm divided by the ceiling. Every block is below its
ceiling, and the worst block is always the longest one.

**Scaling.** At fixed `α = 3`, with a whole cell starting at `β' = −1/2`, `‖K⁻¹‖₂·√θ` stays
between 107.5 and 109.3 for θ from 1/100 to 1/3200. The verifier enforces that this ratio varies
by less than 5%. So on these blocks the true dependence is about `θ^{−1/2}`, not `θ⁻²`. At the
fine-prime θ this means `O(p)` rather than `O(p⁴)`.

This is an observation at `α = 3` only, not a proof. A plausible mechanism is a single turning
point, where the local shift passes the symbol's zero at `|s| = 1/2`. That would give the
`θ^{−1/2}` of an Airy-type layer.

## Not covered

- `BILATERAL-LDU.md`'s base inequality.
- Values of `α ≥ 4`, which first occur at `p ≥ 74`, where a cell has more than 21,000
  coordinates.
- The narrow kernel. For that, see #4402's column gap.
- Any change to #4100's guards. `FINE-PRIME.md`'s `p¹⁰` envelope already absorbs the ceiling.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/forward-fine-theta-conditioning --check-only
python3.12 -B scripts/research_package.py --package research/forward-fine-theta-conditioning
```

The verifier prints `PASS_FORWARD_FINE_THETA_CONDITIONING` in about 20 seconds. It needs
`numpy`.

## Open next questions

1. **Can `‖K⁻¹‖ = O_α(θ^{−1/2})` be proved?**
   - *Why it matters:* it would replace `θ⁻²` by `θ^{−1/2}` in `FORWARD-SMALL-A-AUDIT.md`, which
     saves about `p³` at the fine-prime θ.
   - *First step:* bound the inverse of a Gaussian Toeplitz operator whose shift varies linearly
     through `1/2`. A turning-point (WKB) estimate is the natural route.
   - *Blocked by:* nothing.
2. **Does the constant in `θ^{−1/2}` grow like `e^{aρ/3}` in `α`?**
   - *First step:* repeat the scaling table at `α = 4` and `α = 5` on shortened cells.

## Credit

- The bound is from `FORWARD-SMALL-A-AUDIT.md`, PR1673 (Vlado Vojdanovski's capped-phase
  papers).
- Its fine-prime reuse is #4100's `vendor/FINE-PRIME.md` (Cinna Davis).
- Matarener's #4356 posed the question.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
