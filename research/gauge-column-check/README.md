# Independent check of #4438: the within-cell gauge column transfer

**Claim type:** an independent check by separate code, with exact rationals where possible. **No new κ.**
It covers jwr404's [#4438](https://github.com/CrocSwap/integer-mult-bounds/pull/4438) (head `6157a47b`).

## What is checked

1. **The factorization.** On a constant-phase run (`β_{i+h} = β_i + θh`), LOG-A's entry factors as

       n_{i,h} = (a_i / a_{i+h})·exp(−aρh²),    with a_i = exp(aβ_i²/θ),

   because the exponent is `h²(1+2θ) + 2hβ_i`. This is checked in log form on 2,000 random runs
   (`p ∈ {2,3,5,10}`, `a` up to `5 log 16p`, `θ ∈ [1/(4p²), 1/p²]`). The maximum log error is
   `6·10⁻¹³`.
2. **The column bound.** For a downward kernel (`Ĝ/G ∈ [0.9, 1]` at random) and
   `(1−ε)a ≤ â ≤ a` at random with `ε = 1/(16p²)`, every column off-sum of `diag(â)Ĝdiag(â)^{−1}` is
   at most the ideal one divided by `1−ε`. The maximum observed ratio to the bound is 0.99977, so
   the bound is nearly tight.
3. **The ceiling, in exact rationals.** An ideal off-sum `1 − 1/(8p²)` with `ε = 1/(16p²)` leaves
   gap exactly `1/(16p² − 1)`. The gauge audit's `ε = 1/2` leaves no gap.
4. **The setup constant.** `C = 3` is the least integer with `2^{−Cp} ≤ 1/(16p²)` for every `p ≥ 2`.
   There is equality at `p = 2` (`64 = 64`), and `C = 2` fails there. This is checked to `p = 10⁴`,
   plus the induction ratio `(4/3)² < 8`.
5. **The downstream comparison.** `(2p−1)/(16p) > 1/(8p²)`, i.e. `p(2p−1) > 2`, for every `p`.

All statements of #4438 check out.

**Note.** `C = 3` meets the budget with *equality* at `p = 2`. That is fine for #4438's `ε ≤ 1/(16p²)`,
but there is no slack at `p = 2`.

## Not covered

- Across-cell entries (see #4442, #4449 and my #4462).
- The exponents of #4406.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gauge-column-check --check-only
python3.12 -B scripts/research_package.py --package research/gauge-column-check
```

The verifier prints `PASS_GAUGE_COLUMN_CHECK` in about a second, using only the standard library.

## Open next questions

1. **Does the δ-repaired weight (#4451) make `C` irrelevant here?**
   - *First step:* replace `2^{−Cp}` by `δ = 2^{2−32760p}`. Every comparison then holds with slack.

## Credit

- The lemma is James Reed's (jwr404, #4438).
- The entry law is LOG-A's.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
