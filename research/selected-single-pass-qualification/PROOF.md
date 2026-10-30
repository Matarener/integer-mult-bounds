# Coverage-preserving process-local qualification

This argument is bound to PR #5757 head `53006fe6031dab5c23d5b7d1cf6a92f411a04a68`, including its exact 54-file official export. It concerns verification orchestration, not the multiplication theorem, a new state engine, a new native program or a kappa gain.

## Source custody

`source.payload()` checks the exact archive and complete manifest hashes, the official export commit, all 55 regular archive members, and every retained source length, SHA256 and Git blob. Only the 54 authenticated source paths are materialized. The private source tree is Git-free and its files are read-only. No predecessor file, expected RESULT/CROSS, generated mathematical artifact or selected metadata is changed. All source file hashes and modes are checked again after execution. This assumes a stable local execution environment, as does the existing package runner; it is not an atomic filesystem or adversarial-host guarantee.

Both original `verify.py` and `cross.py` are loaded without modification and their `main` functions are actually called. Their original authentication, AST binding, receipt reads, full equality checks and exceptions remain in place. The inherited four-file AST binding still rejects undeclared changes in the compiler, native interpreter, local verifier and complete source verifier. `runpy` loads the entry functions but does not invoke their `__main__` guards. The public wrapper accepts no command arguments; neither legacy parser is allowed a recording/write option.

## The observed first execution

The original verify entry authenticates its 31 live inputs and derived ASTs, executes the full adapter corpus and cache/type/mutation/proof-omission controls, resets state counters and the signature cache, then invokes `verify_source.main([])`.

The observer is installed only at this final call site. It requires exactly one empty-list call, `TRACE is None`, empty counters, and an empty cache with zero hits and misses. It enables the adapter's existing trace collector, invokes the original complete source verifier, saves the sorted immutable input-key trace and copies counters/cache statistics. It restores `TRACE` in a `finally` block and forwards the original return value and any exception. Existing `support` computes the same signature, amplitudes and counters whether tracing is enabled or disabled; the sole trace operation inserts its already-computed complete immutable key into a set. Repetitions are deduplicated only in the audit input inventory, as in the original cross checker. No scientific computation or acceptance is bypassed in this first execution.

The original verify entry resumes and compares its complete original RESULT, including derived hashes, source RESULT/WORD hashes, all control summaries, cache statistics and call counts. No field is projected away or regenerated to make it pass. Instrumentation overhead is included in candidate time.

## The second entry point and complete oracle

The original cross entry authenticates and checks its bindings again, imports the same adapter, and creates an empty trace set. Its complete source call is temporarily replaced by a handoff. That handoff requires one successful capture, one handoff only, the exact empty-list arguments, an empty cross observer, and counters and cache statistics identical to the snapshot made immediately after the actual source execution. It transfers the captured keys into the original cross collector without state evaluation, result import or output playback.

The unchanged remainder of cross closes its observer, freezes counters, sorts every key, and for each actual input:

1. evaluates the unchanged literal Clifford compiler;
2. compares the complete dense vector and denominator with the quadratic adapter;
3. derives the exact nonzero sparse map;
4. compares that map and denominator with both the adapter and the second unchanged literal interpreter;
5. counts all `2^n` amplitudes, including zeros.

It compares the complete original CROSS: all call counts, 17,651 distinct inputs, 9,037,312 amplitude positions per literal interpreter, two interpreters and the exact trace digest. The input trace has SHA256 `73ac04db73d83151efb474925d48298664cc7490d31bdec7a70dcf79b448f481`. The handoff cannot add synthetic control keys: capture starts after the original control reset and the original exact digest/count checks remain mandatory. The public wrapper additionally requires exactly 17,651 inputs and reports one source execution and one handoff.

On success or failure, the original source entry is restored and `TRACE` is closed. The orchestration has no disk result cache, cache of PASS, cross-commit reuse, randomized sampling, approximate arithmetic or alternative scientific acceptance path. Both original standalone entry points remain available in the authenticated export.

## Fresh-process boundary and independence

The original second **complete source execution** is intentionally not retained as a separate test. The two literal interpreters are still loaded and executed independently of the quadratic engine; they are not replaced by a cached answer. The cross phase shares the already-completed source run and process state. It therefore does not provide a second cold source execution or general protection against every possible stateful host/interpreter defect.

The source is deterministic and its proof-relevant outputs, complete receipts, exact input trace and cache/counter state are checked explicitly. The small feasibility fixture compares the complete baseline two-execution and candidate one-execution receipts using the actual adapter and both literal interpreters. It covers repeated calls, control-trace exclusion, wrong stage arguments, missing/repeated stages, counter/cache leakage and exact exception restoration. Separate fresh normal and optimized candidate runs preserve mode-specific checks. The original two-command baseline remains the audit fallback. A changed word, adapter or dependency needs a new source/coverage decision; this result does not transfer automatically.

## Measurements and scope

The benchmark compares the sum of the two original full registered scientific commands against the complete combined command, in fresh serial processes on the same source and host. Candidate output must contain the entire original verify output and the entire nonduplicate cross output byte-for-byte; only a separate orchestration summary is appended. Every sample and stop is retained. The initial comparison is one baseline/candidate pair, not a median, statistical confidence interval or universal speedup. Normal and optimized candidate stdout must agree completely. Measurement, finite conformance, hosted CI, independent mathematical review and the inherited five framework assumptions remain separate.

## Credit

Ali Romman supplied the original exact quadratic engine (PR #5704), full selected replay integration and both literal audits (PR #5757), original proofs and controls, and retained P104/native/controller/compiler/stabilizer lineage. PR #5816 supplies the independent Linux qualification and the retained resource guard. The new work is the process-local observer/handoff, coverage analysis, controls and paired measurement, prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance. No subagents or independent human/proof-kernel acceptance. All retained notices remain in the archive and NOTICE. Apache-2.0.
