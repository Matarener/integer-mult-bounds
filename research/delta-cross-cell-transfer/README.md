# The δ halo exponents 11, 24, 26, 26 and 6 transfer across cells, and survive the "rounded" reading

**Claim type:** a conditional transfer lemma plus a robustness lemma, with exact rational checks.
**No new κ.** It answers the open question of jwr404's
[#4452](https://github.com/CrocSwap/integer-mult-bounds/pull/4452) and of my #4460: do the within-cell
δ exponents survive on the banded reference across cells? The ideal gaps `1/(8p²)` stay hypotheses.

## Setting

The banded reference `H` has diagonal exactly one and bandwidth `W ≤ p − 1`. The ideal Gaussian matrix
`N` has row and column off-sums `T ≤ 1 − g`, where `g = 1/(8p²)`. Within cells, `|H| ≤ N/(1 − δ)` with
`δ = 2^{2−32760p}`, as in #4451 and #4452.

## Lemma A: the downward reading

LOG-A says "across cells, use the retained downward Gaussian entries", and #4449 proves the matching
contract `0 ≤ H ≤ n`. Split each off-sum as `T = T_in + T_out`. Then

    off(H) ≤ T_in/(1−δ) + T_out ≤ T/(1−δ) ≤ (1−g)/(1−δ),

because `(1−δ)[T_in/(1−δ) + T_out] − T = −δ·T_out ≤ 0`. This is #4442's column split with δ in place
of `1/(16p²)`. The global Neumann ceiling is therefore exactly #4452's
`U = 8p²(D−4)/(D−32p²)`, so all five exponents transfer verbatim.

## Lemma B: any reading with a small excess

Suppose every row and column off-sum of `|H|` is at most `(1 − g) + ρ`, with `ρ ≤ 1/(32p³)`. Then
`1 − off ≥ (4p−1)/(32p³) ≥ 7/(64p²) > 1/(10p²)`. Hence:

- `‖H^{−1}‖₂ < 10p²`, so `100p⁴ < p^{11}` gives spectral endpoint 11;
- `10p² < p⁶` gives normalizer 6;
- the series error `< 10p²·e^{−p²} < p⁶e^{−p²}` at length `p^{24}`;
- bandwidth and agreement distance stay below `p^{26}`.

Per entry, an absolute error `e ≤ 1/(64p⁴)` on the at most `2W` band entries of a row or column is
enough. The downward reading has `ρ ≤ 2δ`, far inside this budget.

**Why this matters.** #4442 noted that FINE-PRIME says "rounded Gaussian entries" where LOG-A says
"downward". Under the coarser ceiling `16p² − 1`, an overshoot of one part in 64 already broke the
argument at `p = 2`. Under δ, the exponents no longer depend on the direction of rounding. Any rounding
with absolute error at most `1/(64p⁴)` per entry works. In particular FINE-PRIME's own
`poly(p)·2^{−(C−o(1))p}` row and column perturbation works eventually, which matches the eventual
status of the ideal gaps.

**#4449's repair is not needed for these exponents.** The raw negative-exponential oracle output `z`,
with `|z − n| < 2η` and `η = 2^{−32768p}`, has a per-row excess of at most `2(p−1)·2η`. That is far
below `1/(32p³)`, and the verifier checks it for every `p` from 2 to 64. Downward repair (#4449) is still
what gives the exact ceiling `U` of Lemma A.

**Near-tightness at `p = 2`.** On this route the excess tolerance at `p = 2` lies in
`(0.0091, 0.0092)`. The budget `1/(32p³) = 1/256` sits inside it.

## Checks

`verify.py` checks:

- the pinned LOG-A, FINE-PRIME and downstream phrases;
- the split identity, as a polynomial identity of degree at most 2 per variable, on a 3×3×3 grid
  (which proves it identically);
- Lemma A's ceiling and exponents, exactly for `p` in 2..64, at several within/across shares;
- Lemma B's gap, `B`, endpoint, normalizer, per-entry budget and bandwidth, exactly for `p` in 2..64,
  together with the all-`p` inequalities `70 > 64`, `100 < p⁷` and `10 < p⁴`;
- the `p = 2` tolerance interval.

| | value |
| --- | --- |
| global ceiling, downward reading, `p = 2` | `U = 32.000…` (just above 32) |
| robust excess budget | `1/(32p³)` per row or column |
| per-entry budget | `1/(64p⁴)` |
| `p = 2` tolerance | in `(0.0091, 0.0092)` |

## Not covered

- The ideal gaps `1/(8p²)`.
- Whether an existing page generator implements either rounding.
- The Schur complement and the core exponent 400.
- The #4100 notes, which keep 20, 42, 45, 48 and 100.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/delta-cross-cell-transfer --check-only
python3.12 -B scripts/research_package.py --package research/delta-cross-cell-transfer
```

The verifier prints `PASS_DELTA_CROSS_CELL_TRANSFER` in about 45 seconds, using only the standard
library.

## Open next questions

1. **Do the smaller exponents propagate through the Schur complement?**
   - *Why it matters:* the core exponent 400 still dominates the agreement distance 26.
   - *First step:* restate the interior elimination's row-dominance gap with `B < 10p²` in place of
     `16p² − 1`.

## Credit

- The column split, the exponent route and the question are James Reed's (jwr404: #4442, #4451,
  #4452).
- The across-cell rounding contract is mihir-s-05's (#4449).
- The source sentences come from LOG-A, FINE-PRIME and the downstream phase-cell report.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
