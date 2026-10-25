# Independent check of #4437: the ideal column majorant survives g = 2 steps

**Claim type:** an independent numerical check with explicit tolerances. **No new κ.** It covers jwr404's
[#4437](https://github.com/CrocSwap/integer-mult-bounds/pull/4437) (head `7ca94e97`). That PR extends
#4402's column majorant from one constant-phase run to every column of the ideal narrow matrix,
including steps `g = 2`.

## What is checked

The ideal matrix `N` is built directly from LOG-A's entry law, without #4437's code:

- `n_{i,h} = exp(−a[(ρh + β_i)² − β_{i+h}²])`, with `ρ = 1 + θ`;
- `β_i = ρi − q_i ∈ [−1/2, 1/2)`, so `q_i = ⌊ρi + β_0 + 1/2⌋` and every step is 1 or 2.

1. **The majorant.** Every interior column off-sum is at most
   `M = e^{−2aθ} + e^{−2a(1−θ)} + 2e^{−2a}/(1−e^{−4a})`. The grid is
   `p ∈ {2,3,5,10}`, with `a` at both GAUSSIAN ends (`4 log 16p`, `5 log 16p`) and at 1, 1/2 and 1/4,
   with `θ ∈ {1/(4p²), 1/p², 0.2, 0.25}`, and 20 phases `β_0`. That is **192,000 columns**, of which
   **55,515 meet a `g = 2` step**. A local run of 704,000 columns (203,625 with `g = 2`) agrees.
2. **Sharpness.** The maximum of off-sum/`M` is **1.0** to floating precision, so the majorant is
   attained and cannot be improved uniformly.
3. **The landing intervals.** At every column, #4437's table holds: incoming `g = 2` gives
   `β ∈ [−1/2, −1/2+θ)`; both steps 1 give `β ∈ [−1/2+θ, 1/2−θ)`; outgoing `g = 2` gives
   `β ∈ [1/2−θ, 1/2)`.
4. **The gap.** `1 − M > 1/(8p²)` at both `θ` ends with `a = 4 log 16p`, the worst case since `M`
   decreases in `a`, for every `p` from 2 to 10⁴. The minimum of `8p²·gap` is 26.3. The perturbed gap
   stays above `1/(16p²)` once `2pε ≤ 1/(16p²)`.

## Not covered

- An all-`p` proof of item 4. #4437 gives the written argument, and this check only samples `p`
  up to 10⁴.
- The rounded reference `H`, `‖N^{−1}‖₁`, and any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/column-cut-check --check-only
python3.12 -B scripts/research_package.py --package research/column-cut-check
```

The verifier prints `PASS_COLUMN_CUT_CHECK` in about 5 seconds, using only the standard library.

## Open next questions

1. **Does the attained majorant leave room for the δ-route ceiling?**
   - *Why it matters:* my #4462 uses an ideal gap of `1/(8p²)`, while the true gap here is at least
     `26/(8p²)`.
   - *First step:* redo #4462's Lemma B with the measured gap `3.3/p²`.

## Credit

- The lemma and the proof are James Reed's (jwr404, #4437, building on #4402).
- The entry law is LOG-A's.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
