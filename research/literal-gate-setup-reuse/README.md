# Exact literal-gate setup reuse after PR #5818

This opt-in verification runner reduces the complete frozen [PR #5818](https://github.com/CrocSwap/integer-mult-bounds/pull/5818) qualification bill by reusing exact P-gate address tables and D-gate phase tables inside its dense literal interpreter. Both literal interpreters still execute every actual state and compare every amplitude, including zeros, absolute phases and denominators. All original source/native/caller/invoice/compiler/outer, adapter, omission and complete RESULT/CROSS checks remain active. No state vector or accepted result is cached.

The initial fresh-process baseline/prototype pair saves **26.61% wall time and 26.57% CPU time**. The later self-contained packaged normal command also passes: **209.93 seconds wall / 209.20 CPU**, versus the same baseline's **283.32 / 282.47**, saving **25.91% wall / 25.94% CPU**. These are source/host-bound measurements, exceeding the user's 15% gate. One baseline with two candidate observations is not two independent pairs, a median or a universal speedup.

## Profile before construction

[PROFILE.json](PROFILE.json) records a complete profiled run. It rejects the original whole-circuit tableau-cache nomination: 17,651 actual circuit keys are all distinct, so there are zero repeat hits. Tableau setup costs only 7.222 seconds, insufficient for 15% whole-run savings even if eliminated. Dense literal work costs 117.684 seconds; repeated pure P/D gate setup is the bounded alternative. Whole-function nested timings overlap and profiling is excluded from the speed comparison.

The pre-construction [coverage gate](COVERAGE-GATE.json) and [PROOF.md](PROOF.md) identify every changed statement and retained obligation. The complete original dense-method source and prepared AST are pinned. Only two scalar helper calls are replaced by indexed tables computed with that interpreter's own unchanged helpers. The second sparse interpreter and quadratic engine share no new setup cache with it. All gate chronology, signed Gaussian arithmetic, denominator/divisibility checks and fresh vector allocation remain unchanged.

## Measurements and retained coverage

Ubuntu 24.04.5 LTS, Linux x86_64, CPython 3.12.3, Intel Core i7-4790; serial fresh processes and no retries:

| Complete qualification | Wall seconds | CPU seconds | Kernel peak MiB |
| --- | ---: | ---: | ---: |
| PR #5818 baseline | 283.32 | 282.47 | 519.03 |
| Initial setup prototype | 207.92 | 207.42 | 521.11 |
| Self-contained packaged normal | 209.93 | 209.20 | 522.85 |

The initial candidate reuses **61,214** setup tables with **23,983** misses and at most **512** resident immutable tables. Each has at most 512 integer entries; complete-key storage is additional. No amplitude or state answer is stored. The complete scientific stdout is byte-identical, SHA256 `c796be009d692546eab74e3ac084ec6badf45245841d81f101c2a164c0a6eaba`.

Every full run checks **17,651 actual inputs** against both literal implementations, **9,037,312 amplitude entries per interpreter**, original complete receipts and trace SHA256 `73ac04db73d83151efb474925d48298664cc7490d31bdec7a70dcf79b448f481`. The unchanged original 1,522-state/22,700-amplitude adapter corpus, cache/type/mutation/capacity/eviction tests, three proof-omission controls and explicit optimized width guard remain. New finite conformance compares the original dense method to its derived method on another 1,522 complete cases / 22,700 amplitudes, including four width-nine cases, with 23 controls. Deliberately corrupt P addresses and D absolute phases are detected; mutable outputs remain fresh. All 13 predecessor orchestration and seven predecessor custody controls remain, plus top-level bundle-byte corruption rejection before imports.

[BENCHMARK.json](BENCHMARK.json), [VALIDATION.json](VALIDATION.json) and `evidence/` preserve complete stdout, stderr, resource receipts and failures/limitations. Public resource receipts remove only the local absolute script path and record the original local receipt hash. Method wrapper snapshots are documentary text from the local round, not standalone entry points. The normal/optimized/sealed qualification observations are distinct from the first-pair speed comparison. Shared host load, sequential order and unflushed OS caches limit timing conclusions; no slow sample is discarded. Kernel and sampled group RSS are different measurements, and sampling can miss short peaks.

## Reproduce a fresh full qualification

Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/literal-gate-setup-reuse
```

The first two commands run finite setup and inherited controls. The third runs a **fresh full scientific qualification**, typically about 3.5 minutes on this host. It emits the original `PASS_COMPLETE_SELECTED_QUADRATIC_REPLAY`, `PASS_ALL_SELECTED_LITERAL_STATES` and `PASS_SINGLE_PASS_COMPLETE_QUALIFICATION` outputs, without an extra performance/PASS shortcut.

The official complete 45-file PR #5818 export at `a0171b8d2f942cdfc5295307548fe484c570b1ba` is retained as immutable `inputs/PR5818.tar`, SHA256 `f166f27e7c247315e852f78e30b2d348e9b66518645b783b5344a6767d87e7cc`. Its source is authenticated before importing; its nested original 54-file PR #5757 export is also authenticated unchanged. Private materializations are read-only and Git-free and checked after success. No network, Git command, unmerged-object cache, third-party Python dependency, edited source or changed expected scientific receipt is needed at runtime.

To repeat a bounded comparison on Linux with `/usr/bin/python3.12`, GNU `/usr/bin/time` and `/proc`, choose a new work directory:

```sh
python3 -B research/literal-gate-setup-reuse/benchmark.py pair --workdir /tmp/setup-reuse-fresh
python3 -B research/literal-gate-setup-reuse/benchmark.py optimized --workdir /tmp/setup-reuse-fresh
```

The pair runs the complete PR #5818 baseline then complete candidate serially, with 600 seconds per command, 900 seconds aggregate, 1 GiB sampled process-group RSS, bounded output and no retries. Expansion requires byte-identical complete stdout and at least 15% lower wall and CPU time. The separately gated optimized phase allows 1,500 seconds cumulative, retaining the same command and memory caps. Existing work directories and run receipts are not overwritten. This opt-in reproduction does not silently repeat the original six-command development round or any historical suite.

## Qualification and source scope

The local round profiles once, measures one unprofiled pair, then separately qualifies the packaged normal, optimized and sealed optimized forms. Normal and deliberate optimized finite controls pass. The complete optimized package passes in 214.55 seconds; its read-only, Git-free implementation export passes under `-I -O -B`, empty PATH and an explicit authenticated import root in 213.97 seconds, with all 42 exported files unchanged. All six local scientific commands pass in 1408.80 seconds total, including the profiler, within the staged 900/1,500-second aggregate limits. These mode/export qualifications are outside the initial speed comparison. Exact committed bytes/modes and hosted CI are recorded separately in VALIDATION.json and the canonical PR handoff. Full-history preflight is unavailable in this shallow checkout; immediate declared input-pin ancestry is checked without claiming a complete history audit.

Canonical main at entry is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. Targeted PR/body and relevant Discussion overlap checks found no matching setup follow-up; they do not establish exhaustive novelty or unpublished-work coverage. The branch retains Ali Romman's exact [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761) test-only repair with original authorship/provenance, already used by PR #5818. No shared research framework, frozen predecessor package, selected record or scientific expected output is changed.

The inherited PR #5818 process-sharing boundary remains: this is not a second cold source execution. The two literal arithmetic implementations still execute fully, with this dense implementation reusing only its own exact scalar setup. Same-agent checks and hosted CI are not independent human or proof-kernel acceptance. The five framework assumptions, conditional kappa and selected record are unchanged. Kappa research, its monitors, automations, literature work and workers remain paused.

## Open next questions

- Does this speedup hold on a second host? Repeat the exact bounded pair and retain all samples; no universal guarantee follows from one baseline here.
- Can a changed compiler use the technique? Authenticate its full closure, remap all AST and key-domain obligations and run finite feasibility before construction. The current source/AST pins deliberately reject changed methods.
- Is the remaining complete source replay now the bottleneck? Profile again only under a separately authorized task. This submission releases its bounded scope and starts no successor work or kappa experiment.

## Credit

Ali Romman supplied [PR #5704](https://github.com/CrocSwap/integer-mult-bounds/pull/5704), [PR #5757](https://github.com/CrocSwap/integer-mult-bounds/pull/5757), the original literal interpreters, controls and engine; preserve [PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) and the native/controller/compiler/helper/BIT/classical stabilizer lineage. [PR #5816](https://github.com/CrocSwap/integer-mult-bounds/pull/5816) supplied Linux qualification and the resource guard; [PR #5818](https://github.com/CrocSwap/integer-mult-bounds/pull/5818) supplied single-pass orchestration. The retained archive and NOTICE preserve full attribution. New setup derivation, finite controls, profiling and measurements: Chris R / Clear1nsight, with substantial OpenAI Codex assistance; no subagents. Memoization and tabulation are standard techniques. Apache-2.0.
