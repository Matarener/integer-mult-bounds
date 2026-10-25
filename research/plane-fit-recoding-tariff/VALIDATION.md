# Verification record and bounded-code review

The mathematical theorem is the written weighted spanning argument in PROOF.md.
The finite checkers validate its source-bound P112 instance and failure modes.
They do not provide formal-kernel or human review of the proof.

## Executed checks

The session used canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. The selected
binding baseline printed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` after its declared
source roots and proof supplements were materialized in the worker's sparse
checkout. This was an orientation check, not the selected cold replay.

The Python 3.12 registered package replay, Python 3.15 optimized direct replay,
separate checker, seven behavioral groups and read-only Git-free export passed
locally. Their exact commands and results are recorded in the session final report. The public commands are in README.md and VERIFY.json.
The verifier checks its committed RESULT.json; it never regenerates that receipt
on a default run. No floating-point arithmetic, randomized result or performance
measurement enters the evidence.

The work counts have independent definitions: 65,535 is every nonempty subset
of sixteen groups; 37,632 is three fields times 112 squared factorization
entries; 264,864 is 496 support pairs times 534 invertible two-by-two matrices.
All runs must report zero errors and the same mathematical receipts. Finite
recoding checks corroborate the calculation, while the determinant proof covers
all fields and all finite spanning query lists in the named row space.

## Code review

All new scientific code is in this package. The proof instance reads one
hash-bound selected input and one byte-for-byte retained certificate. No shared
verifier, frozen predecessor, selected record or supplier is changed. Functions
are below sixty physical lines after formatting. Exceptions preserve ownership;
no checker deletes source files. Test scratch belongs to TemporaryDirectory,
which removes it on success and failure. Every subprocess has a thirty-second
timeout, captures its result and checks the return code.

The primary checker has no recursion. Gaussian elimination loops are bounded by
nine label coordinates or a maximum of 64 queries with 32 coefficients each.
The closure loop has exactly 65,535 iterations. Geometry loops use 112 ports,
sixteen groups and groups of at most eight ports. The separate dense elimination
uses at most 112 rows and columns. Its recoding census explicitly enumerates
three fields of size at most five, 496 pairs and at most 480 invertible matrices
per field. The controls have seven named test groups and four CLI mutations.

`need` and `check` are executable invariant guards, rather than Python asserts;
optimization does not remove scientific acceptance checks. Invalid source hashes,
duplicate ports, false receipts, rank-deficient queries and queries outside the
named row space are rejected. The primary reads at most 2 MiB for selected JSON,
32 KiB for metadata/certificate and 16 KiB for its receipt. Coefficient and label
bounds are checked before scientific elimination. All introduced zip operations
require equal lengths.

Ruff 0.17.1 checks E,F,B,SIM,I,UP,PLW and formatting, with no local suppressions.
Python runs with `-Werror`. An exploratory all-rule lint scan also identified
optional annotation/docstring, magic-constant, print, executable-header and
pytest-style advice. This package keeps explicit mathematics, JSON receipt
printing and standard-library unittest, consistent with its dependency-free
replay. It does not claim that mutually incompatible all-rule style policies
passed. Git's SHA1 blob identifier is explicitly marked non-security use;
SHA256 independently authenticates the source bytes.

## Power-of-ten deviations

Rule 3, allocation. CPython and JSON parsing allocate during checking. A ban on
runtime allocation is incompatible with the standard-library Python replay.
The scope is the bounded package run. Live scientific state is bounded by the
2 MiB input, 112 nine-bit labels, 65,536 closure slots with bases of at most nine
labels, a cache with at most 65,535 keys, and matrices of the dimensions above.
The separate checker never stores the recoding census. Controls use one private
copy at a time and delete it. No claim about allocator-level fixed memory is
made. A fixed-buffer implementation would be a separate proof-engine project.

Rule 9, callbacks. Standard-library unittest dispatch and the four private
mutation functions are indirect calls. Their targets are the seven named tests
and four functions in test_package.py, their lifetimes are one bounded test run,
and subprocesses execute only the current interpreter and a private copied
verifier, with no shell. Normal and optimized test/export replays verify their
cleanup and failure behavior. Scientific checkers use direct calls.

Rule 10, recurring analysis. The repository package hook runs the three declared
commands with Python warnings treated as errors. Ruff is an additional pinned
publication check, not a new package runtime dependency. Registering a global
lint policy or adding an external tool to every mathematical replay would
expand this isolated theorem's scope. No repository CI policy is weakened.
If the repository adopts package linting, include these files in that separate
policy change. The remaining all-rule style advice is not suppressed in code.

## Unrun obligations

No selected cold replay, Lean build, native lowering, full physical bill,
all-size/compiler argument, larger query-space optimization or arbitrary-fitting
search is performed. The inherited selected assumptions remain unchanged.
No new multiplication exponent or selected-frontier update is claimed.
