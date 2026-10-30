# Notice

This package applies explicit end-cut corrections to the published P104 native
channel word in memory and checks them with the published native checker and a
second scanner. It does not modify frozen upstream sources. The three recipes
in `CORRECTION-RECIPES.json` were lowered with the pinned
`research/p104-native-channel/compile.py` and `vendor/clifford_exact.py`
(PR1991 lineage, Chafik Boukhalfa), whose notices are retained in that package.

Open [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614),
[#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601),
[#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610),
[#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) and
[#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) are
leave-alone citations. The deferred flag-9 head-step repair is not reopened.

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
Apache-2.0; predecessor notices and exact source pins are retained in
`SOURCES.json`.
