# Skip impossible numeric-reference scans in research overlap searches

The complete offline `joint-query-controller` overlap command takes **48.7% less
wall time** on the recorded workload. Seven alternating runs per side give
medians **1.015105 s before and 0.521243 s after**. Baseline range is
0.994940–1.087073 s; candidate range is 0.510642–0.535762 s. All fourteen
complete JSON reports agree after removing only `searched_at`, with zero errors.

Claim type: empirical tooling improvement with a scoped equivalence argument
and finite regression evidence. No new kappa or selected-frontier change.
This contribution was produced by Nick Petalas.

## Change and correctness

`scripts/find_overlap.py` builds numeric-reference patterns from an optional PR
prefix, the escaped literal number, and boundary assertions. Every successful
match contains that literal number. If it is absent from the lowercased text,
returning `-1` is therefore exact. If it is present, the original regex still
runs on the entire text. Its original start offset, including any PR prefix,
is preserved. Explicit literal queries still use the original `str.find` path.

The change adds one substring predicate. It does not alter query construction,
reference boundaries, scoring, excerpts, ordering, local/remote inventories,
cache freshness, pagination, or warnings. This proof concerns the patterns
constructed by `search`; arbitrary unrelated patterns supplied directly to the
internal helper are outside its contract.

The baseline profile put 0.559 s in reference regex scans in a 1.652 s profiled
command. A separate candidate profile puts 0.035 s there; local Git inventory
and Unicode excerpt-offset conversion remain substantial costs. Profiling runs
are excluded from the timing samples. The first measured improvement was frozen.

## Evidence and reproduction

[BENCHMARK.json](BENCHMARK.json) is generated from measured output. It records all
samples, source and cache SHA256 values, environment and coverage. The external
16,945,386-byte cache contains 407 open PRs and 5,816 Discussion records. The
sparse checkout searches 72 local notes and explicitly reports 8,278 omitted
HEAD notes. The command returns 1,580 matches. Every full warning and omitted
path list participates in report comparison, even though the benchmark summary
prints only the omitted-path count.

CPython 3.12.15, macOS 27.0.1 arm64, standard library only. The machine has
18 logical CPUs; load averages at intake were 4.62, 3.74 and 3.02. Other work
was not stopped. Both sides use the same interpreter, flags, immutable cache,
checkout, process wrapper and seven alternating pairs. The timed interval
includes startup, imports, local inventory, JSON parsing, search and output.
Comparison and workload hashing occur after timing. The gain is consistent
with removal of the profiled scans and exceeds the observed ranges.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/overlap-reference-prefilter/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/overlap-reference-prefilter
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/overlap-reference-prefilter --check-source-history
```

Another CPython 3.12 installation can replace the absolute path. Both registered
normal and optimized checks enumerate 39,216 numeric offsets and the same number
of literal offsets. Eight complete search comparisons use 289 constructed
title/body pairs, including Unicode expansion, decimal/hash false positives,
explicit numeric overrides, duplicate terms, AND/OR modes and late excerpts.
Work controls require zero regex calls on an absent literal and retain the
boundary checks on present but invalid numbers. The actual CLI regression suite
also runs, including its unchanged numeric-reference fixtures.
[CHECK_TIMES.json](CHECK_TIMES.json) records the three registered commands at
0.126, 0.198 and 0.710 seconds locally, each below its 120-second limit.

To repeat the performance experiment with an external overlap cache:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/overlap-reference-prefilter/benchmark.py --cache /absolute/path/overlap.json --samples 7
```

The harness retrieves the predecessor script from pinned reachable main
`721c03822c421b7f7fcbb2598993b947c4d88419`. It executes both complete commands
with the current shared dependencies and same stable checkout, compares every
report, and verifies the cache was unchanged. Keep the checkout stable while it
runs. It writes temporary baseline source beside the external cache and removes
it on exit. Full Git history and Git on PATH are required for this optional
benchmark. No network access is used. Timing is not a CI acceptance threshold.

## Limitations

The historical cache is hash-identified, not vendored. A fresh cache is a new
workload; the exact recorded timing cannot be reconstructed from this package
alone after that cache is removed. The verifier and actual CLI tests are fully
reproducible without it. The measured gain applies to a sparse checkout and a
reference-sparse task query. Literal-only queries receive no prefilter. A corpus
containing the reference number in nearly every text can pay an extra substring
scan, so no universal speedup is claimed.

## Open next questions

Does the same gain hold for other cards and a complete checkout? Run the same
harness on the intended immutable cache before changing another mechanism.
No additional optimization is part of this contribution. Native operators,
supplier correctness, compiler closure, ownership, precision, tape costs and
the complete multiplication theorem are not audited. Independent human and
formal proof-kernel review are unclaimed.

## Credit and implementation constraints

The existing overlap search retains Douglas Colkitt and its other contributors'
credit. Nick Petalas's [PR3002](https://github.com/CrocSwap/integer-mult-bounds/pull/3002)
supplies the numeric-reference rules; Ali Romman's
[PR5736](https://github.com/CrocSwap/integer-mult-bounds/pull/5736) supplies Unicode
excerpt positioning. Their source notices remain unchanged. Literal prefiltering is a standard optimization;
the contribution is its integration, complete-command measurement and controls.
New work is Apache-2.0.

Build the Lever produced `benchmark.py` and `verify.py`. Prove It Works required
complete report equality rather than matching only result counts. Explain the
Number required separate profiles, seven alternating pairs, zero-error checks
and the complete command as the timed unit. The autonomous local run playbook
stopped optimization at the first measured improvement.

Power of Ten rule 3 deviation: Python allocates managed objects. The deterministic
verifier is bounded by six word lengths over seven symbols, two terms and 289
records. The optional benchmark caps its cache at 64 MiB, samples at fifteen and
each subprocess at sixty seconds. Rule 8/9 deviations are limited to loading the
one declared source module, patching its one helper for comparison, and executing
the two explicit complete command sources. Their names and lifetimes are fixed.
All added functions fit within sixty lines, use bounded iterations, and retain
explicit checks under `-O`. Unchanged discovery/network functions are outside
the modified path. Warning-strict checks run in both modes; no compiler or new
global analysis configuration is introduced.
