# Reuse input validation within one replay plan

At base `721c03822c421b7f7fcbb2598993b947c4d88419`, the planner validates
each declared input occurrence independently. Shared files therefore repeat
the same exact-path check and component `lstat` calls across many packages.
A read-only profile of the complete planner counted 36,576 path-guard calls
for 14,638 distinct paths, including manifest discovery. The guard accounted
for 2.319 seconds of a 4.069-second profiled run. This identifies redundant
work; those instrumented timings are not the benchmark below.

The change retains a set of successfully validated **declared input names**
inside `plan_details`. A name enters it only after both the existing filesystem
guard and exact HEAD-or-changed-path check succeed. Non-string values still
reach the original canonical-path error. No validation state survives a call.
Manifest discovery, reading, hashing, HEAD acquisition and all selection causes
are unchanged. In particular, skipping a repeated validation does not skip a
consumer or remove a repeated input from the manifest's authenticated bytes.

The existing contract requires a stable checkout during planning. For a fixed
root, tracked-path set and filesystem, successful repeated checks have the same
result, so replacing them with membership checks preserves the complete plan.
This is not an atomic filesystem snapshot. A later invocation must check again,
including after a file becomes a symlink or junction, HEAD changes, a deleted
input leaves the current diff, or a manifest changes its spelling.
The set retains O(U) distinct input names for that call; peak memory was not
benchmarked.

## Measurement

The existing benchmark by Ali Romman compares complete `plan_details` results,
not only package counts. It ran five alternating pairs per case on the same
3,678-manifest checkout. All 40 complete results matched their corresponding
baseline, including ordering, causes and manifest SHA256 values.

| Changed paths | Selected packages | Baseline median | Candidate median | Ratio |
| --- | ---: | ---: | ---: | ---: |
| All tracked paths | 3,678 | 1.287 s | 0.733 s | 1.757x |
| Shared runner | 3,678 | 1.203 s | 0.640 s | 1.880x |
| One package file | 22 | 1.176 s | 0.638 s | 1.844x |
| README.md | 1 | 1.204 s | 0.746 s | 1.615x |

[Raw samples, environment, source hashes and full-result digests](replay-planner-input-reuse-benchmark.json)
bind this evidence. The benchmark was run before committing the implementation:
its `head` identifies the checkout baseline; `source_sha256.after` identifies
the exact candidate bytes. The latter are committed in
`585e1404f` and remain unchanged in the documentation commit.

These are local macOS 27 arm64 / CPython 3.14.6 measurements with warm filesystem
caches, repeated calls in one process, and other work on the host. The raw samples
include cold/noisy outliers. No fresh-process, cold-cache, Linux, Windows or
whole-CI speedup is claimed. Reproduce with:

```sh
python3 -B scripts/benchmark_research_plan.py \
  --baseline 721c03822c421b7f7fcbb2598993b947c4d88419 --samples 5
```

## Validation

Six new tests use temporary real Git repositories and independently constructed
expected plans. They check shared-input validation counts without losing either
consumer, every cause or either hash; fresh permission and symlink rejection;
HEAD/deletion/diff freshness; manifest reload and exact-case/canonical spelling;
and non-string diagnostics, including unhashable values. The unmodified baseline
fails the redundant-validation test. Separate injected persistent-cache and
skipped-tracking-guard controls are rejected by the freshness/spelling tests.

The following nine modules pass normally and with `-O`, under `-B -W error`:
92 tests per mode on both CPython 3.14.6 and 3.12.2. Existing platform/tool
skips total eight per mode on 3.14 and four per mode on 3.12.

```sh
for test in plan_input_reuse input_paths symlink_inputs sparse_planning \
            plan_explanations replay_selection matrix_batches git_root_binding onboarding
do
  python3 -B -W error "tests/test_research_${test}.py"
  python3 -O -B -W error "tests/test_research_${test}.py"
done
```

The committed shared runner and new test were also exported with `git archive`
into a fresh Git-free tree, made read-only, and run normally and optimized.
All six tests pass in each mode and exported source hashes remain unchanged.
The tests create their own temporary Git fixtures outside that read-only tree.
This shared-code change has no registered research package: package-specific
source-history and package-export hooks are not applicable.

Native Windows junction execution, hosted CI, complete historical replay and
scientific admission were not performed. Existing junction and sparse guards
are retained; no selected certificate or frozen source is modified.

## Scope, attribution and open next questions

This refines the `replay-runtime` card, seed
`48bb2ae90f98183ae8b15a7200992341`, on priority revision 8.
The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/6077)
records the claim. The selected PR6030 baseline passed source-binding checks;
this work establishes no new mathematical bound or supplier admission.

Credit Douglas Colkitt for the registered runner, Ali Romman for the retained
complete-plan benchmark, and the earlier exact-path, junction and sparse-input
guards. Per-invocation reuse is standard; the contribution is its bounded
application and measured coverage-preserving effect in this planner.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
Independent human review is not claimed.

The next useful check is to run the same exact-output benchmark and native
junction regressions on a Windows checkout, reporting source hashes and the
complete receipts. That can establish host-specific behavior; a Windows host
is required. No broader cache or additional optimization is justified by this
result alone. Concurrent filesystem mutation remains outside the existing
stable-checkout contract.
