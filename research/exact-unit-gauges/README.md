# Exact native unit gauges: 686 without scratch, 674 with one field

This package replaces four disjoint, authenticated common-chart scalar blocks. Their allowance per orientation is 766 in canonical main and 698 in the rank-factor predecessor [PR #4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494). An exact power-of-two gauge optimizer reaches **686 with no additional owned fields**. Selecting the cheaper of gauges and the predecessor's rank-one sum macro reaches **674 with one reusable owned field**. Both inverse-transpose orientations have the same bills, including all scale/unscale operations and owned-field clears.

| Forward persistent scalar ordinals, full_frame_cleanup | Original | #4494 | Gauge, no scratch | Hybrid, one field |
|---|---:|---:|---:|---:|
| 4727–4764 | 418 | 366 | 358 | 358 |
| 1615–1620 | 52 | 46 | 52 | 46 |
| 2900–2905 | 52 | 46 | 52 | 46 |
| 4251–4276 | 244 | 240 | 224 | 224 |
| Total per orientation | 766 | 698 | 686 | 674 |

The new mechanism is scalar gauge selection with an integer circulation certificate. The second mechanism, rank-one aggregation, is explicitly inherited from #4489/#4494. This is a strict local scalar-cost improvement, **not a new κ**, complete supplier, measured runtime improvement, or unrestricted circuit optimum. No recursive jobs or productive-temporary credits are added. The zero-scratch version preserves the original 632-field ABI; the hybrid needs one extra reusable owned field and clears its arbitrary dirty entry and exit values.

From repository root:

```sh
python3 -I -O -B research/exact-unit-gauges/verify.py
python3 scripts/research_package.py --package research/exact-unit-gauges
```

The verifier authenticates source bytes, derives actual contiguous source windows, checks exact symbolic maps including dirty destinations, prices every instruction with the retained source pricing function, and independently checks the feasible signed flow and matching potential objective. See PROOF.md for the universal sufficient construction. RESULT.json contains emitted programs and complete integer flow certificates. No solver package or platform-specific dependency is needed.

## Open next questions

1. Can gauge optimization be inserted into the full native rebuild, followed by a complete stock, norm, coefficient and multiplication-bound replay? First preserve the original four window selectors and compare the rebuilt forward/backward words. This package does not perform that replay.
2. Can one optimize gauge choice jointly with dyadic rank factors? Try only small exact candidates and retain exact scalar bills; rational rank alone does not minimize scalar cost. No claim of global circuit optimality follows from the restricted gauge optimum.

Current main, guidance and recent PRs were checked for this 20-minute session; coverage limitations and predecessor credit are in ATTRIBUTION.md. The selected result and authoritative MathProof DAG are unchanged.
