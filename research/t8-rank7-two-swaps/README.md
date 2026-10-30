# Two early swaps concentrate the T8 idle profile

This focused descendant of [PR3485](https://github.com/CrocSwap/integer-mult-bounds/pull/3485), exact head `1ee2ac4be28f284d75eac0869f2049025f94b94b`, applies adjacent swaps8/9 then7/8 to its call order. Thus `(1,2),(2,1),(3,0)` becomes `(3,0),(1,2),(2,1)` at zero-based times7 through9. It retains PR3485's earlier swap and repairs twelve allocation groups under rederived source windows.

**Complete finite admission passes**, with conditional `κ = 0.001729097946885651030613 - 10^-46 - 10^-70`. The exact improvement over PR3485 is `1.01638539264858483E-7`. The paid change `-21H1+H3-2H7+H32` is favorable for every `0<a<1` by strict concavity and majorization. This is a scoped T8 branch improvement below T740; selected records remain unchanged.

| Quantity | Value |
| --- | --- |
| Replicas / calls / helper occurrences | 8 / 72 / 29,376 |
| Certificate allocations / nonzero flows | 108 / 653 |
| Idle profile | `1940H1 + 536H3 + 172H5 + H32 + 3050H48` |
| Full paid profile | `{1:177116,2:52128,3:16952,4:7344,5:1612,8:576,32:1,48:3050}` |
| Rank mass / deficit / live stock | 520,704 / 2,560 / 7,168 |
| Complete physical stock | `7168+408+8+91+2=7677` |
| Dispatch | `(0,0): extra`; remaining71calls: `gauge44` |

Two exact rational engines certify the endpoint above, approximately 99.96071472804817331% of the same current-word packing cap. `CAP-RATIO.json` retains exact rational inputs and PR3361 attribution. No chronological or packing optimum is claimed, and the separately labeled ancestral outer diagnostic is not the modern admitted exponent.

Full replay freshly checks changed owners, parent lift, controller/physical invoice, discovery ledger, both outer engines and final release. Native artifacts are explicitly reused from an authenticated prior fresh PR3148 replay; no new native-provider rebuild is claimed. Both408-helper words, dispatcher,91private cleanup families and scientific source closure are unchanged. `PLAN-3485.json`, `PREDECESSOR-3485.json` and `ORDER-RECIPE-3485.json` bind the immediate source and exact new swaps, with earlier ancestry retained.

## Reproduce

Use Python3.12, numpy2.3.5 and sympy1.14.0 (tested with mpmath1.3.0):

```sh
python3 -I -Werror -B reconstruct.py
python3 -I -Werror -B price_profile.py
python3 -I -Werror -B test_reconstruct.py
python3 -I -O -Werror -B test_reconstruct.py
python3 -I -Werror -B test_materialize.py
python3 -I -Werror -B verify.py --work /absolute/new/external/admission
```

Verification requires no optimizer. The registered exporter and authenticated materializer close the scientific inputs; outputs are external and no source is rewritten. Thirteen control groups exercise malformed flows, replica labels, source/owner faults, altered native widths, and undeclared, reordered, fractional or omitted swaps. Full admission is mandatory in `verify.py`.

## Open next questions

1. Can a distinct legal chronology concentrate more idle mass with the full native/physical bill? This result covers only the stated two-swap repair.
2. Can a changed recursive interface exceed the stronger T740 endpoint rather than only improving reduced-replica packing?
3. The inherited all-size compiler, common-label/mutable-source, precision/tape and exact-recovery obligations remain separate from finite admission.

Eight-replica architectures predate this work, including the older gauge44-slots-arcflow and gauge44-slots-t16-arcflow constructions. This contribution is the stated current-provider chronology/allocation composition. See `CREDITS.md`.
