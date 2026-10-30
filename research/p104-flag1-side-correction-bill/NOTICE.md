# Notice

This package applies explicit corrections to #3532's repaired P104 words R0
and R1 and to the published word in memory, and checks them with the published
native checker and a second scanner. It does not modify frozen upstream sources
or any other package. `inputs/pr3532/CERTIFICATE.json` and
`inputs/pr3532/REPAIR-RECIPES.json` are byte-identical copies of #3532's files
at head `8fecbf7df7b48c9004bd10a0da6a81f33d455737` (Wentao Li; open PR), kept
unchanged. The three recipes in `CORRECTION-RECIPES.json` were lowered with the
pinned `research/p104-native-channel/compile.py` and `vendor/clifford_exact.py`
(PR1991 lineage, Chafik Boukhalfa), whose notices are retained in that package.

Prepared by Wentao Li <wentaol4@illinois.edu> with substantial AI assistance.
Apache-2.0; predecessor notices and exact source pins are retained in
`SOURCES.json`.
