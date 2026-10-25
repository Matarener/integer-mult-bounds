# Five cross-call three-role cycles improve the selected T16 packing

**Conditional packing result: κ = 0.001673623729715781.** On the unchanged selected PR1094 word and suppliers, this exact owner map improves by `4.191059243×10⁻⁹` over the open [PR #3338](https://github.com/CrocSwap/integer-mult-bounds/pull/3338), and by `5.238820765×10⁻⁹` over its PR3308 predecessor. The selected record is unchanged. This is a finite packing improvement, not a new multiplication theorem or an optimality claim.

## What changed

Starting from the pinned PR3308 map, the witness applies five whole-role cycles across three distinct calls each. Every cycle rotates widths `(5,4,4)` through groups with idle slacks `(2,1,3)`, producing `(3,0,3)`. The exact windows, aggregate capacities, physical-family occupancy and offsets are checked at each step. The roles’ times, helper widths, selected word and both suppliers stay fixed.

The first cycle reaches the same exact κ as PR #3338’s two-role swap. Four more legal cycles then raise κ to `1673623729715781/10^18`. The final idle remainder profile is `{1:2387, 2:3, 3:115, 7:2, 16:2, 48:4880}`. The exact global profile and each move are recorded in [RESULT.json](RESULT.json) and [CYCLES.json](CYCLES.json).

The strict T16 global replay passes with 10,008 actual charts and controls `69/12/6/15`. The independent owner audit retains all 11 controls; both exact moment engines and the independent pricing sweep agree, with the complex supplier still binding and the bit supplier unchanged. The conservative κ is `0.001673623726862990`.

For this fixed word, the exact packing ceiling remains `κ < 1690054109089/1001690054109089 ≈ 0.001687202645325402`. The witness realizes `99.1951817%` of that ceiling and `6.6256563%` of the selected-to-ceiling gap. This confirms that additional packing alone cannot reach κ>0.01; that target requires a changed word or cost structure.

The current public overlap check found PR #3338 as the nearest result: it reports the first cycle’s κ and covers a two-role swap. The additional four cycles and resulting higher exact price are the contribution here. The local cached overlap report is stale and is not a novelty certificate; no claim of global novelty is made.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/t16-cross-call-cycle-packing-improvement --check-only
python3.12 scripts/research_package.py --package research/t16-cross-call-cycle-packing-improvement
```

The registered verifier reconstructs the cycles from the pinned PR3308 owner map, regenerates `OWNERS`, `PLAN` and `SPEC`, performs the strict global replay, then runs the independent owner/pricing check and the fixed-word ceiling calculation. It does not run OR-Tools or alter any frozen source.

## Open next questions

The structured questions and first steps are in [TASK.json](TASK.json). The final map’s other cross-call cycles and longer exchanges remain unsearched. Reaching κ>0.01 also requires a new fully charged word or interface: the fixed-word ceiling is far below that target.

## Credit

The source map and selected word retain their original PR1094, PR3308 and supplier attribution. PR #3338’s two-role result is credited to its author and used only as the nearest public comparison. The five new cycle witnesses, exact replay package and verifier were prepared with substantial OpenAI Codex assistance at the user’s direction. New package material is Apache-2.0.
