# Engineering scope

Build the Lever led to a runnable sequential data program and exact integer
oracles. Prove It Works led to real optimized CLI semantic corruptions and a
Git-free committed export replay. Separate Before Serializing Shared State led
to one owned worktree/branch/output directory, process-held ownership locks and
short shared Git/reservation advisory locks. No extra worker or checkout was
created. The original failed replay diagnostics remain external to the package.

Power of Ten inspections cover packets.py, checks.py, verify.py and
test_controls.py. Calls are acyclic; every iteration uses a bounded extent or a
fixed finite test domain. n<=128, r<=64, w<=128 bound live data to 4,227,200 cells
across input, output and three scratch roles at the simultaneous maximum.
Every read/write checks the data extent; source copying checks the binary
alphabet. Packet extents,
non-overflow words, distinct source/owned buffers, exponent ranges and output
consumption are executable contracts, active under optimized Python. Every
function is below 60 physical lines. Started failures have explicit finally
cleanup. CLI subprocesses have a 120-second timeout and propagate their exits.

Rule 3 deviation. CPython allocates arithmetic objects, iterators and oracle
lists during execution. The five data tapes have fixed bytearray capacities;
the program does not grow them. Test domains and input extents bound live
memory. This is not an allocation-free native runtime. A future native/encoded
port must preserve the same extents and prove its allocation boundary.

Rules 8 and 9 deviation. verify.py loads exactly two authenticated canonical
Python inputs and the two fixed package modules by explicit file paths. The
third authenticated input is the retained proof text. The packing and layout
modules have no nonstandard imports or transitive local imports. Package-local
bytes are bound by the commit/export gate. The loader is needed for hyphenated
package directories and isolated direct execution. CLI controls use an
inode-disjoint source-only copy and no bytecode cache. No generated code or
eval strings are used. A native port can replace this bounded loader with its
ordinary module mechanism. The test driver passes module objects with fixed
call targets to keep independent oracles explicit.

Rule 10 deviation. Diagnostics are scoped to the new Python package. Replay
uses -Werror; Ruff E4/E7/E9/F is run without cache. Repository-wide lint/type
policy and frozen predecessor code are not changed. All arithmetic in the
scientific path is integral or Fraction, with no floating tolerances. No CPU
performance result is claimed; data ticks are exact interpreter operations.

The theorem ranges over all finite parameters, while this interpreter has
deliberate capacity limits. Header arithmetic and loop counters are host
control, not an encoded fixed-tape implementation. Extending those limits or
promoting a complete caller requires a new bounded replay and a control/storage
invoice. The current five-data-role statement does not hide these obligations.
