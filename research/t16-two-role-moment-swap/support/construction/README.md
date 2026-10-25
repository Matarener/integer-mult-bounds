# Candidate 001 independent construction gate

Worker 4 independently ran the unchanged strict T16 construction verifier on worker 1's two-role-swap-001 map. All eleven stages and controls 69/12/6/15 passed. The source-bound checker then authenticated the raw results and rejected six source, log, data, chart and missing-control mutations.

This closes the previously unrun full placement/window/controller admission for this map. It does not replace worker 3's exact-score gate or worker 5's complete-invoice/proof-scope review. No selected-frontier change or unconditional multiplication theorem follows.

## Exact inputs

`ADMISSION.json` binds all three candidate data hashes, the actual strict assembly and invoice hashes, 43 canonical input hashes, all seven selected provider artifacts, the original 179-file source inventory with only three data files overlaid, and all eleven raw stage logs. `DATA-FREEZE.json` records the independently derived 10,008 chart count before SPEC construction. The candidate has 69,120 role windows and 144 whole invocations.

The actual stock remains 14,826, comprising 14,336 data/owner families, 480 helpers, eight centres and two coefficient fields. The independent T16 checker conservatively reserves 504 helpers and reports 14,850. Both produce the same stock bit length and row coefficient 16,469. Prefix 397 remains charged at 512. No cost was removed.

Source base is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`. `SOURCES-PR3308.json` preserves the exact predecessor inventory from PR3308 head `8bc0555b484bf4aec4b91c680763d930d6754974`. Runtime checks use committed canonical files, not that foreign Git object. Native local supplier evidence is hash-bound reuse from the selected archive, not a new cold native replay.

## Reproduce

First run the candidate owner's complete package replay to create `source/`, `local/` and `strict/` in an external output directory. The source must come from the unchanged canonical `research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz`, with only candidate OWNERS/PLAN/SPEC overlaid. Its strict invocation is:

```sh
python3.12 -E -S -B OUTPUT/source/verify_t16.py \
  --main REPO --local OUTPUT/local --work OUTPUT/strict
```

Then run these checks from this bundle directory. `DATA` names the identical frozen three-file data directory. `SCRATCH` is an existing external session-owned directory.

```sh
python3.12 -Werror -B check_strict_bundle.py \
  --repo REPO --pins SOURCES-PR3308.json \
  --source OUTPUT/source --data DATA --local OUTPUT/local \
  --strict OUTPUT/strict --output fresh-admission.json
python3.12 -Werror -B test_strict_bundle.py \
  --repo REPO --pins SOURCES-PR3308.json \
  --source OUTPUT/source --data DATA --strict OUTPUT/strict \
  --scratch SCRATCH --output fresh-controls.json
ruff check --select E4,E7,E9,F,B check_strict_bundle.py test_strict_bundle.py
```

The original run used CPython 3.12.15 on Linux. Raw logs preserve its actual absolute paths. New environment-dependent logs and receipt hashes need not match those old bytes. Every new run must instead bind its own data, source and complete output hash chain. Do not silently attach this receipt to another map.

## Implementation limits

The checker reads bounded local artifacts and does not execute supplier code. Python allocates managed objects, so a strict no-allocation rule cannot hold. File and decoded JSON reads are capped at 64 MiB, the source inventory at 180 files, and source traversal at 320 paths. All functions are at most 59 lines. The six mutation fixtures use disposable copies and remove them on exit. The original frozen verifiers are unchanged, including their existing assertions and internal implementation limits.

## Open next questions

Worker 2 may produce a stronger capacity-48 evacuation map. Before composing or replacing this candidate, freeze its exact three data files and rerun construction, score and full-invoice gates on those same bytes. Final publication source closure and exact-head hosted checks remain required.

## Credit

Independent source-bound construction check by Nick Petalas. The strict verifier, controllers, native local supplier and geometry retain the original attribution in the unchanged canonical source archive, including Hao Yan's T16 controller and the selected Rohan Arun/Jeremy Kothe packing lineage. Worker 1 supplied the new swap. Workers 3 and 5 own the separate score and invoice reviews. New checker source is Apache-2.0. No independent human review is claimed.
