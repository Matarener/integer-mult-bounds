# Defer publication mismatch digests

This contribution was produced by Nick Petalas.

The complete publication preflight is about 12% faster on the measured large-input
fixture after deferring two diagnostic SHA256 digests until a byte mismatch.
This is a measured verifier improvement with a scoped equivalence argument,
not a finite mathematical certificate or a new multiplication theorem. No new
kappa is claimed.

The production change is one conditional in `scripts/check_research_commit.py`.
Python previously evaluated the mismatch message before calling `require`, even
when `working == committed`. The message hashes both buffers. The changed code
compares those same buffers first and constructs the same message only on failure.

## Equivalence argument

If the buffers agree, both versions continue to the next file. The old version
also computes two digests that cannot affect the equality decision. If they
differ, both raise `ValueError` with exactly the same filename, working digest,
committed digest and punctuation. The surrounding `closing(git_blobs(...))`
context still closes the reader on failure. Successful iteration still advances
the reader through its final Git exit-status check.

Inventory, literal path spelling, regular-file requirements, optional executable
modes, committed source metadata, raw ancestry, replacement/graft isolation and
resource bounds are untouched. The comparison remains exact byte equality;
digest equality never decides acceptance. As with the original command, the
checkout must stay stable during a check. Exceptional failure of the SHA256
implementation itself is outside the equivalence claim on successful comparisons.

## Measured evidence

Canonical base is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
The unchanged `research/physical-gaussian-core` fixture supplies 42 compared files,
54,975,541 bytes and two declared source commits. Its mathematical verifier was
not run. Every timed sample runs the complete byte/history preflight through
`check(..., check_source_history=True)` in a fresh interpreter, including imports,
all Git subprocesses, exact comparison and the full returned receipt.

Ten alternating trials per side on CPython 3.12.15, macOS arm64 gave:

| Implementation | Median | Range |
| --- | ---: | ---: |
| Original | 280.56 ms | 277.11 to 300.94 ms |
| Deferred digests | 246.91 ms | 241.00 to 256.76 ms |

The median reduction is 11.99%. All 20 complete receipts are byte-identical,
with zero command errors. Both sides use the same shared reader, fixture,
flags and warmup. The host has 18 logical CPUs; the recorded initial one-minute
load is in the generated benchmark receipt. Other processes were running, so
the sides alternate. These are warm-filesystem timings, not cold-disk or
cross-platform performance claims.

An untimed complete-command profile attributes 34 ms of 274 ms to SHA256 and
133 ms to subprocess calls. Removing 84 diagnostic digests is consistent with
the observed 34 ms saving; Git and file transport still limit the command.
The generated JSON receipt binds both implementation hashes and records every
sample, host details and the complete common stdout. It is retained in the PR
body; reproduction writes a new receipt only into the requested scratch directory.

The focused verifier runs 36 actual Git regression tests. Two new tests require
zero successful-comparison digests and the exact mismatch message, two mismatch
digests and reader closure. The no-digest test rejects the original implementation.
Existing controls cover normalized/binary bytes, working drift, missing files,
inventory changes, literal wildcard/Unicode paths, committed links, reader final
failure, immutable objects, source-history failures and executable modes.

## Reproduction

From the repository root, use the same interpreter for both sides:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/lazy-publication-digests
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/lazy-publication-digests/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/lazy-publication-digests --check-source-history
```

The registered commands run normal and optimized Python with warnings as errors.
They exercise transport contracts, not the predecessor package's mathematics.
The test fixtures are temporary synthetic Git repositories, not research checkouts.

For timing, materialize `research/physical-gaussian-core` and all paths in its
`VERIFY.json` before running. Full Git history and the pinned base are required.
Pass an absolute scratch directory outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/lazy-publication-digests/benchmark.py --scratch-dir "$RUN_DIR" --rounds 10
```

`RUN_DIR` names a directory selected by the reviewer. The benchmark writes the
unchanged baseline script and `benchmark.json` there, never into the checkout.
Source provenance is in `SOURCES.json`; current implementation/test changes are
declared replay inputs in `VERIFY.json`.

## Scope and engineering choices

The autonomous local run playbook stops at this first measured improvement.
Build the Lever supplies the reproducible complete-command benchmark. Prove It
Works requires complete receipts and real Git rejection tests. Power of Ten
keeps the production edit to one existing comparison and bounds the benchmark
to 5 through 30 pairs with a 60-second timeout per subprocess. Python allocation
and the existing input-size-dependent checker loops remain managed-runtime
deviations; this change introduces no buffer or new production loop. The
benchmark deliberately imports exactly the selected before/after implementation
files to use the same complete API, rather than modifying either source.

No native replay, supplier admission, physical machine implementation, selected
frontier replay, formal proof-kernel check or independent human review is claimed.
Timing on small packages or another host may show little benefit. A complete
multiplier and the five retained framework assumptions remain outside this work.

## Open next questions

How much does deferred diagnostic work save across a representative publication
workload, including small packages? This matters because fixed Git overhead can
dominate. First choose a fixed package list and preserve every complete receipt
under alternating trials. A representative workload and a separate measurement
budget are needed. The structured question is in `TASK.json`.

## Credit and coordination

Credit ywz65's publication comparator, Nick Petalas's earlier source-history
preflight, roger-sato's immutable-object isolation, Douglas Colkitt's source
reader/runner and the retained executable-mode and reader-cleanup contributors.
The Gaussian package is only an unchanged transport fixture; its contributors
retain its mathematical and implementation credit.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19246971).
The concurrent joint-ancestry and committed-metadata-reuse claims change separate
preflight stages. Their performance is not measured here. Apache-2.0.
