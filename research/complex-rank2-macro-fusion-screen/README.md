# Selected complex rank-two macro-fusion screen

**A source-bound negative screen for direct pair fusion. No new supplier or κ claim.**

## Result

The selected complex trace has 2,412 rank-one child climbs per orientation. A direct pair-to-rank-two macro would be attractive in the recursive cost model: if it preserved the exact operator, replacing two rank-one calls by one rank-two call would multiply that pair's recursive charge by `2^-a`, for the provider saving exponent `a > 0`.

This screen checks the narrowest concrete version of that idea against the pinned selected source. It walks each register's climb history and looks for two successive rank-one climbs whose combined endpoint transition also has an exact rank-two child recipe. Each orientation has 1,441 such rank-one successor links, of which 35 have a matching direct rank-two recipe. **All 35 candidates are interrupted by scalar operations on the same register**: 20 have five such touches, five have two, and ten have one. No candidate can be substituted directly while preserving the recorded scalar schedule.

The forward phase-B witness on `L195` has a genuine exact identity. Its calls at events 12806 and 13402 use the recipes `0→2, rank 1` and `2→252, rank 1`; their 512-by-512 Gaussian-dyadic operator product equals the direct `0→252, rank 2` recipe on **all 512 basis vectors**. The exact operator hashes and the full intervening-window receipt are in [`RESULT.json`](RESULT.json). This confirms the child-map composition, rather than inferring it from matching endpoint frames.

The intervening ADD still prevents a direct replacement. In the forward trace it changes the required output to `L195_out = D x + (1/2) B y`, where `D=BA` and `y=L521`; in the backward trace it also writes `L521_out = y - (1/2) A x`, so the caller consumes the intermediate `A x`. The one-output rank-two recipe supplies `D x` but neither cross-register block nor the intermediate tap. Every basis input has a nonzero missing contribution. Computing the tap separately needs a rank-one-equivalent call: the separated rank-two-plus-rank-one profile costs `2^(1-a)+1 > 2` for `0<a<1`, versus two rank-one calls, before adapter and restoration costs. A multi-output rank-two child that emits the tap would be a changed provider contract; this PR does not posit or price one. The selected κ remains `0.001672660197076918`.

All 100 candidate/add-operand instances still have no existing same-key rank-one call to absorb the moved work. Thus the selected-source direct-fusion route reaches a concrete wall: exact child composition succeeds, but the required observable intermediate makes the available single-output replacement non-improving. This does not rule out changed-basis or multi-output synthesis.

## Task and overlap

Base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The original task is `complex-rank-shape-decoder`; this package narrows it to direct fusion of two rank-one frame climbs into an available rank-two endpoint recipe in the selected complex schedule. It does not satisfy the task's construction or five-percent acceptance gate.

The refreshed overlap query covered 734 open PRs and 2,596 Discussions with complete pagination. It surfaced [PR #3998](https://github.com/CrocSwap/integer-mult-bounds/pull/3998), which removes two scalar ADDs in a staged544 graph; that is a different provider, graph and identity. The closest higher-rank antecedent remains [PR #1836](https://github.com/CrocSwap/integer-mult-bounds/pull/1836) and its follow-up [`complex-heterogeneous-child-interface` audit](../complex-heterogeneous-child-interface/README.md): those study simultaneous unequal-rank climbs, unlike this package's successive same-register pair and its observable intermediate ADD. The [two-invocation stage-pair audit](../../docs/research/stage-pair-audit.md) studies another bit-side graph. This is a scoped complement, not a broad novelty claim. Exact source archive, canonical word and child recipes are pinned; the verifier has no pending-PR dependencies.

## Reproduction

From the repository root:

```sh
python3 scripts/research_package.py --package research/complex-rank2-macro-fusion-screen --check-only
python3.12 scripts/research_package.py --package research/complex-rank2-macro-fusion-screen
```

The registered normal and optimized replays pin the selected trace, canonical word and child recipes; replay climb and scalar-frame legality in both orientations; enumerate direct endpoint-recipe candidates; test same-key call reuse; reconstruct the `L195` candidate window; compare both rank-one operators' product with the direct rank-two operator on all 512 basis columns over `Q(i)`; bind the nonzero ADD tap; and run wrong-rank and source-removal controls. No full supplier replay or new κ is claimed.

## Open next questions

The direct single-output rank-two route is closed for this witness: its child composition is exact, but the ADD requires either the missing `B y` contribution (forward) or the intermediate `A x` tap (backward). The next distinct question belongs to vector/tap synthesis: can a changed-basis multi-output rank-two provider emit both `D x` and the required tap for less than two rank-one calls after all interface and restoration costs? No such provider is present in the pinned source, so this package stops before expanding that construction round. `TASK.json` records the changed-contract question and its gate.

## Credit

Credit Cinna Davis / PR #1836 and Adam Gall's `complex-heterogeneous-child-interface` package for the simultaneous unequal-rank census and reciprocal-encoding classification; credit the selected PR #1094 provider lineage and its pinned source audit. Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
