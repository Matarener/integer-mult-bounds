# Turning-point asymptotics of the broad forward inverse

**Claim type:** a formal (semiclassical) derivation of the leading constant, confirmed numerically to
better than 1%. **No new κ, and this is not a proof.** It answers open questions 1–2 of my
[#4408](https://github.com/CrocSwap/integer-mult-bounds/pull/4408). #4408 found that the phase-cell
blocks behind `FORWARD-SMALL-A-AUDIT.md`'s `O(α⁵ρ²θ⁻²e^{aρ/3})` actually grow like `θ^{−1/2}`. It asked
why, and how the constant depends on `α`. The answer is

    ‖K⁻¹‖₂ ≈ e^{a/4} / (2α√π) · θ^{−1/2},        a = πα².

## Derivation

The block is `K_{k,i} = α⁻¹G(i − s_k)`, with `G(y) = e^{−b₀y²}`, `b₀ = π/α²`,
`s_k = λk + c` and `θ′ = 1 − λ = θ/(1+θ)`.

1. **Alternating ansatz.** Try `x_i = (−1)^i u(i)` with `u` slowly varying. By Poisson summation,
   `Σ_i (−1)^i u(i)G(i − s)` is dominated by the frequencies `±π`. The next terms are smaller by
   `e^{−2π²/b₀}`. To first order in `u′` this gives

       Σ_i (−1)^i u(i) G(i−s) ≈ 2g₀ [cos(πs) u(s) − (π/2b₀) sin(πs) u′(s)],   g₀ = √(π/b₀)·e^{−π²/(4b₀)}.

2. **The turning point.** Write `s_k = k + (c − θ′k)`. Then `cos(πs_k) = (−1)^k cos(π(c − θ′k))`.
   This vanishes where `c − θ′k ≡ 1/2`, which is exactly where `β′ = ±1/2`: the zero of the shifted
   Gaussian symbol, at a phase-cell edge. With `y` the distance from that point,

       (Kx)_k ≈ (−1)^k · T u,     T = A[(πθ′) y − (π/2b₀) ∂_y],     A = 2g₀/α.

3. **The harmonic oscillator.** Write `T = A(π/2b₀)(κy − ∂_y)` with `κ = 2b₀θ′`. Then
   `T*T = A²(π/2b₀)²(−∂² + κ²y² + κ)`. Its lowest eigenvalue is `A²(π/2b₀)²·2κ`, because the
   harmonic oscillator `−∂² + κ²y²` has ground energy `κ`. So
   `σ_min = Aπ√(θ′/b₀)`. Substituting `A` and `b₀ = π/α²` gives the formula above.

The minimizing vector is the oscillator's Gaussian ground state, of width `(2b₀θ′)^{−1/2}`,
alternating in sign and sitting at the cell edge. In the actual block the turning point lies on the
block's boundary. The numerics match the full-line constant, which means the truncated matrix acts like
a Neumann boundary there. That is observed, not derived.

## Numerical confirmation

`verify.py` computes `‖K⁻¹‖₂` by inverse power iteration with sparse LU. It uses the banded block,
dropping entries below `e^{−78}`, on a window of `min(1/θ, 60θ^{−1/2})` coordinates starting at
`β′ = −1/2`:

| `1/θ` | `α = 3`: ratio to `110.4385·θ^{−1/2}` | `α = 4`: ratio to `20222.76·θ^{−1/2}` |
| --- | --- | --- |
| 400 | 0.97357 | 0.94626 |
| 1,600 | 0.98198 | 0.96333 |
| 6,400 | 0.98981 | 0.97929 |
| 25,600 | 0.99461 | 0.98905 |
| 102,400 | **0.99723** | **0.99438** |

The ratio tends to 1, and the gap `1 − ratio` roughly halves each time `θ` is quartered, as an
`O(θ^{1/2})` correction should. The verifier also checks two controls:

- a dense SVD over the whole cell agrees with the sparse iteration at `θ = 1/400`;
- halving the window at `θ = 1/102400` changes the value by less than `10⁻⁶` relative, so the
  conditioning is localized at the turning point.

## Consequence

At the fine-prime `θ = 1/(4p²)`, with `a ≈ 4 log(16p)`, the true conditioning is

    e^{a/4}/(2α√π) · 2p ≈ 16p²/(α√π)   (with e^{a/4} ≈ 16p),

which is `O(p²/√log p)`. The audit's ceiling is `16p⁴·α⁵·e^{aρ/3}`. At `p = 19` the prediction is
`110.44 · 38 = 4197`, which is close to #4408's measured 4118, against a ceiling of `9.1·10⁹`. The
loss in the ceiling comes from two places: the exponent `a/3` in place of `a/4`, and the reciprocal
gap `θ⁻²` in place of `θ^{−1/2}`.

## Not covered

- **A rigorous upper bound.** A proof would need coercivity away from the turning point, plus
  control of the boundary layer.
- **The narrow kernel.** For that, see #4402's column gap.
- **Any change to #4100's guards.** The ceiling already sits inside the `p¹⁰` envelope.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/forward-turning-point --check-only
python3.12 -B scripts/research_package.py --package research/forward-turning-point
```

The verifier prints `PASS_FORWARD_TURNING_POINT` in about 3 seconds. It needs `numpy` and `scipy`.

## Open next questions

1. **Can the reduction be made rigorous?**
   - *Why it matters:* it would give `‖K⁻¹‖₂ ≤ (1 + o(1))·e^{a/4}/(2α√π)·θ^{−1/2}`.
   - *First step:* a Grushin-type reduction near the turning point, plus the accretive symbol bound
     of `GAUGEFREE-INTERIORS.md` §3 away from it.

## Credit

- The bound is from `FORWARD-SMALL-A-AUDIT.md` (PR1673 lineage). The shifted-symbol picture is from
  `GAUGEFREE-INTERIORS.md`.
- The `θ^{−1/2}` observation is my #4408, which answered Matarener's #4356.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
