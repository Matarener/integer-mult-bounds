# Fixed-point exponential for the first ceiling evaluation

**Opt-in replay speedup. No new κ. The pinned ceiling engine is unchanged.**

For the selected local word, the fixed-point exponential returns the same 256-bit bounds as the pinned Taylor series, so the published ceiling bracket is unchanged.

The catalogue asked for one measured replay stage. `scripts/research_baseline.py` cannot bind the selected frontier here: its checker imports `verify_selected_result`, which then requires the frontier1094 package roots, and those roots are not in this checkout. The profiled stage is one `ceiling()` call on the selected complex local word inside the unchanged [ceiling engine](../complex-local-word-ceiling/ceiling.py). On CPython 3.14, `cProfile` attributed most of that call to `math.gcd` inside the exponential Taylor series. One evaluation took about 0.82 seconds before this kernel and about 0.02 seconds with it. The verifier remeasures both and requires at least a 5× median improvement on the same bracket.

[exact-child-interval-reuse](../exact-child-interval-reuse/README.md) already memoizes repeated `child_cost` intervals. Its own note says the first fill is only about 1.14× faster; the large ratio appears on a warm repeat. [exact-exp-performance](../exact-exp-performance/README.md) speeds a different, degree-16, 200-bit owner-check kernel, and that complete check improved by only a few percent. [ceiling-range-reduction](../ceiling-range-reduction/README.md) extends the logarithm and exponential domain; it does not claim identical intervals. This package does not replace any of those results and does not edit `ceiling.py`. Other packages authenticate that file's SHA-256 `86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc`.

## What is checked

The fixture is the selected paid profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` with `m=73`, 896 live families, 9 stages and centre 64. The published bracket is

`52814190909/31250000000000 < a < 1690054109089/1000000000000000`.

Every exponential argument visited by that search, and by the same search after one extra rank-1 child, is compared with the pinned series. A one-term truncation of the new series is rejected. Arguments outside `0 <= low <= high <= 1/2` are rejected. Logarithms are filled before the timed section so the comparison is the exponential, not the first `ln` walk. Three pairs alternate which engine runs first. There is no cross-run cache: a changed `ceiling.py` fails the hash pin, and a shortened series fails the bound comparison.

## Reproduce

From the repository root, with the standard library only:

```sh
python3 scripts/research_package.py --package research/ceiling-exp-fixed-point --check-only
python3.12 scripts/research_package.py --package research/ceiling-exp-fixed-point
```

Expected marker: `PASS_CEILING_EXP_FIXED_POINT`. Wall times are machine-specific. The 5× gate is there so a kernel that stops being faster fails closed; it is not a portable performance certificate.

## Open next questions

1. Do these fixed-point bounds equal the pinned series for every rational argument in `[0, 1/2]`, or only on the selected screen and the arguments this verifier visits? A divergent argument could make an opt-in caller certify a different bracket. The first step is to compare both engines on a denominator sweep outside the selected ranks. Until that identity is proved, the pinned file remains the authority and this kernel stays opt-in.

## Credit

The interval engine and the published selected-word ceiling are Douglas Colkitt's, with Claude assistance, in `research/complex-local-word-ceiling`. The memoized child-cost reuse, the degree-16 integer exponential, and the range-reduction adapter remain their authors' work in the packages named above. Prepared by Riquelme Soares (@hevlyo), with substantial AI assistance for profiling, the integer series, and the equality checks. No independent human review is claimed. Apache-2.0.
