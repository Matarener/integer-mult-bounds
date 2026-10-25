# Independent check of #4449: downward rounding of the across-cell Gaussian coefficient

**Claim type:** an independent check by separate code, with exact rationals. **No new κ.** It covers
mihir-s-05's [#4449](https://github.com/CrocSwap/integer-mult-bounds/pull/4449) (head `1fb77b37`). That PR
supplies the across-cell contract `0 ≤ H ≤ n`, `n − H < 4·2^{−P}`, used by #4442 and by my #4462.

## What is checked

Setting: `s < t`, `u = α²`, `ρ = t/s`, `q_i = ⌊ti/s + 1/2⌋`, `b_i = ti − s·q_i`.

1. **The exact exponent.** `u((ρh + β_i)² − β_{i+h}²) = j/k`, with `j = u((th + b_i)² − b_{i+h}²)`
   and `k = s²`. So `n_{i,h} = exp(−πj/k)` exactly. Checked on 24,000 random cases with
   `s ≤ 60`, `t ≤ 3s`, `u ≤ 50`, `|i| ≤ 500`, `|h| ≤ 40`, including both signs of `h`.
2. **Ranges.** `−s/2 ≤ b_i < s/2`, with `j > 0` for every `h ≠ 0` and `j = 0` at `h = 0`.
3. **The second form.** `j/k = u·d(d + 2b_{i+h}/s)`, with `d = q_{i+h} − q_i`.
4. **The period cut.** `q_{i+s} = q_i + t` and `b_{i+s} = b_i`.
5. **The repair `H = max(0, z − 2η)`.** Tested against every admissible P-grid oracle output `z`
   (`|z − n| < 2η`) for 200 rational true values `n`: 794 cases, all giving `0 ≤ H ≤ n`,
   `n − H < 4η`, and `H` on the grid.
   - One ulp is not enough: `n = 3η/2` with `z = 3η` overshoots.
   - The constant 4 is a sharp supremum: `z = 2η` with `n → 4η`.
6. **The row bound.** At most `2W` entries give an across-cell rounding sum below `8Wη`.

All statements check out.

## Not covered

- Whether an existing page generator uses this construction. #4449 states the same limit.
- The fast exponential routine itself.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/cross-rounding-check --check-only
python3.12 -B scripts/research_package.py --package research/cross-rounding-check
```

The verifier prints `PASS_CROSS_ROUNDING_CHECK` in about a second, using only the standard library.

## Open next questions

1. **Does the across-cell bound `8Wη` fit inside my #4462 robust budget `1/(32p³)`?**
   - *First step:* with `W ≤ p − 1` and `η = 2^{−32768p}`, check `8(p−1)·2^{−32768p} ≤ 1/(32p³)`. It
     holds easily, so FINE-PRIME-style rounding at this grid is covered.

## Credit

- The construction and the proof are mihir-s-05's (#4449). The repair method comes from the retained
  phase-cell review.
- The entry law is LOG-A's.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
