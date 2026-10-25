# A source-window swap improves the T8 allocation

This focused descendant of [PR3468](https://github.com/CrocSwap/integer-mult-bounds/pull/3468), exact head `dbeac6cf5c1190459fb5ed7a6020bdc50641577d`, swaps adjacent calls `(1,3)` and `(2,2)` at zero-based times 11 and 12 and repairs twelve chronological allocation groups. The source windows are rederived after the swap. Both 408-helper native words and the complete physical stock remain unchanged.

**Complete finite admission passes**, with conditional `κ = 0.001728996308346386172130 - 10^-46 - 10^-70`. This is an exact gain of `3.861251115005474E-9` over PR3468. The paid-profile change is `-3 H1 + H3`, strictly favorable for `0<a<1`. This remains a scoped T8 branch improvement below the supported T740 global endpoint; selected records are unchanged.

| Quantity | Value |
| --- | --- |
| Replicas / calls / helper occurrences | 8 / 72 / 29,376 |
| Certificate allocations / nonzero flows | 107 / 651 |
| Idle profile | `1961 H1 + 535 H3 + 172 H5 + 2 H7 + 3050 H48` |
| Full paid profile | `{1:177137,2:52128,3:16951,4:7344,5:1612,7:2,8:576,48:3050}` |
| Rank mass / deficit / live stock | 520,704 / 2,560 / 7,168 |
| Complete physical stock | `7168 + 408 + 8 + 91 + 2 = 7677` |
| Dispatch | `(0,0): extra`; remaining 71 calls: `gauge44` |

Two exact rational engines certify the complex endpoint above, approximately 99.95483891225235365% of the same current-word packing cap. `CAP-RATIO.json` retains the exact rational comparison and PR3361 attribution. The independently labeled ancestral outer diagnostic is not the modern admitted exponent. Neither chronological nor packing optimality is claimed.

The replay freshly checks the changed owners, parent lift, controller/physical invoice, discovery ledger, both outer engines and final release. Both native-provider artifacts are explicitly reused from an authenticated prior fresh PR3148 replay; no fresh native-provider rebuild is claimed here. Source closure and the compressed overlay are unchanged from PR3468. `PLAN-3468.json`, `PREDECESSOR-3468.json` and `ORDER-RECIPE.json` bind the source chronology and the single declared change.

## Reproduce

With Python 3.12, numpy 2.3.5 and sympy 1.14.0 (tested with mpmath 1.3.0):

```sh
python3 -I -Werror -B reconstruct.py
python3 -I -Werror -B price_profile.py
python3 -I -Werror -B test_reconstruct.py
python3 -I -O -Werror -B test_reconstruct.py
python3 -I -Werror -B test_materialize.py
python3 -I -Werror -B verify.py --work /absolute/new/external/admission
```

Verification has no optimizer dependency. The registered source exporter and authenticated materializer close the scientific inputs. Outputs are external; no source is rewritten. Twelve test groups reject malformed counts, flows, calls, windows, owner fields, provider/source corruption, and undeclared or omitted swaps. Full native/controller/outer execution is mandatory in `verify.py`.

## Open next questions

1. Can a different source-compatible chronology produce another fully charged gain? This result covers one adjacent swap and twelve-group repair only.
2. Can a changed recursive interface beat the stronger T740 supplier cap, beyond reduced-replica packing gains?
3. The inherited all-size compiler, common-label/mutable-source realization, precision/tape and exact recovery remain separate obligations from finite admission.

T8 itself is prior art, including the older gauge44-slots-arcflow and gauge44-slots-t16-arcflow constructions. This contribution claims the stated current-provider chronology/allocation composition, not the first eight-replica architecture. See `CREDITS.md` for ancestry.
