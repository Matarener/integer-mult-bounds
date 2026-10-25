# Independent check of #4439 and #4442: halo exponents under ε = 1/(16p²)

**Claim type:** an independent check of conditional exponent arithmetic, by separate code with exact
rationals. **No new κ.** It covers jwr404's
[#4439](https://github.com/CrocSwap/integer-mult-bounds/pull/4439) (within one cell, head `26af8afb`)
and [#4442](https://github.com/CrocSwap/integer-mult-bounds/pull/4442) (across cells under the downward
reading, head `d079c2b0`). It is the ε-route counterpart of my #4460, which covers the δ route.

## What is checked

- **The ceiling.** The split identity `(1−ε)[T_in/(1−ε) + T_out] − T = −ε·T_out` is proved as a
  polynomial identity on a 3×3×3 grid. It gives `off ≤ (1−g)/(1−ε) = (16p²−2)/(16p²−1)`, so the gap is
  exactly `1/(16p²−1)` and the absolute sums are below 2. Exact for `p` in 2..64.
- **The exponents**, with `B = 16p²−1`. Exact for `p` in 2..64, plus all-`p` arguments.

  | Role | Value | Reason |
  | --- | --- | --- |
  | spectral endpoint | 12 | `B² ≤ p^{12}`; for `p ≥ 3`, `(16p²)² < p^{12}` |
  | series length | 26 | error `< B·e^{−p²} < p⁶e^{−p²}` |
  | bandwidth and agreement distance | 28 | `(2p^{26} ± 1)(p−1) < p^{28}` |
  | normalizer | 6 | `B < p⁶`; 7 also works |

- **The "fails" entries.**

  | Exponent | Where it fails | Reason |
  | --- | --- | --- |
  | endpoint 11 | `p = 2` | `63² > 2^{11}` |
  | length 25 | `p = 2` | certified lower bound `(1−x)^L ≥ e^{−xL−x²L}` |
  | 27 | `p = 2` (loose count) and `p ≥ 3` (sharp count) | |
  | normalizer 5 | `p = 2` | `63 > 32` |

- **#4442's tightness at `p = 2`.** An overshoot of 1/64 exceeds the ceiling, since
  `63·63 = 3969 > 3968 = 62·64`.
- **#4442's bare-kernel example.** With `θ = β = 1/4`, `h = 1`, `g = 2`, the next phase is `−1/2`.
  The square gap is `2 = 32/16`, against `ρh² = 5/4 = 20/16`.

All statements check out.

## Not covered

- The ideal gaps.
- The rounding contract, which is #4449.
- The δ route, which is my #4460 and #4462.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/eps-halo-exponent-check --check-only
python3.12 -B scripts/research_package.py --package research/eps-halo-exponent-check
```

The verifier prints `PASS_EPS_HALO_EXPONENT_CHECK` in under a second, using only the standard library.

## Open next questions

1. **None specific to the ε route.** It is superseded by the δ route (#4452, #4460, #4462).

## Credit

- The lemmas and exponents are James Reed's (jwr404: #4439 and #4442).
- The entry law is LOG-A's.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
