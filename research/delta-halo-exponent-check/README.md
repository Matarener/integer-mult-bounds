# Independent check of #4451 and #4452: the halo exponents 11, 24, 26, 26 and 6 inside one cell

**Claim type:** an independent check of conditional exponent arithmetic, by a separate proof route
plus exact rational arithmetic. **No new κ.** It covers jwr404's
[#4451](https://github.com/CrocSwap/integer-mult-bounds/pull/4451) (head `be243a28`) and
[#4452](https://github.com/CrocSwap/integer-mult-bounds/pull/4452) (head `af68f597`). The ideal gaps
`1/(8p²)` stay hypotheses.

## What is checked

Notation: `D = 2^{32760p}`, `δ = 4/D`, `g = 1/(8p²)`, `η = 2^{−32768p}`.

1. **(R) Relative-error repair (#4451).** From `a − 4η < â ≤ a` and `a > 2^{−8p}`, we get
   `a/â < 1/(1 − 4η·2^{8p}) = 1/(1 − δ)`. Also `δ < 1/(16p²)`.
2. **(N) Neumann ceiling.** The identity `(1 − δ)/(g − δ) = U = 8p²(D − 4)/(D − 32p²)` is checked
   exactly. Also the rounded off-sum `(1 − g)/(1 − δ)` is below 1, so the absolute sums are below 2.
3. **(B) The U chain, for all `p ≥ 2`, by a route different from the PRs'.** From `p < 2^p` we get
   `512p⁴ < 2^{4p+9} ≤ D`, so `r = 32p²/D < 1/(16p²)`. With `V = 8p²/(1 − r)`:

       8p² < U < V < 8p² + 1 ≤ 16p² − 1 < p⁶,      V² < (8p² + 1)² < p^{11}.

   The last step is `1089 < 2048` at `p = 2`, and `(8p²+1)² ≤ 81p⁴ ≤ p⁸` for `p ≥ 3`.
4. **(S) Neumann polynomial.** `P − A^{−1} = −Q^L A^{−1}` and `‖Q‖ < 1 − p^{−22}`, so the error is
   below `U·e^{−p^{−22}L}`. At `L = p^{24}` that is `U·e^{−p²} < p⁶e^{−p²}`. The bandwidth is
   `(2L ± 1)(p − 1) < p^{26}`.
5. **Exact replay.** Every inequality in 1–4 is checked with `Fraction` for each `p` from 2 to 64.
6. **The "fails" column at `p = 2`.**
   - `U > 32 = p⁵`, so normalizer 5 and spectral endpoint 10 fail.
   - Length `p^{23}` fails on this route, by the certified lower bound `(1−x)^L ≥ e^{−xL−x²L}`.
   - The loose radius `2p^{24} + 1` exceeds `p^{25}`.

| Role | #4452 | Confirmed |
| --- | ---: | --- |
| Spectral endpoint | 11 | yes; 10 fails at `p = 2` |
| Series length | 24 | yes; 23 fails at `p = 2` |
| Bandwidth | 26 | yes; 25 fails (loose count at `p = 2`, sharp count for `p ≥ 3`) |
| Agreement distance | 26 | yes |
| Normalizer | 6 | yes; 5 fails at `p = 2` |

## Remarks

- **The sharp count at `p = 2` is below `p^{25}`.** The sharp bandwidth count is `2^{25} − 1`, so
  "25 fails" at `p = 2` holds only for the loose count `(2p^{24}+1)W`. For `p ≥ 3`, the sharp count
  exceeds `p^{25}`, so the uniform conclusion is unchanged. #4452's text already says this, and the
  verifier records it explicitly.
- **#4452 relies on `Ĝ_0 = 1`.** The Neumann step needs the unit diagonal. #4452's lemma states only
  `0 ≤ Ĝ ≤ G`, but `Ĝ_0 = 1` is inherited from #4438/#4439. A future write-up should restate it.
- **"Smallest" is relative to this proof route.** The failures are failures of the stated
  majorant route, not lower bounds for the actual block.

## Not covered

- The ideal gaps `1/(8p²)` for every prime.
- Across-cell entries (#4449, #4442).
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/delta-halo-exponent-check --check-only
python3.12 -B scripts/research_package.py --package research/delta-halo-exponent-check
```

The verifier prints `PASS_DELTA_HALO_EXPONENT_CHECK` in about 20 seconds, using only the standard
library.

## Open next questions

1. **Do 11, 24, 26, 26 and 6 survive across a cell?**
   - *Why it matters:* this is #4452's own open question, and the global reference still uses
     20, 42, 45, 48 and 100.
   - *First step:* #4442's column split with `δ` in place of `1/(16p²)`, using #4449's `0 ≤ H ≤ n`.

## Credit

- The lemmas, exponents and proofs are James Reed's (jwr404, #4451 and #4452, building on #4438 and
  #4439).
- The downward rounding contract is in the pinned downstream phase-cell report.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
