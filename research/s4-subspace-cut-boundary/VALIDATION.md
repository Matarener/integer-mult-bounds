# Verification scope and bounded code

The primary checker authenticates three unchanged source texts by SHA256.
It executes no predecessor source. SOURCES.json and the registered replay
also bind their exact Git blobs and the historical task catalogue. Live
overlap is coordination evidence, not a mathematical input.

Membership hashes concatenate sorted subspace membership bitmaps in
little-endian order, two bytes per natural subspace and eight per edge
subspace. Bit x means that binary coordinate vector x belongs to the space.
Each seven-entry profile lists the three generators followed by four targets.
The separate checker compares the full inventory, not just the optimum.

Local commands use CPython 3.12.15:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/s4-subspace-cut-boundary
python3.12 -I -O -Werror -B research/s4-subspace-cut-boundary/verify.py
python3.12 -I -O -Werror -B research/s4-subspace-cut-boundary/independent.py
```

Six behavioral groups include actual optimized CLI rejection of an incomplete
coordinate-only inventory, a wrong target, a too-small middle dual coefficient,
counterfeit and over-size source bytes, false and Boolean-aliased receipts,
duplicate keys and nonfinite JSON. Positive Git-free replay retains all source
pins. Tests remove their owned copies. Use an external TMPDIR for scratch.

Selected source-binding baseline passed. No selected cold replay, full word
search, supplier admission, Lean, Docker, human review or hosted-CI pass is
claimed. Publication bytes/history and committed Git-free replay are separate
publication checks recorded in the session report.

## Engineering constraints

Build the Lever changed the deliverable into two rerunnable exact checkers.
Prove It Works required complete inventory agreement and actual mutated CLIs.
No extra agent or checkout was used.

Power of Ten inspections cover three new Python files. There is no recursion
or dynamic execution. The primary loop has at most six stages, 2,825 spaces
and 64 vector choices. Intersection sets have at most 64 elements. RREF has
at most nine free binary entries or four free F5 entries, 2,825 emitted bases
and seven rank calls per basis. Elimination has at most twelve rows and six
columns. Functions remain under sixty lines. Explicit exceptions preserve
checks under optimized Python. Returned subprocess status is checked.

Rule 3 deviation, managed allocation: Python allocates sets, integers, lists
and JSON objects during enumeration. Fixed input domains bound mathematical
data to 2,825 sets of at most 64 vectors, their bitmaps and a finite profile
histogram. File reads are bounded at 128 KiB. Tests use one owned temporary
package at a time and a sixty-second timeout per child. Interpreter/library
allocator internals are not instrumented. Replacing the interpreter to
preallocate every object would exceed this package's scope. Before larger
modules are introduced, require new capacity bounds and exhaustion controls.
No physical RAM or runtime-performance measurement is claimed.

Rule 10 deviation, shared diagnostics configuration: this isolated package
does not change repository-wide CI or analyzer settings. Its registered
commands use warnings-as-errors, and optimized controls exercise failures.
Ruff checks/formatting cover all three new files with outputs retained in
the session record. No diagnostic suppression is introduced. Revisit shared
configuration only as a separately scoped repository tooling change.
