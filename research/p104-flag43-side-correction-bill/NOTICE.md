# Notice

This package applies explicit corrections to #3508's repaired P104 word R0 in
memory and checks them with the published native checker and a second scanner.
It does not modify frozen upstream sources or #3508's package. The two recipes
in `CORRECTION-RECIPES.json` were lowered with the pinned
`research/p104-native-channel/compile.py` and `vendor/clifford_exact.py`
(PR1991 lineage, Chafik Boukhalfa), whose notices are retained in that package.
Correction T also reuses #3508's committed `W6 -> FULL` recipe.

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
Apache-2.0; predecessor notices and exact source pins are retained in
`SOURCES.json`.
