# Install the borrowed adapters into the complete native word

This package closes the **whole ideal native-word integration and prefix-envelope check** left open by [#4502](https://github.com/CrocSwap/integer-mult-bounds/pull/4502). It supplies a guarded installer, the complete rewritten forward/backward native programs, and fresh whole-word replay against the pinned canonical chart. It adds no new local optimization and claims **no new κ**.

| Complete THREE-base word | Original scalar allowance | Rewritten | Saving | Formal prefix row ℓ₁ | Max coefficient | Max numerator | Max denominator |
|---|---:|---:|---:|---:|---:|---:|---:|
| Forward | 158,120 | 158,020 | 100 | 457 → 457 | 32 → 32 | 32 → 32 | 32 → 32 |
| Backward | 158,168 | 158,068 | 100 | 169 → 169 | 5 → 5 | 21 → 21 | 64 → 64 |

Each orientation is replayed on **all 632 independent persistent inputs plus the original arbitrary owned C input**. All 408 helper fields are restored in logical coordinates and C exits zero. Both paid profiles remain `{1: 2487, 2: 713, 3: 232, 4: 102, 5: 28}`: 3,562 calls, rank mass 5,157. There are no new fields, queries, warps, transport events or adapters. There are two more scalar instructions, despite a lower allowance; counting scalar instructions alone would miss the improvement.

`PATCHES.json` contains eight frozen replacement rules, four per orientation. Each binds its exact source window, original roles, common chart, dyadic matrix and full replacement. `NATIVE.json` is the complete generated word, ready for downstream ideal-native consumers. Unchanged event ranges and their new starting indices are in `RESULT.json.retained_event_segments`; downstream index-based phase references must use this map rather than assume indices stayed fixed.

```sh
python3 -I -O -B research/native-splice-replay/verify.py
python3 scripts/research_package.py --package research/native-splice-replay
```

To regenerate the native artifact at a new path:

```sh
python3 -I -O -B research/native-splice-replay/install.py --output /tmp/rewritten-native.json
```

The installer refuses to overwrite an existing output. The verifier compares the parsed artifact with the regenerated program, rather than testing a platform-sensitive compressed-container hash. Standard-library Python only; tested on Windows. No Linux execution was available.

The retained independent native interpreter and prefix evaluator are authenticated and their exact pure functions extracted from source; their complete top-level modules and external authentication closures are not executed. This replay uses their declared ideal chart/free-warp semantics. Physical phase recipes are retained by exact event identity and mapped indices, **not regenerated**. No rounded recursive induction, all-size compiler, actual memory/tape execution or new global bound is verified here.

## Open next questions

1. Feed the rewritten complete word and mapped event indices into the rounded precision/error induction, including local error injection and suffix amplification. Unchanged global prefix maxima alone do not prove an unchanged rounded budget.
2. Rebind physical phase receipts using the supplied retained-event map, and separately check any downstream generator that hard-codes event indices. The actual non-scalar event contents and order are already identical; receipt consumption has not been regenerated here.

See PROOF.md for the universal sufficient assembly argument, ATTRIBUTION.md for predecessors and overlap limitations, and RESULT.json for complete deterministic receipts. The selected frontier and authoritative MathProof DAG remain unchanged.

The retained canonical file is used as the chart, profile and endpoint reference. Its original cleanup-generation metadata is not rewritten. Downstream users should consume NATIVE.json or the guarded installer; rerunning an old generator from the original canonical cleanup arrays will regenerate the original word.
