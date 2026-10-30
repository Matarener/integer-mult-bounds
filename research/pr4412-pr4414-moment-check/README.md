# Independent check of the strictification inequalities in #4412 and #4414

**Claim type: an independent certified finite check. No new κ.** This
accepts neither PR. It checks none of their native audits, outer ledgers or
inherited premises.

## Object

1337isnot1337's two predecessors of #4416 (whose check is
[#4420](https://github.com/CrocSwap/integer-mult-bounds/pull/4420)) each
tensor a native mixed unit, then split paid jobs at a cutoff `J`. With
`α = P_τ/T_τ`, `γ = P_1/(b^C T_τ)` and `X_τ = Σ n_r r^τ`:

| PR | conditional κ | saving `C` | cutoff | needs |
| --- | --- | --- | --- | --- |
| [#4412](https://github.com/CrocSwap/integer-mult-bounds/pull/4412) | 0.00247755 | `0.00247756` | `J = 4^n` | `α < 1 − 10⁻⁹`, `γ < 999/1000`; with `n = 15000`, `1/(1+n/10⁹) + 2(999/1000)^n < 1` |
| [#4414](https://github.com/CrocSwap/integer-mult-bounds/pull/4414) | 0.00267987 | `0.00267988` | `J = ⌊(19/4)^v⌋` | `α < 1 − 10⁻⁸`, `γ < 9999/10000`; with `v = 150000`, `1/(1+v/10⁸) + 4/2¹⁵ < 1` |

No outside check existed for either.

## Results

Every link holds, recomputed with exact rationals and enclosure widths below
`10⁻³⁰`. The enclosures overlap each PR's recorded intervals.

| | #4412 | #4414 |
| --- | --- | --- |
| Invoice: targets / paid calls, rank-one moments | 3,528 / 25,774; 47,075 vs 46,851 | 6,648 / 48,442; 108,769 vs 108,257 |
| `α` | `0.999999996840`; `1 − α = 3.16·10⁻⁹` | `0.999999982435`; `1 − α = 1.76·10⁻⁸` |
| `γ` | `0.9989653420` (base 4) | `0.9998629803` (base 19/4) |
| Closing bound | surplus `1.4392544772·10⁻⁵`, inside the recorded interval | exactly `16386003/16408576`, gap `22573/16408576` |
| **Limit saving `C*` (α = 1)** | `0.002477561641`, **`1.6·10⁻⁹` above the tested saving** | `0.002679889969`, **`1.0·10⁻⁸` above** |

`γ` stays below 1 at each `C*`. So, as at #4416, each tested saving sits at
its own invoice's ceiling. Larger powers cannot raise either κ; only a
different invoice can.

Other checks:

- #4414's `(9999/10000)^10000 < 1/2` is exact.
- #4414's control holds: the integer cutoff base 4 fails the tail, since
  `γ > 1` there.
- #4412's cutoff base 4 lies below its minimum target rank 5.

## Not covered

- The native audits behind `T` and `P`. **Tightest margin:** #4412's `α`
  clears `1 − 10⁻⁹` by only `2.2·10⁻⁹`.
- The tensor and splitting proofs, the compiler ranks, the outer rows and
  every inherited premise.

## Reproduce

```sh
python3.12 -B research/pr4412-pr4414-moment-check/verify.py
```

It prints `PASS_PR4412_PR4414_MOMENT_CHECK` in about 2 minutes, using only
the standard library.

## Open next questions

1. **Rebuild the three p6/p7 invoices from their native words** (#4412,
   #4414 and #4416).
   - *Why it matters:* every `α` margin is below `10⁻⁸`, while one paid call
     moves `α` by more than `10⁻⁶`.
   - *First step:* census the native words with separate code.
   - *Blocked by:* nothing.

## Credit

The constructions and invoices are 1337isnot1337's (#4412, #4414, with
OpenAI Codex assistance), building on zxv's #4359, #4405 and Jacob Alan
Sussman's Theorem 1G. Prepared by Ryanson Jonathan with substantial Claude
Code (Claude Opus 5.5) assistance. Apache-2.0.
