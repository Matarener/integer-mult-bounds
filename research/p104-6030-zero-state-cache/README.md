# Gate-table zero_state for the selected PR6030 primary replay

**Replay-runtime tooling only. No new κ, no certificate change, no edit to any frozen file, and no change to
`make frontier6030-verify`.** The selected frontier is untouched.

## What it does

The selected replay (`make frontier6030-verify`, via `scripts/audit_p1046030.py`) runs DreamingOfClouds'
PR6030 verifier `research/p104-helper470-twin-rung-removal/verify.py` twice, in normal and `-O` mode,
each under a 600 s stage timeout. The maintainer audit recorded 228 s and 461 s for these two stages.

A cProfile of the normal run (280 s under the profiler) puts **202 s in one function**:
`Op.zero_state` of the vendored exact Clifford compiler `research/p104-native-channel/vendor/clifford_exact.py`,
called 32,766 times from `local.native()` through `lower_child` and `monomial`. For every gate of every
call it re-evaluates a per-address Python function over all 512 addresses: `mv(G, x)` for permutation gates
(73 s) and `qvalue(Q, alpha, x, n)` for diagonal gates (101 s).

That bottleneck has already been solved for the same compiler bytes. Charles Bethin's merged
[`research/clifford-state-performance/fast_state.py`](../clifford-state-performance/fast_state.py)
(PR662 lineage) replaces both per-address loops with exact tables built by a lowest-bit recurrence, and its
README gives the proof of equality. It was pinned against
`research/complex-multicold/.../clifford/clifford_exact.py`, SHA256 `2982ead0…0962`. PR6030's chain loads
another copy of that file from PR5827's archive chain, and the copy is **byte-identical**. VictorLiwentao's open
#2329 wires the same evaluator into the cold617 consumer.

This package adds no new table algorithm. It binds the existing evaluator to the selected PR6030 consumer:

- `run.py` executes the **unchanged** PR6030 `verify.py` in place, through `runpy`. That verifier
  authenticates its own seven-deep source chain and requires its committed `RESULT.json` byte for byte. A
  `SourceFileLoader.exec_module` hook intercepts every module named `clifford_exact.py`. It refuses bytes
  that do not hash to the pin (fail closed), executes exactly the hashed bytes, and then replaces
  `Op.zero_state`. The run must load and patch at least one copy. All 12 PR6030 package files that the run reads, `fast_state.py` and the vendored
  compiler (14 input pins) are checked against `SOURCES.json` before the run.
- `run.py --mode differential` runs the original and the table method on **every** zero_state call that
  reaches the method in the real run and requires the results to be equal, including the list-of-tuples container. It returns the
  original value, so the target's own checks see unchanged values.
- `test_equivalence.py` (about 1 s): 1,714 random-circuit states for n = 1..9, 280 lowered children, 48
  canonical frames. Three mutants (sign, unreduced denominator, global phase) are rejected by the
  differential wrapper with its mismatch error. Changed compiler bytes are refused by the hook. Each of the
  14 changed input pins is refused, and so is a one-byte change to each of the 14 input files.

## Results

Same fixture, same harness, fresh processes (raw samples in [BENCHMARK.json](BENCHMARK.json)):

| Stage of the selected replay | original zero_state (s) | gate tables (s) | ratio of medians |
|---|---:|---:|---:|
| normal (`-I -B`) | 120.38*, 107.01 | 47.31, 47.64 | 2.39x |
| optimized (`-I -O -B`) | 62.94, 62.16 | 42.03, 41.68 | 1.50x |
| both primary stages | 169.2 (second round) | 89.3 | about 80 s saved per selected replay |

\* overlapped the differential run. An earlier pair of normal baselines on the same host gave 107.83 and 107.72 s,
and an earlier pair of `-O` baselines gave 60.85 and 62.11 s. The table was measured before two hardening
edits made after review: the hook now executes the hashed bytes itself, and fast mode counts its calls. After
those edits, the registered run's fast stage took 47.49 s and a separate `-O` fast run took 41.97 s.

**Coverage.** The differential run passed on all **32,766** zero_state calls that reach the method in one
normal-mode replay (131.1 s, and 115.8 s in the registered run). These are every call of this fixture, not all
possible inputs. After each run, every module in `sys.modules` loaded from a file named `clifford_exact.py`
must carry the replacement, which guards against a copy loaded by another route. The hook executes exactly
the hashed bytes, so no bytecode cache can substitute for them. The fast-table runs print the target's
marker `PASS_P104_BASE5907_EDIT_KAPPA_312580400`, which the unchanged verifier prints only after requiring its
committed `RESULT.json`. That file includes `recipe_payload_sha256` over all 2,922 distinct native
chart-change recipes and 208 main adapters. With bounded 64-entry caches, the run makes 14,020 phase-table and 13,812 permutation-table misses; each table is rebuilt in O(512) by the
recurrence.

Host: macOS arm64 (Apple M5, 10 cores), CPython 3.12.14, `python3.12 -I -B [-O] run.py --mode …`. All four
modes ran serially in alternating order on the same fixture. The host was shared with two other research
sessions (load average about 8 on 10 cores), so these are descriptive wall times for this host, not a
platform-independent ratio. No correctness check depends on the timing.

**Why `-O` is faster here, and what it skips.** Under `-O`, Python drops every `assert` in `clifford_exact.py`.
These include the compiler's self-checks in `lower_child` and `monomial`, such as
`compiled.zero_state()==op.zero_state()`, so the optimized stage makes 8,974 zero_state calls, against
32,766 in normal mode. This is not a coverage gap in the selected replay. Every recipe is still checked independently by
`native_verify.equal`, which uses `require`, not `assert`, and the normal stage keeps all the assertions.
Reviewers comparing the two stages should still note that they do not execute the same checks.
The maintainer audit's 461 s for `-O` against 228 s for normal does not match the local ordering. Those runs
were on another host and at other times, so this package does not explain that difference.

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/p104-6030-zero-state-cache/verify.py                       # tests + fast run, ~50 s
python3.12 -I -B research/p104-6030-zero-state-cache/run.py --mode differential       # every call, ~2 min
python3.12 -I -B research/p104-6030-zero-state-cache/run.py --mode original           # timing baseline
python3.12 scripts/research_package.py --package research/p104-6030-zero-state-cache   # both commands, 165 s here
```

Each run prints one JSON line: status, counters (loads, patched loads, differential calls, table cache
hits and misses), seconds and the `-O` flag. The target's own marker
`PASS_P104_BASE5907_EDIT_KAPPA_312580400` is printed by the unchanged verifier before it.

## Limits

- This package does not change the selected replay. Opting `scripts/audit_p1046030.py` into it is a
  maintainer decision. The audit runs a copy under `work/source/`, so `run.py`'s fixed `TARGET` would need a
  parameter (open question 1).
- Equality is established by the evaluator's written recurrence proof (in the predecessor README), by the
  differential over every call of this one fixture and by random circuits. It is not a formal proof.
- Only CPython 3.12 on macOS was timed. Linux, Windows and other CPython versions were not run.
- The five framework assumptions of the selected record are untouched and irrelevant here.

## Open next questions

Also in [TASK.json](TASK.json):

1. **Opt the selected replay into the binding?** First step: parameterize `TARGET` to the audit's
   `work/source` copy, then run the five-stage audit with both engines and compare `VALIDATION.json` and the
   stage logs byte for byte. This needs a maintainer decision, because the selected replay is admission evidence.
2. **What is the remaining ~45-55 s?** No function now dominates the way zero_state did. The first profile
   suggests the next candidates are the orthogonality loops in
   `research/p104-productive-controller/caller.py::physical` and the pr4359 `native_inventory.contact`. A
   fresh profile of `--mode fast` should come before any change.

## Credit

- PR6030 word, verifier and package: DreamingOfClouds (with Claude), with Douglas Colkitt's portability repair.
  PR5827's chain (local.py, pricing, sources): Ali Romman, with the lineage named in its files.
- Exact Clifford compiler `clifford_exact.py`: retained through icekylinx's frame-sa504 package. Native channel:
  Chafik Boukhalfa (PR1992). The independent Gaussian interpreter comes from Ali Romman's PR1862.
- Gate-table evaluator `fast_state.py` and its equality proof: Charles Bethin (PR662 lineage), reused unchanged.
  Related prior replay-runtime work on the same kernel: #2329 (VictorLiwentao, production cold617 wiring),
  `research/packed-clifford-gate-tables` (PR1781 packed checker) and `research/clifford-state-reuse`.
- This binding, its tests and its measurements were prepared by Josie Elliston with Claude Opus 5.5
  (Anthropic) via Claude Code. Apache-2.0.
