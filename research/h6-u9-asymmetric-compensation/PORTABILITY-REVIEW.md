# C04 portable loader review

Status: PASS for the inspected loader and final adaptation map, after correction of the manually executed oracle path. Heavy scientific stages remain the root's execution obligation. No package or frozen source was edited by this reviewer.

Inspected SHA256 values:

- verify.py: a07bbbc84d4310bbd7bc4d8b40b27a309fbdfabd4ea76516376601818318f732
- ADAPTATIONS.json: 147a2cad963185f51eb8e0881470931b18f181cfe8df815480d9b59dc8ae8ab0
- FROZEN-SHA256.json: a6393759e393cbf55500e04188601c0a799e2390b2cd3f844542ec3851744c22

- controls.py: ee5f9da59b570521e3c765e331bc2037a7c41f54303c017f0f0ab07a939c2def
- VERIFY.json: c26edd3102ce1eb9fc1a2f72a88fabb889aa5c8ecd335f399913f24cf6b72d36

## Source binding and assertion preservation

The installed SourceFileLoader.get_code replacement routes every source module under the package root through Portable.code. That function reads the source bytes, authenticates those same bytes, applies the enumerated unique substitutions, and compiles with dont_inherit=True and optimize=0. It never asks the original loader to select a package bytecode cache. SourceFileLoader.exec_module injects the same PORTABLE instance into nested modules before execution. Normal imports such as e8_cubed and explicit nested spec loaders therefore receive the same protection. Unregistered package source fails authentication. Every registered frozen file is checked both before and after the stage.

A concrete gap in the initial map was found and fixed by the root: legacy-budget/optimistic_budget.py directly execs the interval oracle, bypassing SourceFileLoader. The final map uses PORTABLE.authenticate for its raw oracle/receipt reads and PORTABLE.code(REPO/ORACLE) for the executed oracle. This now authenticates and registers the manually executed source, while retaining all historical assertions. The scientific oracle bytes and source-hash fields are unchanged.

## Adaptation scope and receipt comparison

The map changes only source location, immutable-source loading, output handling, and retained assertion compilation. It does not change factors, matrices, arithmetic, ranks, coefficients, chronology, controls, or precision equations. Replacing historical writes by comparisons avoids overwriting fixed evidence. The composition write option is explicitly rejected. Local absolute paths are mapped to the preserved source tree and inherited run inputs. Dictionary keys representing source paths receive the same normalization during receipt comparison.

Every mathematical JSON field is compared recursively. The only excluded fields are RESULT elapsed_seconds/environment and frozen replay elapsed_seconds/optimization_flag. These are runtime observations, not numerical claims. Canonical recipe outputs are compared byte-for-byte for both new and baseline recipes, including their serialization and phase witnesses. Required receipt sets must match exactly at the end of each stage. Path normalization does not alter scalar values or omit scientific fields.

The six declared stages cover:

- factor: full frozen asymmetric result, including original assertions and controls;
- native: actual recipe generation, all new recipe bytes and complete native result;
- replay: all frozen new/baseline operator checks and replay controls;
- adapters: baseline recipe regeneration and complete semantic/Boolean adapter invoice;
- precision: native coefficients, full label census and finite exact-grid/range ledger;
- composition: frozen all-column chronological compensation composition result.

This restores fresh execution of the generation controls and chain checks when all six stages pass; replay alone would not establish that coverage. Execution receipts identify loaded source files, now including the direct interval oracle. Package-level checks should also bind verify.py and ADAPTATIONS.json; FROZEN-SHA256 intentionally lists the preserved inputs rather than authenticating its own verifier.

## Meaningful lightweight controls performed

All controls ran with an optimized Python caller and temporary fixtures, without editing package files:

1. A syntactically valid matching-timestamp .pyc was deliberately made to execute a cached replacement. Ordinary import accepted it before loader installation. A nested import through Portable then executed the authenticated source instead.
2. That source contained an always-failing historical assert. It still raised the named AssertionError with the -O caller, proving optimize=0 reaches nested source execution.
3. Modifying an authenticated child source after the initial scan was rejected at load time with the source-hash error.
4. Changing rank_mass_change, the common fractional grid, total operator coverage, or baseline recipe coverage in otherwise valid receipts was rejected by the complete JSON comparison.
5. Adding one whitespace byte to new recipe serialization was rejected by the byte comparison.
6. Importing the actual revised legacy-budget module, without running its expensive main, registered precisely the legacy module and its interval oracle. The executed oracle's SHA256 matched the frozen entry.

No remaining loader defect was found in the inspected revision. These tests establish source-binding and comparison behavior; they do not replace the root's normal/optimized registered mathematical validation, portable export replay, or exact-head hosted checks.

## Final registered controls and metadata

The root added controls.py and registered it in normal and optimized modes. Source review confirms its rejection helper raises unexpected acceptance outside the caught ValueError path; it tests modified source, mathematical receipt and recipe bytes, missing coverage, and acceptance of the explicitly ignored duration observation. Its temporary fixture poisons matching caches for the real physical compiler and its nested Clifford vendor, then exercises the retained Op.then dimension assertion and exact nested execution set. These are meaningful controls of the actual wrapper boundary. The root reports optimized controls and metadata validation passing; this reviewer did not repeat those runs.

VERIFY.json registers all six scientific stages under -I -O -B with the frozen code forced to optimize=0, plus controls under -I -B and -I -O -B. The README accurately distinguishes generator/replay controls, arbitrary complex operator scope, logical FULL restoration, standalone exact precision, and excluded finite-tape/approximate-child/joint-supplier claims. Source acquisition and export instructions match the inspected closure. The registered full stage executions and hosted checks remain independently reported root evidence.
# C04 launcher compatibility follow-up

Status: PASS for the bounded delta reviewed after CI run39235715551. This is a source/evidence review of the cache-directory fix and timeout allocation, not a new mathematical replay or a claim that the amended head has completed hosted CI.

The only controls.py change is `cache.parent.mkdir(exist_ok=True)` to `cache.parent.mkdir(parents=True, exist_ok=True)`. The repository's actual `run_python_replay` inserts `-X pycache_prefix=<fresh temporary root>`, so `cache_from_source` returns a nested path whose parent ancestors do not yet exist. The captured CI failure is exactly this missing-directory error. Creating the missing ancestors preserves the matching-cache poison construction, nested authenticated compiler loading and retained assertion test; it removes no control and changes no mathematical code.

VERIFY.json changes only time limits: factor120 to60 seconds, native480 to600, and adapters180 to120. Other stages and both controls retain their commands, coverage labels and timeouts. The sum is unchanged at1140 seconds. The allocation responds to observed hosted execution: native437.571527273 seconds, frozen replay75.16050586999995 seconds, adapters approximately55 seconds; it does not claim a guaranteed runtime bound.

## Inspected hashes

- controls.py: acc3b6cab64231a9b5d5cf07370d32784cdba2b38014bc57a1d99375fe642c88
- VERIFY.json: 3a9a675da69ad73298f5ff1b7af8fde73a9e99d9fac0ccf0389f76d4b52e2961
- verify.py, unchanged: a07bbbc84d4310bbd7bc4d8b40b27a309fbdfabd4ea76516376601818318f732
- ADAPTATIONS.json, unchanged: 147a2cad963185f51eb8e0881470931b18f181cfe8df815480d9b59dc8ae8ab0
- FROZEN-SHA256.json, unchanged: a6393759e393cbf55500e04188601c0a799e2390b2cd3f844542ec3851744c22

## Evidence inspected

The captured `publication/C04-CI-FAILED.log` (SHA256 b8a766bd1e8a94d46405542482f9ac38d4837aed96d24216dbe92dfef2cbe6c4) contains PASS_PORTABLE_C04 for factor, native, replay, adapters, precision and composition, followed by FileNotFoundError in controls.py at the former mkdir call. The CI snapshot identifies the pre-fix head as de2ba3f4558d66cf0909712e7832a1d5b9aa037e. Those six successful mathematical stages remain evidence for their unchanged scientific bytes; the overall old CI run failed at control setup.

`C04-LAUNCHER-FIX.log` (SHA256 1ccd55df88518e934370093ffe4123013a93c2caab8297e7581b429888d6682a) contains both normal and optimized PASS_PORTABLE_SOURCE_RECEIPT_CACHE_AND_ASSERTION_CONTROLS markers and PASS_ACTUAL_REGISTERED_LAUNCHER_CONTROLS_NORMAL_AND_OPTIMIZED. This is the root's retained actual-launcher rerun evidence, independently inspected here; no heavy jobs were repeated by this reviewer.

No factors, recipes, source bindings, receipt comparisons, assertions, precision equations, invoice claims or coverage domains changed. The exact finite proof and its existing exclusions remain as reviewed. The root retains responsibility for amended-head publication and the subsequent automatic hosted CI result.
