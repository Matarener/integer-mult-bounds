# Validation and implementation limits

The complete registered replay passed locally on CPython 3.12.15 on 2026-10-18.
Optimized scientific and Git-free committed-byte checks are recorded in the
publication handoff. These are author checks, not hosted CI or human review.

Scientific checks use Python 3.12+ and the standard library. VERIFY.json registers
the complete new census, the unrestricted small oracle, literal dirty controls
and three behavioral test groups. All commands use warnings as errors. Direct
optimized replay retains every scientific check because none uses Python assert.
The exact receipts are RESULT.json and CHECKS.json. Normal replay changes neither.

## Exact coverage

The five-source census checks 145,080 paired-source assignments and 1,401,120
exceptional-source assignments. It compares every coverage-histogram bin with
PR2208's pinned receipt using the proved factors 12 and 13. The six smaller
domains include positive cases; they are not substitutes for the five-source
exhaustion. Ordered digests cover each word, cut, physical port assignment,
paired-mask bitset and exceptional-output repair decision in deterministic order.

The independent small oracle checks 116,400 unrestricted port bitstrings and
both transfer orientations. It matches all 2,796 restoring cases, full observation
sets and complete two/three-read masks. Its word generator enumerates all labelled
strings and filters counts and source-label symmetry afterward. The main generator
instead builds perfect matchings and solves source restoration before replay.

Four complete words pass 552 forward/inverse pairs, covering every dirty basis
column and one mixed state at widths 1, 2, 3. The five-source 74-call and 78-call
fixtures remain credited predecessor constructions. The new two-source fixtures
have exactly one three-read output or exactly one three-insertion source.
All 178 single-call deletions and 178 port/direction changes reject. Three
out-of-domain requests reject. These finite matrix controls do not prove an
all-size supplier theorem.

Three behavioral groups inject an actual faulty restoration producer and an
actual faulty query producer, corrupt an input, exceed the one-MiB input bound,
alter the result receipt, and run optimized relocated dirty controls without Git.
They check unchanged export bytes and copy files into distinct inodes without
chmod. All subprocesses have 120-second bounds and checked return codes.

The original native two-transfer domains were freshly compiled with C++17,
`-O3 -Wall -Wextra -Wpedantic -Werror`, then run with arguments `2 0` and `2 1`.
Every histogram bin matches its existing receipt, at 1,740,960 and 18,214,560
assignments respectively. No new native algorithm is claimed; this is an actual
replay rather than receipt binding alone. The unrelated four-transfer native
and six-source domains were not rerun.

To repeat that optional native cross-check, choose an owned external output
directory and compile the pinned unchanged source:

```sh
c++ -std=c++17 -O3 -Wall -Wextra -Wpedantic -Werror \
  research/bidirectional-connector/census.cpp -o "$AUDIT_OUTPUT/census"
"$AUDIT_OUTPUT/census" 2 0
"$AUDIT_OUTPUT/census" 2 1
```

On macOS an explicit compatible `-isysroot` may be needed. The author run used
Clang and the SDK reported by `xcrun --show-sdk-path`. This compiler is not a
runtime dependency of the new standard-library registered replay.

## Diagnostics and engineering decisions

Build the Lever led to a runnable exhaustive checker rather than a claim based
on a stored predecessor receipt. Prove It Works required full-histogram agreement,
a separate brute oracle and actual faulty-producer rejection. Boundary Discipline
put byte/resource checks at JSON and subprocess boundaries.

Power of Ten inspection of the five new Python files found no recursion or
unstructured jumps. Every scientific loop has an enforced finite domain: at most
five sources, 17,325 source words, twelve phase cuts per word, 48 restoration
choices per cut, 32 source masks and two roots. A single maximal-domain census
therefore has the conservative upper bound 9,979,200 candidates. Actual counts
are lower. No complete candidate history is retained; hashes are incremental.
The independent oracle uses at most three sources and seven source events.
Dense checks have at most 38 rows of width three. JSON/input reads are capped
at one MiB, source manifests at 32 entries and native receipt rows at sixteen.
The longest new function is 49 physical lines after formatting.

Root restoration, source-domain capacities, full histogram agreement and exact
endpoints use always-enabled ValueError contracts. The fault controls exercise
them under optimized Python. File handles and temporary exports have scoped
cleanup; subprocess failures propagate or are explicitly expected and checked.
Mutable roots, counters, hashes and test substitutions remain local. There is
no dynamic evaluation or generated code. Scientific operations have direct call
targets. Historical/native sources are not modified to satisfy local style rules.

Rule 3 deviation, managed allocation: Python necessarily allocates tuples,
integers, dictionaries and JSON objects during the census. Preallocating every
runtime object is unavailable in this execution model. The enforced domains
bound all live collections: at most 17,325 eleven-label words, 33 histogram
bins, 48 port choices per cut and four 32-bit reader sets. Temporary source and
JSON buffers are at most one MiB plus the one-byte overflow probe. The oracle's
set rows contain at most five symbols and observations number at most twenty.
Verification checks the capacities, maximal five-source domains and overflow
failure. A native port would need its own fixed-capacity implementation and
independent replay before replacing this checker.

Rules 8/9 deviation, test dispatch: standard unittest discovers three named test
methods, and unittest.mock temporarily replaces two explicitly named producers.
These are required to exercise actual producer failures, not part of scientific
enumeration. Context managers restore both targets on success and failure.
The three test groups pass under normal and optimized Python.

Local static diagnostics use Ruff 0.17.1, target Python 3.12, with
`E,F,I,B,UP,SIM,RUF,C4,PIE,PERF,PTH,RET`, plus formatting and warnings-as-errors
execution. All selected checks pass without suppression. Python allocation and
standard test dispatch deviations above remain explicit. No native build,
formal proof-kernel check, hosted CI or independent human review is claimed for
the new Python package. The fresh predecessor native replay is stated separately.

## Publication checks and remaining obligations

Before publication, run the registered replay, optimized direct commands,
metadata/source pins, exact committed-byte/source-history preflight and Git-free
replay from an export of committed bytes. Package-local files plus the five live
inputs suffice for direct scientific replay. The original task catalogue and
selected record are pinned historical provenance for metadata checks.

This check does not discharge the original 72-map exclusion, a caller's
nonuniform port prices or the complete physical/recursive bill. Selected source
binding and the original card's 945-pairing positive control were run as
orientation only. No full selected cold replay, Lean or Docker run was performed.
