# Cyclic H6 readers and paid partial-centre visits

This package gives exact logical H6 subfamily circuits, a complete disjoint root-product tiling with its expensive residual completion, and two partial-frame replacements for eight existing Pauli centres. It exposes two cost tradeoffs: fewer scalar operations can worsen the recursive rank profile, and cheaper private copies can require more source, target and helper visits.

All ordinary source, target and helper inputs are arbitrary. The checked words restore ordinary helper **logical values at declared final frames**. Helpers move from ZERO to FULL; raw physical return to their entrance frames is not proved. Binary frame incidences, exact scalar operators, private-stream contracts and physical compiler admission are distinct obligations.

For `r=2,...,7`, `N=2r`, mutable cyclic readers cost `N(54r-1)` forward and `N(54r+2)` inverse-transpose component primitives, compared with `N(72r-37)` and `N(72r-34)` for the static predecessor. Real and imaginary components are charged separately. Both pay rank mass `83N`. The mutable word saves `18N(r-2)` component primitives, but its rank-profile pressure is strictly worse for `r=3,...,7` at equal stock and arity, for every exponent `0<b<1`. A written concavity proof establishes that comparison; finite exact intervals corroborate it.

The 4,800 disjoint six-port modules cover all 28,800 root-product ports and verify all 172,800 within-module coefficients and address parities. They handle 115,200 nonzero compensation entries. The residual remains 480,222,720 ordered entries under the inherited full-H6 pairing census. A specified residual edge-reader completion saves 1,209,600 scalar component primitives against the all-edge word, but its complete `.002` moment still exceeds one. The full billion-event stream is counted and described, not materialized or executed.

The selected Pauli group supports 5,760 signed ports and has support span `U` of dimension 15 with a two-dimensional radical `W`. Its private returns save 16 ranks at ZERO or 32 at W. Fresh source/target visits outweigh those savings. The additional checked refinement inserts these visits into the actual r3 tiling: supported sources visit U after their rank-3 arc; radical delivery requires lifting the relevant cyclic readers and targets to `arc+W`. Every added transition is charged. Individual feature supports span the same U, so simply shrinking one of the eight gather frames does not help. The paid refinements worsen the fixed-profile comparison at beta = .002, .003 and .005, for all admissible odd arities L >= 3; the L = 1 capped bill is not claimed.

[Cyclic proof](cyclic/PROOF-CYCLIC.md) and [Pauli proof](pauli/PROOF.md) give the assumptions, operators, complete profiles and exact covered domains. Complete deterministic receipts and the separate mathematical audit accompany the checkers. The rank/Smith theorems already published in [PR3649](https://github.com/CrocSwap/integer-mult-bounds/pull/3649) and [PR3655](https://github.com/CrocSwap/integer-mult-bounds/pull/3655) are outside this contribution.

## Reproduction

Run the registered standard-library Python 3.12 package from the repository root:

```
python3.12 scripts/research_package.py --package research/h6-partial-frame-networks
```

The same commands run directly from a Git-free export, with an absolute package path:

```
python3.12 -I -O -B /absolute/export/research/h6-partial-frame-networks/verify.py --stage cyclic
python3.12 -I -O -B /absolute/export/research/h6-partial-frame-networks/verify.py --stage pauli
python3.12 -I -O -B /absolute/export/research/h6-partial-frame-networks/verify.py --stage independent
python3.12 -I -B /absolute/export/research/h6-partial-frame-networks/controls.py --package /absolute/export/research/h6-partial-frame-networks
```

 Each stage writes temporary replay files outside the package, authenticates the executed source buffers and compares every field of the regenerated typed JSON receipt. Gzip transport bytes do not determine mathematical equality. The package-local source inventories and `SOURCES.json` retain original Git pins and unpublished source bytes; no private workspace is required at runtime.

## Scope and limits

The cyclic operators are exhaustive finite ordinary-column checks on the stated r2..7 families; the tiled geometry exhausts 2,400 binary frame cases and 4,800 signed modules. The Pauli full-support factor identity and schedule are written proofs supported by finite geometry and arbitrary-input diagnostic operators. The static/mutable comparison is an all-exponent written argument for the fixed profiles. These are not formal-kernel proofs.

Private work uses the inherited cleared COPY/descent/scatter/ERASE interface. The full K factor and full-H6 support counts remain explicitly inherited pinned evidence. Source/target frame representatives, Clifford phases, raw physical helper return, coefficient temporary states, rounded precision, approximate children, physical banks, owner allocation, tape/controller costs and all-size transfer remain open. No complete favorable H6 supplier, compatible BIT supplier, new kappa, selected-frontier change or unrestricted lower bound is claimed.

## Open next questions

Can a full dynamic incidence network replace the large residual edge bank? A useful first step is one complete overlap-aware source/helper/target itinerary with its whole stock and rank histogram; the present disjoint modules do not provide it.

Can another factor network share enough partial-centre visits to improve the complete moment? Start with actual support spans, target-cap inclusions and a paid chronology. The present comparison covers only the selected eight-centre group and the specified tiling.

Can a complete logical word receive physical and rounded recursive admission? Bind actual frame and phase recipes first, then price raw returns, coefficient temporaries, numerical error, storage and access. [TASK.json](TASK.json) records these questions and their blockers.

## Sources and credit

Scientific inputs are pinned to `20ecf2891d80b5acf18d980b2164fb44ea7faa90`; repository guidance is pinned to `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority 7. Credit Dominik Scholz / PR606 for the H6 geometry, DreamingOfClouds for the H6/Walsh proposal, and the PR1830 compensation/encoder audit with its retained predecessor lineage. Original unpublished C03 scripts, receipts and their exact adaptations are identified in the source inventories. Historical notes retain their original limits and are not fresh acceptance of unrelated claims.

Ross Richardson, with substantial OpenAI Codex assistance, including separate AI mathematical review contexts. That review is not independent human or formal-kernel acceptance. Apache-2.0; the original [Niemeier source notice](notices/niemeier-NOTICE) retains its geometry, Clifford-frame, common-frame and supplier ancestry.
