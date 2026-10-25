# Independent check of #4436's direct flow for overlapping ranks

**Claim type:** an independent re-implementation, checked against #4436's recorded flows, plus
exact recurrence values and a local trend. **No new κ.** The object is zxv's
[#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436), at head `56003680`, §2: the
partially matched integer lockstep flow for the case where paid ranks overlap target ranks
(`max paid < ambient`). In it:

- a parent round's issued jobs at point `b` are matched to the child demand
  `D(b) = Σ W_k·u(b − e_k)` over present child points;
- the remaining `u(b) − D(b)` jobs become paid boundary exits;
- child target slots that have no parent point become new sources.

## Results

`verify.py` implements the flow separately. It checks:

- **All 9 recorded finite flows.** The separated control at `n = 20, 40, 80`, the strict overlap at
  `n = 20, 40, 80`, and the source-open equality case at `n = 20, 40, 80` are reproduced exactly:
  sources, exits, boundary exits, column mass, unit count and matched jobs. #4436's
  `RESULT.json` values are copied into `VECTORS.json` with its SHA256.
- **Every rank on raw p7.** At every rank `121 ≤ N ≤ 1000`, all sources lie in `(N/m, N]`, all exits
  are below `N`, and the rank-one potential identity `Σ S_s·s − Σ X_e·e = 608 × (column mass)` holds
  exactly.
- **The exact leaf recurrence.** `L(1000) = 995.6296444195137…` lies inside #4436's printed interval.
  The effective saving there is `1 − log L/log N = 0.000634`, which confirms #4436's statement that
  rank 1,000 misses the target.

**Local trend.** `trend_local.py` computes the same recurrence in floating point. This is local
evidence and is not part of the verifier.

| `N` | `L(N)` | effective saving |
| --- | --- | --- |
| 1,000 | 995.6296 | 0.000634 |
| 3,000 | 2,982.0507 | 0.000750 |
| 10,000 | 9,926.6191 | 0.000800 |
| 30,000 | 29,742.7603 | 0.000835 |

For comparison, the separated p3 compiler of #4359, checked in my #4404, reached 0.001193 at
`N = 10⁴` against its limit of 0.002304. The direct p7 flow is climbing more slowly, toward a raw
root near 0.0027. These finite values neither prove nor refute an asymptotic direct exponent, which
#4436 leaves open.

## Not covered

- #4436's size bounds `B_N ≤ exp(O(N log N))`, its nested batching and its resource envelopes.
- Native premises.
- The asymptotic direct saving.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4436-direct-flow-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4436-direct-flow-check
```

The verifier prints `PASS_PR4436_DIRECT_FLOW_CHECK` in under a second, using only the standard
library.

## Open next questions

1. **Does the direct flow's complement-plus-exit recurrence admit a uniform estimate?** This is
   #4436's exponent gate.
   - *Why it matters:* it would remove the tensor and padding step.
   - *First step:* fit the measured exit mass as a function of `N`, and test whether the boundary
     exits carry a vanishing share of the `t`-potential.

## Credit

- The direct flow, the size bounds and the recorded flows are zxv's (#4436).
- The multinomial lockstep construction is Jacob Alan Sussman's Theorem 1G.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
