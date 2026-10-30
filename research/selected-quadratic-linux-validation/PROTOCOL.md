# Frozen Linux qualification protocol

Authority: the human requested Linux validation of PR5757, clear success/stop criteria, complete coverage and a focused upstream PR. The kappa campaign stays paused.

Subject: PR5757 head `53006fe6031dab5c23d5b7d1cf6a92f411a04a68`; current main `de5ec2e7a6074068452f45b1a191b5c72832df4a`. The 54-file retained source closure consists of its 23 files and 31 declared live inputs, all byte/blob authenticated. No engine or source proof changes are allowed. Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/pull/5757#issuecomment-6430625161.

## Success

1. Unchanged complete literal and accelerated source checks exit zero, with byte-identical full scientific stdout equal to the known selected stdout hash. Original code independently reconstructs and compares complete RESULT and decompressed WORD; adapter binding preserves all scientific checks.
2. All six alternating fresh-process samples use the same 54 files and environment. Record every sample, wall/user/system time, kernel max RSS and sampled aggregate process-group RSS. Compute medians/ranges without dropping a slow result. No universal or cross-platform speed claim.
3. Complete adapter qualification includes existing cache/type/mutation/proof-omission controls and every actual state compared with both literal interpreters. Normal and deliberate optimized operation retain explicit failures. Qualification overhead is measured separately from the timed source replay.
4. Source bytes and permissions remain unchanged, and the retained source root is Git-free/read-only. Separate source corruption controls operate on private copies, never frozen originals.
5. Publication reports source pins, complete coverage, all failures/stops, measured limits, predecessor credit, portable reproduction and a seven-field handoff. No new kappa, engine redesign or selected-result change.

## Execution limits and stopping

- One root scientific executor; one exclusive lock; no parallel scientific runs.
- Maximum 600 wall seconds per scientific command; 1 GiB sampled aggregate process-group RSS; 2 MiB stdout and stderr each; 4,500 seconds aggregate scientific wall budget for this qualification. These are newly declared task limits, not reuse of the consumed 150-second campaign grant.
- First execute only the first literal/accelerated pair. Continue the remaining `quadratic,literal,literal,quadratic` samples only after exact equality, integrity and resource feasibility pass. No automatic retries.
- Following the timed samples, execute the original full `verify.py` and `cross.py` as distinct qualification phases. An optimized qualification may be used to satisfy deliberate `-O` coverage without repeating unchanged full phases unnecessarily.
- Any output/binding/coverage mismatch, source or permission change, unexpected stderr, nonzero exit, timeout, memory/output limit or missing dependency stops the affected phase. Preserve evidence. Do not change thresholds, inputs or expected results to obtain a pass. A bounded infrastructure repair must be documented and reviewed before any new run.
- No speedup is a valid outcome. Publish useful platform/coverage findings without claiming improved performance. A successful optimization does not discharge the five inherited framework assumptions or constitute independent human/proof-kernel acceptance.

## Independent work and overlap

Review the source binding, complete output comparisons and cache/phase contract independently. This contribution is Linux qualification of the author's implementation, not a second native engine. Live PR5757 head/comments and Discussion5748 were checked; a targeted PR search returned no separate Linux scope. Discussion coverage is bounded, not an exhaustive novelty claim.

Shared assignment-test repair PR5761 already exists; do not duplicate it. Upstream connector comment writes returned403; the authorized signed-in Chrome session posted the claim successfully. Existing monitors, other threads and kappa construction workers remain paused.
