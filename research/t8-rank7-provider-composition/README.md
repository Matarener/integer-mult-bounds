# Eight replicas for the current rank-seven providers

This descendant of [PR3465](https://github.com/CrocSwap/integer-mult-bounds/pull/3465), exact head `52c8434c4b184dbbd3e080aff43b0a9714fe8bf1`, reduces the architecture from sixteen replicas to eight. It retains both 408-helper native words and projects the authenticated PR3413 chronology onto replicas 0 through 7, then constructs a new allocation under the resulting actual source windows.

**Complete finite admission passes**, with conditional `κ = 0.001728992447095271166656 - 10^-46 - 10^-70`. The exact improvement over PR3465 is `0.000001738106498620572263`. This improves the reduced-replica branch and remains below the supported T740 global endpoint. Selected records are unchanged.

| Quantity | Value |
| --- | --- |
| Replicas / calls / helper occurrences | 8 / 72 / 29,376 |
| Certificate allocations / nonzero flows | 106 / 645 |
| Idle profile | `1964 H1 + 534 H3 + 172 H5 + 2 H7 + 3050 H48` |
| Full paid profile | `{1:177140,2:52128,3:16950,4:7344,5:1612,7:2,8:576,48:3050}` |
| Rank mass / deficit / live stock | 520,704 / 2,560 / 7,168 |
| Complete physical stock | `7168 + 408 + 8 + 91 + 2 = 7677` |
| Dispatch | `(0,0): extra`; remaining 71 calls: `gauge44` |

Two rational engines certify complex endpoint `0.001728992447095271166656`, approximately 99.95461568983635598% of the same current-word packing cap. `CAP-RATIO.json` retains exact rational bounds and attribution to PR3361. The old outer adapter's separately labeled diagnostic is not the modern admitted exponent. No chronological or T8 packing optimum is claimed.

The complete replay freshly checks owners, parent lift, physical/controller invoice, discovery, both outer engines and final release. It explicitly reuses authenticated native-provider artifacts from a prior fresh PR3148 replay; no fresh native-provider rebuild is claimed here. The unchanged compressed overlay and canonical source closure avoid duplicating that scientific ancestry. `PREDECESSOR-3465.json` binds the immediate predecessor.

## Reproduce

Use Python 3.12, numpy 2.3.5 and sympy 1.14.0 (tested with mpmath 1.3.0):

```sh
python3 -I -Werror -B reconstruct.py
python3 -I -Werror -B price_profile.py
python3 -I -Werror -B test_reconstruct.py
python3 -I -O -Werror -B test_reconstruct.py
python3 -I -Werror -B test_materialize.py
python3 -I -Werror -B verify.py --work /absolute/new/external/admission
```

Verification requires no optimizer. The registered exporter includes the canonical sources needed by the authenticated materializer. Outputs are external and source bytes remain unchanged. Eleven reconstruction test groups include malformed replica labels, missing calls, wrong fixed geometry, changed windows, malformed flows, actual owner faults and source corruption. Materializer controls additionally reject archive and source tampering.

See `PROOF.md` for chronology, allocation and complete-cost obligations and `BOUNDED-DOMAIN.md` for the stopped discovery scope. The inherited analytic assumptions and all-size compiler, common-label/mutable-source, precision/tape and exact-recovery obligations remain distinct from complete finite admission.

T8 itself is prior art: `research/gauge44-slots-arcflow`, `gauge44-slots-deepen-arcflow`, `gauge44-slots-balance-arcflow`, and `gauge44-slots-t16-arcflow` retain older eight-replica constructions and comparisons (including the PR1005/PR1018 480-helper ancestry). This contribution claims the actual current 408-helper supplier composition, projected schedule and complete new allocation/admission, not the first eight-replica architecture.

## Open next questions

1. Can fewer replicas satisfy actual owner windows and a fully charged invoice? Start with necessary family/width and exact cost bounds before another bounded allocation.
2. Can an omitted T8 pattern or changed schedule improve this specific certificate? Name an uncovered domain and preserve all source-event constraints; no optimality is claimed here.
3. Can a changed recursive interface beat the stronger T740 endpoint? A complete native cost ledger and the inherited all-size obligations remain necessary.
