# Independent Linux qualification of the selected quadratic replay

On this Linux x86_64 host, the complete [PR #5757](https://github.com/CrocSwap/integer-mult-bounds/pull/5757) source replay has a median runtime of **339.49 seconds with the literal engine and 130.58 seconds with the quadratic engine: 2.60x faster**, or **61.54% less wall time**. All six full scientific stdout hashes agree. The original complete RESULT and regenerated WORD comparisons, mathematical checks and rejection controls run unchanged.

This independently qualifies Ali Romman's published integration on Ubuntu 24.04.5 LTS, CPython 3.12.3 and an Intel Core i7-4790. It changes verification capacity. The selected conditional kappa remains **0.00310045**, with the same five framework assumptions.

## Measurements

| Fresh process | Engine | Wall seconds | User + system CPU seconds | Kernel peak RSS MiB |
| --- | --- | ---: | ---: | ---: |
| 1 | literal | 349.644 | 348.37 | 474.92 |
| 2 | quadratic | 130.581 | 130.26 | 492.72 |
| 3 | quadratic | 127.268 | 126.82 | 492.38 |
| 4 | literal | 331.023 | 330.42 | 475.05 |
| 5 | literal | 339.494 | 338.36 | 474.93 |
| 6 | quadratic | 132.138 | 131.53 | 492.51 |

The literal range is **331.02–349.64 seconds**; quadratic is **127.27–132.14 seconds**. Median child CPU time is 338.36 versus 130.26 seconds. Timed peak RSS increases from at most **475.05 to 492.72 MiB**, about 17.67 MiB. The process cache is fresh each run; operating-system caches are not flushed. This is a descriptive three-sample comparison per engine on a shared host with dynamic CPU scheduling, not a universal performance guarantee.

## Complete qualification and its extra cost

The two original registered scientific commands also pass in normal Python: full adapter qualification **128.13 seconds**, and all-actual-state literal comparison **274.74 seconds**, totaling **402.88 seconds**. Deliberate optimized adapter qualification and oracle runs pass in **127.00 and 277.05 seconds**, totaling **404.05 seconds**. The two oracle outputs match byte-for-byte, as do normal/optimized adapter outputs. That stronger qualification work is additional to the timed complete source replay; it is not included in the 2.60x claim.

The full source and its source syntax binding preserve:

- All thirteen helper cuts, 748 public inputs, 756 reverse columns and 571,536 endpoint coefficients.
- All 2,923 distinct native frame maps, 208 main adapters, 1,080 helper normalizers, signed Pauli actions and absolute phases.
- The physical caller, productive targets, complete paid/target invoice, both moment engines, compiler and outer checks, and original rejection controls.
- The 1,522-case adapter corpus, cache key/type/mutation/capacity/eviction controls and three omitted-proof rejection controls.
- Every actual state input: 17,651 distinct states, with 9,037,312 exact amplitude entries compared against each of the two original literal interpreters, including zeros and denominators.

Independent static inspection also confirms that all thirteen original assertions are outside the replaced state method and become explicit failures in the derived compiler. The existing optimized width-mismatch control passes. See [the coverage review](PROOF.md), [assertion map](ASSERTION-COVERAGE.json) and [coverage inventory](COVERAGE.json).

All ten commands exit zero, with no stderr, resource stop or source mutation. Their aggregate scientific wall time is **2,217.07 seconds** under the declared 4,500-second shared budget. Each command is capped at 600 seconds and sampled aggregate process-group RSS at 1 GiB. Maximum kernel RSS across qualification is **516.88 MiB**. The sampled aggregate peak is **513.62 MiB**; sampling can miss a short peak and is not an exact continuous maximum. Raw outputs and resource measurements are in [RESULT.json](RESULT.json) and `evidence/`.

## Reproduce the recorded evidence

Python 3.12, standard library:

```sh
python3.12 -B scripts/research_package.py --package research/selected-quadratic-linux-validation
```

Expected markers:

```text
PASS_LINUX_RECORDED_EVIDENCE_ONLY
PASS_SYNTHETIC_RECORDED_EVIDENCE_CONTROLS
PASS_REGISTERED_RESEARCH_PACKAGE
```

This short registered check authenticates source and recorded outputs, recomputes statistics and runs 17 synthetic evidence rejection controls. Three additional controls launch the original optimized entry on private copies with a damaged engine, WORD or compiler; each rejects at the exact source-hash predicate before mathematics starts. It does **not** rerun the expensive positive scientific experiment or attest independently that a recorded measurement occurred.

Controls reject omitted qualification, changed entry points or runner/source identities, resource failures, boolean/number aliases, nonfinite time, diagnostics, reordered samples and a truncated oracle with a coherently rehashed receipt. Complete typed output is checked, not merely a PASS marker. The existing source controls remain in the cold experiment.

## Cold Linux experiment

The original official 54-file export is retained byte-for-byte in `inputs/PR5757.tar`; its 55th member is its export receipt. Runtime needs no Git or network. `reproduce.py` authenticates every member and creates the same read-only 54-file source tree, then uses the exact original measurement runner in an external work directory:

```sh
python3.12 -B research/selected-quadratic-linux-validation/reproduce.py all --workdir /tmp/pr5757-linux-fresh
```

Use a new directory. This explicitly runs six complete timed source replays plus four qualification commands, serially, and can take roughly 37 minutes on the measured host. It stops on the first failure and never retries or overwrites an existing run. GNU `/usr/bin/time`, `/usr/bin/python3.12` and Linux `/proc` are required. The per-command and aggregate resource limits remain in force. It adds no discovery search, native build, Lean, Docker or historical suite.

For a staged run, use `prepare`, `pair`, `remaining`, `qualification` and `cross-normal` with the same work directory. The first pair must pass exact integrity/output checks before the remaining samples. [PROTOCOL.md](PROTOCOL.md) records the initial decision and [the normal-oracle addendum](NORMAL-ORACLE-ADDENDUM.md) records the explicit final mode-specific gate. Source preparation and recorded-evidence checking are tested separately; the public convenience command sequences the same frozen runner phases rather than claiming an additional unrecorded ten-run experiment.

## Sources, independence and limits

Subject head: `53006fe6031dab5c23d5b7d1cf6a92f411a04a68`; canonical main at entry: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. The package refines `replay-runtime` to independent Linux qualification; it implements no engine optimization. [The original released investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5748) explicitly left Linux measurements open. [Our bounded claim](https://github.com/CrocSwap/integer-mult-bounds/pull/5757#issuecomment-6430625161) precedes these runs. The overlap search was targeted, not an exhaustive novelty audit.

The 31 live source inputs and 23 integration files retain their original bytes and notices. Original origin commits are recorded but are not required as cached unmerged Git objects at runtime. The new retained archive and manifest are pinned to their real retention commit in SOURCES.json. No frozen source, original expected receipt or selected metadata is edited. The local publication checkout is shallow: full-history ancestry preflight is not claimed. Exact committed bytes/modes and immediate ancestry of the two declared pin commits are checked separately. The inherited native/all-width, ownership, compiler, precision/tape and analytic assumptions remain. No new physical multiplier speedup, kappa gain, independent human or proof-kernel acceptance is claimed.

Shared assignment-test failures have an existing separate repair, [PR #5761](https://github.com/CrocSwap/integer-mult-bounds/pull/5761). This package does not duplicate it. Hosted results for this submission are reported separately from local scientific qualification.

## Open next questions

- Can a reviewed newer word use the same acceleration? Start with exact source/consumer binding and complete artifact/control comparisons; this frozen result does not transfer automatically.
- Can repeated qualification cost be reduced safely? First distinguish engine-validation reuse from changed-word coverage, bind the complete actual-input trace and code dependencies, and require invalidation controls. A cached scientific PASS is insufficient.
- Does the performance hold on another Linux host? Repeat the same bounded serial experiment and retain all samples, full outputs and memory tradeoffs.

The kappa research campaign stays paused. Any next engineering experiment needs its own measured bottleneck and scope decision.

## Credit

Ali Romman supplied PR #5757, the [PR #5704 exact quadratic engine](https://github.com/CrocSwap/integer-mult-bounds/pull/5704), original proofs/controls and macOS measurements. Retain the [PR #5599 construction](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), native, controller, compiler, helper, BIT and classical stabilizer lineage in [NOTICE](NOTICE) and the original export. New Linux execution, applicability review, guarded reproduction and evidence checks were prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance. No subagents. Apache-2.0.
