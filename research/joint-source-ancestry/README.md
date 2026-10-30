# Joint publication source ancestry

The complete publication byte/history preflight takes **34.2% less time** on the
unchanged `research/e8-d0-root-swaps` fixture: median **0.2425745 s to
0.1596787 s**, with the same complete receipt. This is a verifier-engineering
improvement with a scoped equivalence proof and empirical timing certificate.
The command is opt-in; it shares the original byte/mode checker and supplies a
new source-history implementation under this package.
It changes no mathematical research result, supplier or kappa.

The fixture has 14 files and five distinct source commits. Seven alternating
fresh-process pairs all pass. Baseline times range from 0.2377195 to 0.2460621 s;
changed times range from 0.1546250 to 0.2043218 s. The generated
[BENCHMARK.json](BENCHMARK.json) binds both implementation hashes, the complete
receipt, every sample and the environment. Timings include interpreter startup,
argument parsing, file inventory, byte comparison and source-history checking.
They exclude fixture preparation and separate diagnostic profiling. This is
warm local filesystem evidence on a shared macOS arm64 host, not a universal
runtime guarantee or a multiplier speedup.

## What changes

The existing `--check-source-history` preflight resolves every distinct pin and
runs a separate `merge-base --is-ancestor` query for it. For multiple source
commits, the changed preflight first checks every exact object type with one
`cat-file --batch-check` request. It then evaluates:

```text
git rev-list --max-count=1 <all distinct source commits> --not <publication>
```

If the result is empty, all pins are ancestors. Otherwise it runs the original
per-pin checks for the existing first-failure diagnostic. Ordinary missing or
noncommit objects also take that original path, so a later invalid object does
not hide an earlier ancestry error. Malformed protocol responses, Git errors
and timeouts fail closed. The single-source path remains the original path.

On this fixture, source-history Git calls fall from 13 to 5. Separate profiles
in the generated evidence identify subprocess waiting as the dominant baseline
cost. The source-history portion occupies about 65% of the profiled complete
check; removing eight processes is consistent with the measured end-to-end gain.
The profiles are diagnostic observations, not timed samples.

## Scoped equivalence proof

Let `A(c)` include commit `c` and all its ancestors in the stored Git graph.
For exact commit pins `p_1,...,p_k` and publication `h`, the revision expression
above enumerates

```text
(A(p_1) union ... union A(p_k)) minus A(h).
```

This set is empty exactly when every `p_i` belongs to `A(h)`. In one direction,
each pin belongs to its own ancestor set. In the other direction, ancestry is
transitive, so every ancestor of a pin that belongs to `A(h)` also belongs to
`A(h)`. Limiting enumeration to one commit preserves emptiness. The type batch
requires the returned object ID to equal the literal pin and its type to be
`commit`; an annotated tag cannot silently stand in for its peeled commit.
This equivalence assumes a stable graph and completed, successful Git queries;
resource failures still reject.

Only that positive result bypasses the old loop. Ordinary negative answers run
the unchanged loop in sorted order. Both paths use committed metadata, reject
shallow history, disable replacement objects and grafts, and retain the existing
Git environment isolation and 30-second per-command timeout. No new ref, index
or repository mutation is involved. Corrupt Git graphs and hostile Git binaries
are outside the original and changed contracts.

The written argument concerns acceptance in the stated finite Git graph; the
tests exercise concrete positive and failure cases. It is not a formal-kernel
proof or a re-verification of the fixture's mathematics.

## Verification and reproduction

Run the optimized command from the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/joint-source-ancestry/preflight.py --package research/e8-d0-root-swaps --check-source-history
```

Verify and publish this package with:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/joint-source-ancestry
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/joint-source-ancestry/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/joint-source-ancestry --check-source-history
```

The registered normal and optimized commands compare the full real receipt and
run all 18 source-history tests through the adapter. The thirteen inherited
contract tests remain the original source; five new tests cover the joint path. They cover merged incomparable sources, duplicate
pins, foreign cached commits, missing commits, tags/trees/blobs, the first-error
ordering, committed metadata versus working drift, shallow history, replacements,
grafts, bounds, malformed responses, Git failures, timeout propagation and the
read-only CLI. They perform no scientific replay of the benchmark fixture.

To repeat the optional timing experiment, create a scratch directory outside the
checkout and pass its path:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/joint-source-ancestry/benchmark.py --scratch /absolute/external/scratch
```

The benchmark authenticates the baseline script against its provenance pin,
replays that exact module with its original import/root context, and compares
complete receipts from both CLIs. It needs full Git history and the materialized
14-file fixture. It writes temporary files only under the supplied directory and
removes them. The registered verifier does not enforce host-dependent timings.
The generic replay and publication preflight themselves require Git; this package
does not promise a Git-free export. No Lean, Docker, selected cold supplier replay
or complete multiplication theorem was run or claimed.

## Resource bounds and inspection

The existing limits remain 100,000 metadata rows, 256 distinct source commits
and 16 MiB of source metadata. New loops traverse at most 256 pins and four
object kinds. A batch request contains at most 16,640 bytes for 64-digit IDs;
normal replies contain at most 18,688 bytes. Joint reachability emits at most one
commit ID, with a 30-second timeout. Rejection can add two Git commands before
the original loop and can therefore be slower. A large-history joint walk might
also be slower or time out when individual commit-graph checks would pass.

New functions remain under 60 physical lines and use structured, nonrecursive
control flow. Python allocation is a managed-runtime deviation from fixed-memory
operation; pin counts, request/reply sizes and benchmark sample counts bound the
new retained collections. The benchmark's dynamic execution is limited to the
exact hash-authenticated baseline module; it preserves that module's CLI context.
Normal and optimized tests run with warnings treated as errors.

## Open next questions

Does shared traversal still help on real publications with 32 to 256 distinct
source commits and much larger histories? Alternate the complete CLI paths on
such a publication, keep exact receipts and rejection controls, and profile the
remaining work. A representative publication and a separate measurement budget
are needed. No broad performance claim follows from the five-pin fixture.

## Credit

This contribution was produced by Nick Petalas. The publication preflight,
source-history policy and immutable Git reader retain their existing attribution,
including ywz65, Nick Petalas, roger-sato, Arham Tahir and Douglas Colkitt.
Conorholds's root-swap package and all its predecessor mathematics remain their
authors' work; only its existing file/history inventory is used as a timing
fixture. New work is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
