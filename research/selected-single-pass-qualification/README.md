# Single-pass complete P104 qualification

This opt-in runner executes both unchanged qualification entry points from [PR #5757](https://github.com/CrocSwap/integer-mult-bounds/pull/5757), sharing their duplicate complete source execution within one fresh process. It retains the complete original RESULT/CROSS checks, all original adapter and proof-omission controls, every actual input and both full literal interpreters. No persistent acceptance cache is used. It follows [PR #5816's Linux qualification](https://github.com/CrocSwap/integer-mult-bounds/pull/5816).

The coverage argument and its explicit process-isolation limit are in [PROOF.md](PROOF.md). [COVERAGE-GATE.json](COVERAGE-GATE.json) records the pre-construction decision. The small fixture uses the actual adapter and both retained literal interpreters: three inputs, 1,536 amplitudes each, complete equal receipts, and thirteen exact-predicate stage/contamination/exception controls. Full measurements and qualification status are recorded separately; no unmeasured performance claim follows from the fixture.

## Initial Linux comparison

One complete fresh-process baseline/candidate pair on Ubuntu 24.04.5 LTS, Linux x86_64, CPython 3.12.3, Intel Core i7-4790:

| Scope | Wall seconds | CPU seconds |
| --- | ---: | ---: |
| Original verify plus original cross | 405.86 | 403.68 |
| Single-pass complete qualification | 268.93 | 268.56 |
| Saved | 136.93 (33.74%) | 135.12 (33.47%) |

All complete scientific outputs and original receipts agree. This measures the **whole two-command qualification bill**, including the independent literal audit, rather than just the accelerated source replay timed in PR #5816. Peak kernel RSS increases from the old pair's maximum 514.38 MiB to 518.56 MiB; the candidate sampled aggregate process-group peak is 514.86 MiB. Sampling can miss short peaks. One pair, shared host load and unflushed OS caches do not establish statistical confidence or universal performance. No slow sample is discarded.

## Reproduce

Python 3.12, standard library:

```sh
python3 -B scripts/research_package.py --package research/selected-single-pass-qualification
```

The first two commands run small controls and source-custody rejections; the third is a **fresh full scientific qualification**, not a recorded-evidence check. It should emit the original scientific output, `PASS_COMPLETE_SELECTED_QUADRATIC_REPLAY`, `PASS_ALL_SELECTED_LITERAL_STATES` and `PASS_SINGLE_PASS_COMPLETE_QUALIFICATION`. It can take several minutes. Both literal interpreters check every one of 17,651 distinct actual states and all 9,037,312 amplitude entries per interpreter, including zeros and denominators.

The exact 54-file source closure is authenticated and materialized temporarily from the unchanged official export, read-only and Git-free. No network, Git, third-party Python dependency, source rewrite or expected-receipt update is required. Original standalone entry points remain in the retained archive. The original pending PR head is not needed as a cached Git object at runtime.

To reproduce the bounded initial performance comparison on Linux with `/usr/bin/python3.12`, GNU `/usr/bin/time` and `/proc`, use a new work directory:

```sh
python3 -B research/selected-single-pass-qualification/benchmark.py pair --workdir /tmp/single-pass-fresh
python3 -B research/selected-single-pass-qualification/benchmark.py optimized --workdir /tmp/single-pass-fresh
```

The first phase runs the complete original verify, complete original cross and combined candidate serially: 600 seconds per command, 900 seconds aggregate, 1 GiB sampled process-group RSS, bounded output and no retries. Complete scientific output equivalence and at least 15% wall and CPU savings are required before the separately gated optimized phase. That phase raises only the declared aggregate ceiling to 1,500 seconds; per-command and memory caps remain unchanged. All prior receipts still count toward the total. Every run records wall/user/system time, kernel peak RSS, sampled group RSS, full stdout/stderr and source integrity. A shared host, unflushed OS caches and one comparison pair limit timing claims. Normal and optimized candidate outputs must agree byte-for-byte.

## Qualification evidence

All five guarded scientific commands pass in **1,212.21 seconds total** under the staged shared limits. The first pair costs 674.79 seconds, below its 900-second gate. The complete optimized candidate takes **268.03 seconds**. A separately exported, read-only, Git-free implementation runs with `-I -O -B`, empty PATH and an explicit package import root in **269.39 seconds**. Normal, optimized and sealed stdout is byte-identical; all 18 exported files retain bytes and modes. The extra mode/export qualifications are not added to either arm of the one-pair speed claim.

[VALIDATION.json](VALIDATION.json), [BENCHMARK.json](BENCHMARK.json), [SEALED-VALIDATION.json](SEALED-VALIDATION.json) and `evidence/` preserve the complete results. The source/export corruption controls pass normally and under optimization. Public resource receipts remove only the local absolute script path and retain the original local receipt hash; all original receipts remain in the execution checkpoint. Scientific stdout is not filtered.

The sealed export is implementation commit `47e6c56c687ced98a854f7d1e723b7a04db3f15b`; later additions are report/evidence metadata. Final committed bytes/modes and hosted CI are checked separately. Full-history ancestry preflight is unavailable in the shallow checkout; immediate declared source-pin ancestry is checked without claiming a complete source-history audit.

## Scope and limits

Source: exact PR #5757 head `53006fe6031dab5c23d5b7d1cf6a92f411a04a68`. Canonical main at entry: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8. [Scoped claim](https://github.com/CrocSwap/integer-mult-bounds/pull/5757#issuecomment-6431932553). Targeted source/PR overlap was checked; unpublished work and exhaustive Discussion coverage are not established. This is a different optimization from the retained engine/signature cache and the already-published E7 bit-lane optimization.

This shares the source execution and its trace within a process. It does not preserve an independent second cold source execution, claim an independent human audit or proof-kernel acceptance, certify a changed word, or resolve the inherited framework assumptions. It changes verification work only. Conditional kappa and selected metadata are unchanged; the kappa campaign, source/literature monitors, workers and automations remain paused.

The branch carries Ali Romman's exact [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) test repair with original authorship and provenance to avoid the known revision-8 routing-test failure. That dependency changes no research artifact.

## Open next questions

- Can the same source-execution sharing apply to a changed reviewed word? First authenticate its closure and map its two entry points, trace and original receipts; stop if any obligation or state-isolation premise differs. This submission makes no successor transfer.
- After this orchestration change, is literal arithmetic or amplitude reconstruction the measured remaining bottleneck? Profile one full qualified run before proposing a new cache. Persistent reuse would need a separate complete dependency/invalidation contract; a cached PASS is insufficient.
- Does performance hold on another host? Repeat the bounded exact comparison and retain every sample and memory result. One pair does not establish a universal speedup.

See [TASK.json](TASK.json) for the frozen task card and structured scope, and [SOURCES.json](SOURCES.json) for exact retained-source pins.

## Credit

Credit Ali Romman for [PR #5704](https://github.com/CrocSwap/integer-mult-bounds/pull/5704), [PR #5757](https://github.com/CrocSwap/integer-mult-bounds/pull/5757), original controls and the retained P104/native/controller/compiler/classical stabilizer sources. The archive and NOTICE preserve all predecessor attribution. New observer/handoff, review, controls and measurements were prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Publication, hosted CI and mathematical acceptance are separate.
