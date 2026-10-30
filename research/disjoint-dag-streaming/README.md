# Stream disjoint-tensor DAG hashes with lower allocation

This opt-in adapter reduces peak traced allocation during complete
`DisjointTensor(26).verify()` from **107,703,062 to 41,079,356 bytes**, about
**62%**, while returning the identical complete receipt. The historical
checker and its certificates remain unchanged.

Claim type: **tooling improvement with a scoped serialization-equivalence
proof**. This answers Open next question 1 of Wentao Li's
[PR #2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117).
It supplies neither a new mathematical construction nor a new kappa.

## What changes

The old checker builds every DAG row, a complete JSON document and its encoded
bytes before hashing. [accelerator.py](accelerator.py) emits the same compact
JSON bytes into bounded chunks and hashes them incrementally. It keeps a
static copy of the original `verify` body; only its final digest construction
changes. The registered check compares the entire function AST after exactly
that substitution, so a removed or weakened nondigest check is rejected.

[PROOF.md](PROOF.md) proves exact byte equality for the restricted
integer/tuple/null schema, gives a conservative 68,575-byte bound on each
emitted chunk, and explains sorting and managed-memory costs. The explicit
limits are one million array entries and 10,000 bits per support. This is an
opt-in bound, not a claim that all possible historical expansion budgets fit.
Source authentication runs before checker imports. Direct execution disables
old bytecode reads as well as new bytecode writes.

## Reproduce

From the repository root, using the tested CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/disjoint-dag-streaming
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/disjoint-dag-streaming/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/disjoint-dag-streaming/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/disjoint-dag-streaming --check-source-history
```

The interpreter path is host-specific; another CPython 3.12 installation can
run the same standard-library-only checks. Expected direct result:
`PASS_DISJOINT_DAG_STREAMING`, 1,623 schema fixtures, six complete circuit
receipts and 41 rejecting controls. Both Python modes run identical coverage.

To repeat the descriptive benchmark, choose an existing output directory
outside the checkout and run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/disjoint-dag-streaming/benchmark.py --rounds 5 --output "$disjoint_run_dir/measurements.json"
```

The benchmark refuses an output inside the checkout. Its generated JSON
contains samples, source hashes, environment, node counts, errors and full
receipts. Timing is not a CI correctness gate, and no generated log or export
belongs in the checkout.

## Evidence

The written equivalence proof is corroborated by all 1,617 length-zero-through-
two schemas with supports in `{0,1,2,3}`, every argument choice and active
subset; six large-integer fixtures extend through 10,000-bit supports. Four
chunk thresholds exercise flush and delimiter cases. Six complete circuits
cover `(h,k) = (4,1), (6,2), (6,3), (8,3), (10,3), (26,3)`. Both their actual
bytes and complete verification receipts agree.

The largest fixture has 60,372 active nodes, 57,772 additions, 2,600 inputs,
2,600 outputs and 4,604,600 nonzero coefficients. Its unchanged DAG digest is
`5da8011dadf51d6121d343416fa38b6b4bf524fd689e5b1b2def91324660f19b`.
Every value comes from an executed circuit. The contribution is the changed
encoder, not a re-audit or new proof of those predecessor circuit counts.

The 41 controls comprise 13 malformed schemas, four invalid chunk budgets,
five changed declared inputs, eleven deleted nondigest top-level statements,
and eight rejection calls on four corrupted actual circuits. The corruption
cases change a sum support, create a cycle, exceed the recurrence count and
change an output binding. The original and accelerated methods both reject.

## Measurements

CPython 3.12.15, macOS arm64, standard library only. Five fresh-process pairs
alternate order. Both sides build the same circuit and consume every result;
all full receipts agree and there are zero errors. Five traced-allocation
measurements per side give the same respective peaks. The table gives median
wall time with minimum and maximum in brackets.

| Quantity | Original | Streaming |
| --- | ---: | ---: |
| Digest peak traced allocation | 84,685,162 B | 691,046 B |
| Complete verify peak traced allocation | 107,703,062 B | 41,079,356 B |
| Digest wall time | 0.227564 s [0.226946, 0.229425] | 0.204584 s [0.203043, 0.224004] |
| Complete verify wall time | 0.322287 s [0.318810, 0.355722] | 0.299514 s [0.294348, 0.309523] |
| Construction plus verify wall time | 0.399820 s [0.397821, 0.433130] | 0.377585 s [0.371520, 0.388686] |

These are additional Python allocations after circuit construction, measured
with `tracemalloc`. They are not process RSS, retained circuit memory, or a
physical multiplier memory claim. Timing is measured separately with tracing
disabled. Construction-plus-verification includes circuit construction and the
complete checker, while import and source authentication are excluded equally.
The primary result is allocation reduction. The modest timing difference is
host-descriptive and is not a portable speed guarantee.

| Pair | Original verify s | Streaming verify s | Original construction + verify s | Streaming construction + verify s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.323283917 | 0.302542917 | 0.399819792 | 0.380593542 |
| 2 | 0.321335458 | 0.299513541 | 0.398702042 | 0.377585041 |
| 3 | 0.322286625 | 0.295842375 | 0.402609333 | 0.373650625 |
| 4 | 0.318810458 | 0.294347792 | 0.397820750 | 0.371520042 |
| 5 | 0.355722250 | 0.309522667 | 0.433130208 | 0.388685959 |

An untimed-in-the-report profile of the original verification spent 0.105 s
of 0.380 s in `compile`, 0.044 s in JSON encoding, and most remaining time in
the checker body, which includes decimal support conversion. These scalar
conversion and compile costs remain. The machine had 18 logical CPUs and
load averages 2.64, 3.55, 3.73 before the run; unrelated processes were active,
so order is interleaved. No other replay was run concurrently in this worktree.

## Scope and provenance

Canonical base is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision
8. [SOURCES.json](SOURCES.json) binds the four imported checker/dependency
files and the predecessor question. The selected record and original task
card are provenance only. Existing default sources, frozen certificates,
archives, selected frontier and predecessor credit are unchanged.

Live overlap included paginated snapshots of 379 open PRs and 5,784 Discussion
records, recent account contributions, the latest handoffs and active threads,
batch reservations, distinctive main README searches and merged-PR searches.
Sparse local notes covered 70 of 8,348 paths, so their omissions are explicit.
The relevant existing PRs #2001, #2039, #2117 and #2150 accelerate other paths
or leave this exact question open. No exhaustive novelty claim is made about
unpublished work or arbitrary historical diffs.

The complete selected supplier, full historical audit suites, Lean, Docker,
native costs, all-size compiler, precision/tape, erasure and exact-recovery
obligations were not rerun or discharged. This package does not change a
mathematical result or supplier admission.

## Open next questions

1. Can the default checker adopt this encoder while preserving historical
   source bindings? Specify the source-pin migration and retain old evidence
   first. Default adoption is outside this opt-in package.
2. Can the remaining compiler allocation be reduced while preserving every
   physical embedding and freshness check? Start with its users, edges, gates
   and values. A streamed compiler needs a separate ownership argument.

The structured questions, first steps and blockers are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Douglas R. Colkitt authored
the retained disjoint-tensor and reversible-embedding checker. Wentao Li
[@VictorLiwentao](https://github.com/VictorLiwentao) supplied
[#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001),
[#2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117), the explicit
serialization question, and earlier byte-preserving formatter precedents.
Stephan Arrington's [#1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044)
supplies the retained frame-union lineage. Incremental SHA256 and compact JSON
are standard techniques. The new contribution is this exact bounded-chunk
encoder, its source-bound application and the measured allocation reduction.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
