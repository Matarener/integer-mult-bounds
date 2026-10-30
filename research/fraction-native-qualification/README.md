# Native bookkeeping for complete PR5848 qualification

The complete frozen qualifier runs in **32.77 rather than 40.52 seconds median wall time (19.12% less)** and **32.74 rather than 40.33 seconds median CPU (18.82% less)** on this Linux host. Each candidate command includes every new finite/native check and a fresh compile, link and load. Compiler-child CPU is counted. This is a local six-process B,C,C,B,B,C comparison, not a universal speedup or hosted performance result.

This opt-in package follows [PR #5848](https://github.com/CrocSwap/integer-mult-bounds/pull/5848), [PR #5852](https://github.com/CrocSwap/integer-mult-bounds/pull/5852), [PR #5853](https://github.com/CrocSwap/integer-mult-bounds/pull/5853) and the [entry-domain handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/5852#issuecomment-6436191164). It changes verification implementation; it makes no kappa, construction, physical-cost, compiler or selected-frontier claim. Kappa research remains paused.

## What changes

An exact 16,384-entry per-trace contribution table avoids recomputing pure Fraction contributions. Bounded injective tokens represent complete canonical weight pairs, always indexed by the original source site i. A small C extension implements the exact seven-integer key, FIFO bookkeeping and coefficient-loop control. It uses authenticated Fraction descriptors and ordinary Python C APIs, retaining the GIL. The original Python Fraction callback computes every miss; all three score additions still use Python numeric operations in their original order. Per-coefficient F(0) construction is deliberately retained.

Rows, rounded injections, ideal metadata, full output comparisons, signed witnesses, peaks, hashes, reverse checks and the independent exact integer backend remain active. Mutable caches and answers never cross traces or backends. Only loaded immutable native code is reused within one fresh process; each fresh process pays its build. Unsupported or changed native packets use the inherited checked path or literal original trace under the documented domain rules. A platform without the required compiler/headers fails native qualification explicitly.

## Frozen sources and coverage

Canonical main: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8. Complete PR5848: `66fb6c6b8683b37967e9d7f313b3df99a49d2406`. Its 97-file official export remains byte-for-byte unchanged. The source manifest pins all 12 retained inputs to own ancestor `2ebc3a071c62fc839aaed1291220d78a317395d4`. The separate inherited test-only PR5761 repair retains its exact author/commit credit; no shared test is weakened here.

- **964** complete finite comparisons on 241 programs at four capacities, with full values, numeric types and input preservation.
- **73** inherited controls and **45** native controls, covering collision equality, FIFO wrap, exceptions, source/runtime drift, fallback, metadata ownership, cyclic GC, re-entry and malformed C API packets.
- **Four** unchanged predecessor source-custody rejection checks in registered verification, separate from both timed candidate.py stages as in PR5848.
- Complete independent qualification on **25,984 events / 799 coordinates**, including all 120 inherited independent finite fixtures, six source controls, full actual ideal/error outputs and witness comparisons. Actual output SHA256: `954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9`.
- Complete optimized qualification also passes. The C native actual path preserves 2,579,750 calls, 2,252,966 hits, 326,784 misses, 310,400 FIFO evictions and 3,587 weight tokens.

The native API accepts validated packets from the source-bound wrapper. Its error/lifetime checks are memory-safety defenses, not a theorem that arbitrary callbacks or noninjective supplied tokens have Fraction semantics. The proof assumes stable inputs/runtime during a trace, matching the predecessor. Full-C-API support is the tested CPython 3.12 ABI; this is not abi3, subinterpreter or free-threaded support.

## Reproduction

Tested on Linux x86_64, CPython 3.12.3 and GCC 13.3. An existing `cc` and Python 3.12 development headers are required; no dependencies are installed and no compiled binary is committed.

Registered finite/native/source verification, about three seconds here:

```sh
python3 -B scripts/research_package.py --package research/fraction-native-qualification
```

Explicit complete guarded replay, about 33 seconds here. Choose a new evidence directory outside the package; it retains stdout, stderr, timing, source inventory and RSS receipts:

```sh
python3 -B research/fraction-native-qualification/replay.py /tmp/native-qualification-evidence
```

Fresh complete timing round, first pair then the remaining fixed-order repetitions only if the first pair passes both 15% gates:

```sh
python3 -B research/fraction-native-qualification/benchmark.py pair /tmp/native-qualification-benchmark
python3 -B research/fraction-native-qualification/benchmark.py remaining /tmp/native-qualification-benchmark
```

The same default 180-second command / 1 GiB sampled process-group RSS / 600-second initial round and 1,500-second shared-round contract applies. One serial runner, zero automatic retries. Do not infer complete performance from the inner `qualify.seconds`: it excludes the preceding native finite/build stage. The outer GNU-time receipt is authoritative and includes compiler children. The original raw timing driver and every observation are retained under `evidence/runtime`; the portable wrapper changes evidence/source path resolution only.

## Findings, failures and limits

The earlier table, entry gate and compact keys were correct within their tested domains but failed their complete-cost screens. Cache-only C lookups were slightly slower than the Python slot-key parent in the fixed micro screen. The full coefficient-loop mechanism subsequently passed a complete actual audit and the complete timing gate. Do not discard those negative results or credit all improvement to C alone: the candidate combines the exact table, source-bound entry/compact/slot mechanisms and native bookkeeping.

The first debug attempt passed scientific checks but stopped on a temporary-directory cleanup ResourceWarning. Explicit cleanup fixed it without suppressing warnings. A later forced-GC constructor fixture was inert: its callback did not run during construction, so it did not demonstrate the intended interleaving. That failure and draft remain; a deterministic metadata-ownership test replaced it. Checked constructor token reads remain a source-reviewed safety condition. No empirically exercised constructor-GC interleaving is claimed. All attempts are retained; no automated retry or timing sample was dropped.

The source reviewer is a user-requested GPT-6-astra xhigh agent and performed static review only. All compiler and numerical execution used one parent runner. This is assisted engineering verification, without independent human or proof-kernel acceptance. Registered hosted replay covers finite/native/source checks; it does not itself freshly establish the local complete-performance measurements. See [PROOF.md](PROOF.md), [VALIDATION.json](VALIDATION.json), the [complete timing gate](evidence/runtime/GATE-6.json) and the retained static reviews.

## Open next questions

Can a further source-bound reduction in the remaining coefficient/score bookkeeping pay its additional validation bill? First census the new candidate, refresh upstream overlap and name one bounded feasibility test. Keep this measured candidate frozen during publication. A new arithmetic implementation would require a broader independent proof and validation bill; it is outside this contribution.

Original mathematics/arithmetic: Ali Romman and all retained P104/native/compiler/precision authors; see NOTICE and nested archives. New profiling, table/domain/compact/slot integration, C helper and validation: Chris R / Clear1nsight with substantial OpenAI Codex/Astra assistance. Apache-2.0.
