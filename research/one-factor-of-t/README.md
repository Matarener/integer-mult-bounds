# One factor of `T` on #4100's coefficient error path

**Claim type:** a written ∞-norm error ledger, plus a fixed-point simulation of the normalized
synthetic convolution. **No new κ.** It answers open question 1 of unpaidmoon's
[#4371](https://github.com/CrocSwap/integer-mult-bounds/pull/4371): how many factors of `T` does one
coefficient pick up through `PROOF.md`'s three source transforms, the pointwise product and the
final `M` scale?

#4371 showed that the literal "full array dimension in all norm changes" reading costs
`2^{Θ(p²)}`, while one factor of `T` allows `C = 5` for `b ≥ 13` and `C = 8` for `b ≥ 2`.

## Ledger

Measure every error in the sup norm over coefficients. For stages `L_k` with
`‖L_k‖_∞ ≤ λ_k` and rounding `ρ_k`, the final error is at most `Σ_k ρ_k Π_{j>k} λ_j`. The point is
that no downstream product contains `T` more than once.

| Stage (`PROOF.md`) | `‖·‖_∞` on errors | Source of the bound |
| --- | --- | --- |
| CRT address map and the permutations `R`, `Q`, `P_s`, `P_t` | 1 | permutations |
| Chirp `a`, twist `y^k`, twiddles `y^E` | 1 | unimodular diagonals, plus truncation toward zero |
| Normalized butterflies `H0 = [[1,1],[1,−1]]/2` | 1 | row sums equal 1 |
| Ring products, divided by `r` | bounded | exact Kronecker packing on bounded data |
| Final `×M` inside one synthetic convolution | `M = T/r < 2^{p/6+2}` | `PROOF.md` |
| Completed normalized `S_gauss` and `D N⁻¹ C` | 1, times `2^γ` | dyadic normalization, with `γ = O(d log p) = o(p)` |

The `D N⁻¹ C` contraction rests on row sums: `‖N⁻¹‖_∞ ≤ 1/δ` (`INVERSE-CONDITIONING.md`) and
`D ≤ e^{a/4}`.

**The factor `M` touches only internal rounding.** As an exact map, the synthetic convolution
`w ↦ M·F_plus((F_minus a)(F_minus w)/r) = (a*w)/T` is a cyclic average of bounded data. It is an
∞-contraction, so errors already present in its inputs are **not** multiplied by `M`. Only rounding
made after its forward transforms is multiplied by `M`. That rounding is at most `c·ℓ·2^{−P}`,
because normalized levels average their errors.

**Count.** Each of the three transforms (two forward, one inverse) contains one synthetic
convolution, in the middle map `Q F_t`. Its internal error is at most about `M·ℓ·2^{−P}`, then
passes through contractions and `2^γ`. The pointwise product `U·V1` is bilinear on bounded data, so
it adds errors rather than multiplying them. The contributions therefore add:

    final error ≲ 3·2^{2γ}·M·poly(p)·2^{−P},

which gives **`m = 1`**. With `P = Cp` and `M < 2^{p/6+2}`, #4371's one-factor table applies:
`C = 5` for `b ≥ 13`, and `C = 8` for `b ≥ 2`.

## Simulation

`verify.py` simulates the scalar case `r = 1` (`M = T`) with `P = 40`-bit truncation toward zero,
on random inputs of modulus below 1/4, for `T = 2^4..2^14`:

- **Error bound.** The maximum error stays below `4·M·ℓ·2^{−P}`.
- **Ratio to `M·ℓ`.** `error/(M·ℓ·2^{−P})` falls from 0.68 to 0.34.
- **Ratio to `M²`.** `error/(M²·2^{−P})` falls from `1.7·10⁻¹` to `2.9·10⁻⁴`, so there is no second
  factor of `T`.
- **Inputs.** An exact-map input perturbation of sup size `η` moves the output by at most `η`.

## Not covered

- **The effective row gap after truncation and rounding** (#4217). Until it holds, the
  `D N⁻¹ C` row is conditional on it, as #4371 notes.
- **The internal rounding of `GAUSSIAN.md`'s circuits.** This ledger uses its claim that they are
  contractions up to `2^γ`.
- **The ℓ² reading.** If a stage were only an ℓ²-contraction, each ℓ∞→ℓ² change would cost up to
  `√T`. The ∞-norm row-sum bounds avoid any change of norm.
- **The final scaling** `S²·2^{2b+4}`. It is part of exact recovery, which `PROOF.md` budgets
  separately.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/one-factor-of-t --check-only
python3.12 -B scripts/research_package.py --package research/one-factor-of-t
```

The verifier prints `PASS_ONE_FACTOR_OF_T` in about one second. It needs `numpy`.

## Open next questions

1. **Are `GAUSSIAN.md`'s completed circuit stages ∞-contractions with only `2^γ` growth, once
   their internal rounding is included?**
   - *Why it matters:* this is the remaining assumption in the ledger.
   - *First step:* bound one shifted-interior circuit's prefix factors in the ∞-norm.

## Credit

- The construction and the sentence are Cinna Davis's (#4100).
- The failure of the product reading and the `C` table are unpaidmoon's (#4371).
- #4320 and #4311 are earlier audits of the same chain.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
