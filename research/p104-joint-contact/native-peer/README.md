# Exact dense audit of the four added P104 MOVE maps

All 512 columns of each of the four new actual MOVE interfaces pass exact complex dyadic comparison, including absolute global phase. There are **1,048,576 complex entry comparisons per mode**. This is a focused delta audit, with no new construction, kappa, selected promotion or full-framework admission claim.

The reviewed predecessor is PR5545 commit `18968423711fd902aaee1099979497d55603e1dc`; the reviewed successor is PR5551 commit `79072da5404a01056df2af2e4132324b01c72366`. Both actual words, all imported source bytes, source inventories, PR scope snapshots and input hashes are retained locally. Runtime requires Python 3.12 and its standard library, with no Git, network, external worktree or author native evaluator.

```
python3.12 run.py
python3.12 -O run.py
```

Default execution is read-only and compares both saved scientific artifacts. `--write` is explicit author mode. `RESULT.json` inventories every added/removed actual frame pair, its bases, rank, field roles and event versions; it also records every changed multiplicity among otherwise common maps. `MAPS-PROGRAM.json` emits the four literal recipes and their complete expected/actual circuits.

## Exact delta

| New pair | Rank | Actual successor event / role |
| --- | --- | --- |
| 17 -> 720 | 2 | 14477 / 297 |
| 17 -> 782 | 3 | 14807 / 152 |
| 615 -> 207 | 5 | 15477 / 198 |
| 775 -> 207 | 2 | 15478 / 319 |

Each new pair occurs once. Distinct actual MOVE pairs change from 2,942 to 2,940, with 2,936 common pairs, four added pairs and six removed pairs. The six removed pairs are 3->335, 335->720, 335->782, 615->915, 775->915 and 915->127. Counting all changed multiplicities gives exactly `2H1 -3H2 +H3 -H4 +H5`; it is not obtained by counting distinct pairs alone.

## Engine and checks

This package reuses Chris R/Clear1nsight's independent dense arithmetic interpreter from [PR5548](https://github.com/CrocSwap/integer-mult-bounds/pull/5548), exact commit `b038f9d9b5cf0ce92184da909e57a3be476fc812`, unchanged SHA-256 `43fd40847a0853c0ac511d58ce77ef822a5c6dd1b25f662f01cefaa3196a2f7d`. Its dense-column/compiler/first-difference functions execute P, D, X, phase and signed positive/inverse C gates on complete integral real/imaginary vectors with a binary denominator. Neither vendor state interpreter nor vendor tableau is used for matrix comparison. This is credited reuse of that independent arithmetic implementation, not a new independently authored dense engine.

The canonical Clifford compiler and literal chart/recipe descriptions are the byte-pinned PR5545 sources. The new comparison loop streams columns, compares every complex coordinate, checks exact column norm, measures support `2^rank` on every column, records absolute anchors and hashes the complete matrices. Source authentication precedes imports.

For each new map, controls reject a global phase error invisible to signed Pauli tableaux, wrong child sign, wrong ordinary boundary and wrong declared rank. Two source-byte corruptions fail authentication. Normal/optimized agreement is reproducibility of the same implementation.

## Relation to previous review

[PR5548](https://github.com/CrocSwap/integer-mult-bounds/pull/5548) checked the older rank-1/5/6 maps among frames 739, 240 and 127, plus their route composition. None is one of these four added frame pairs. Its repeated-H5 ceiling concerns a different fixed edit family.

[PR5550](https://github.com/CrocSwap/integer-mult-bounds/pull/5550) checked the earlier forward caller, target aliases, ordinary pass count and related target interfaces. It expressly retained the local all-input/all-width ABI and untouched paid-map foundation. Our local endpoint/chart ABI and helper targets remain the predecessor's, so replacement into the same caller is a conditional compositional argument. This four-map audit does not rerun or independently discharge that caller's full source foundation.

The 2,936 common MOVE pairs, other native interfaces, full caller dual, erasure, precision/tape/storage, uniform compiler and analytic recovery remain outside this focused dense audit. The five framework assumptions remain. No independent human or proof-kernel acceptance is claimed.

## Credit and license

Ali Romman supplies PR5544/5545's construction, native interface, caller and price. Chris R/Clear1nsight supplies PR5548's new dense interpreter and prior audit. Retain Gareth Davidson, David Arias, Cinna Davis, Jacob Alan Sussman, zxv, Cao Yifan and all Clifford, native-review, geometry, COPY, precision and analytic source notices. New inventory, word binding and focused application prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0; LICENSE is retained. No public package has been edited by this audit.
