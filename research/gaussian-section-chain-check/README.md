# One check of jwr404's p = 19 section chain, with the sharp two-power threshold

**Claim type: an independent certified finite check of one section. No new
κ.** It covers 33 open PRs in one package, and adds the exact threshold that
their two-power steps approach.

## Object

The section is the one from #4319 and my
[#4336](https://github.com/CrocSwap/integer-mult-bounds/pull/4336): `p = 19`,
`β₀ = −1/2`, bandwidth 2, `t_i = i`. The interiors `3..6` are eliminated, and
the survivors `0, 1, 2, 7, 8, 9` are row-normalized to `H`.

jwr404's chain then applies `HALO.md`'s polynomial inverse
`P = p⁻²⁰ Σ_{j<J} Q^j H*`, with `Q = I − p⁻²⁰H*H` and `J = ⌈p⁴²⌉`, and
bounds its error.

| PR | Claim |
| --- | --- |
| #4354 | `281/100 < ‖H⁻¹‖₁ < 282/100` |
| #4355 | `‖H⁻¹‖₂ < 319/100` |
| #4361 | every absolute row and column sum of `H` is below `1226/625`, so `‖H‖₂ < 1226/625 < 2 < 19¹⁰` |
| #4362 | every eigenvalue of `Q` lies in `(0, 1 − p⁻⁴⁰)` |
| #4364 | `(1 − 19⁻⁴⁰)^(19⁴²) < e⁻³⁶¹`, so the error is below `(319/100)e⁻³⁶¹` |
| #4366–#4369, #4374, #4379–#4400 (27 PRs) | `(319/100)e⁻³⁶¹ < 2^(−19C)` for `C = 1..27` |
| #4401 | `(319/100)e⁻³⁶¹` is not below `2⁻⁵³²` |

## Results

Every claim holds, certified with exact rationals.

| Quantity | Value |
| --- | --- |
| `‖H⁻¹‖₁` | `2.8138216884…`, inside `(2.81, 2.82)` |
| `‖H⁻¹‖₂ ≤ √(‖·‖₁‖·‖_∞)` | `3.183009 < 3.19` |
| Largest row or column sum of `H` | `1.9615957574 < 1226/625 = 1.9616` |
| `‖H‖₂` | `≤ 1.961596` |
| `p⁻²⁰(1226/625)² < 1` and `p⁻²⁰(100/319)² > p⁻⁴⁰` | exact, so the spectrum of `Q` lies in `(0, 1 − p⁻⁴⁰)` |
| `19⁻⁴⁰ · 19⁴² = 361` | exact, so `(1 − x)^N < e^(−xN) = e⁻³⁶¹` |
| The 27 two-power claims and #4401's negative | all hold, from `e³⁶¹` enclosed to 60 digits |

**The sharp threshold.** `(319/100)e⁻³⁶¹ < 2^(−k)` holds exactly for
`k ≤ 519`, and fails at `k = 520`. The chain's step of 19 stops at 513 and
then fails at 532; the true boundary lies between them.

**Two tight spots.**

- The row and column sums of `H` clear `1226/625` by only `4.2·10⁻⁶`. The
  largest sum is `1 + e^(−9π/722)`, from the forward step at vertex 0.
- The round ceilings `2.82 · 3.61 = 10.1802` exceed `3.19² = 10.1761`.
  #4355's 2-norm bound therefore needs the certified norms, not the rounded
  ones, as its own README notes.

## Method and independence

Nothing is imported from jwr404's packages, and the method differs from
theirs:

- The entries come from `GAUGEFREE-INTERIORS.md`'s original form.
- `H⁻¹` comes from the quotient identity: the survivor block of `A⁻¹` times
  `diag(S)`.
- `H` is the exact inverse of that, with one perturbation bound.

The notes this reads are on main, pinned by SHA256 with phrase checks.

## Not covered

- Any other section, prime or bandwidth.
- `HALO.md`'s all-size claims.
- Whether `#4100`'s callers need more than the `2^(−C)` thresholds proved
  here.

## Reproduce

```sh
python3.12 -B research/gaussian-section-chain-check/verify.py
```

It prints `PASS_GAUSSIAN_SECTION_CHAIN_CHECK` in about 10 seconds, using only
the standard library.

## Open next questions

None from this check.

## Credit

The chain, its section and its thresholds are jwr's (#4354, #4355,
#4361–#4401). The kernel and lemmas are `#4100`'s `GAUSSIAN.md`, `HALO.md`,
`INVERSE-CONDITIONING.md` and the vendored `GAUGEFREE-INTERIORS.md`.
Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
