# Engineering contract

The falsifiable predicate is exact circuit/header bits, agreement with the independent closed primitive/storage formulas, borrowed bytes and all heads restored, both private tapes blank, and rejection of intended optimized CLI faults. The accepted change is one supplied binary-program interpreter. The main checkout, frozen inputs and selected frontier are outside its write scope.

Foundational Thinking led to canonical counter width, which makes zero detection local to the decremented top bit. Subtract Before You Add removed the now-unused full-width is_zero routine. Build the Lever led to the rerunnable machine, independent invoice and actual CLI controls. Prove It Works requires final committed-byte/history gates and scientific/control execution from the actual Git-free export. Separate Before Serializing Shared State gives each worker its own package/outputs and serializes only shared Git and reservation mutations with short OS advisory locks.

## Power of Ten inspection

1. The changed call graph has no recursion. Every success path returns its owned heads and private storage. Host rejection precedes tape construction. Interrupted/corrupted running-state rollback is outside the contract. Private control trees use scoped temporary directories and bounded, waited subprocesses.
2. Every machine scan is bounded by an allocated extent. The outer opcode loop is bounded by program length, at most 200,000. Traversal is bounded by wire cells, at most 4,098. Binary-field admission is bounded by 14 iterations. Direct access cases cover 1,024 fixed indices. Generic and header cases have fixed finite shape/seed/address lists. Controls have eight faults and one retry, each CLI limited to 300 seconds. The replay manifest allows 300 and 600 seconds, within the 1,200-second package total.
3. Machine tape extents are fixed before execution and the exact sum is checked. Only current-head read/write/unit-move accesses occur in machine routines. Python allocations and count objects are covered by the deviation below. Control copying caps 64 files and 1,000,000 bytes per source, each copied exclusively to a distinct inode. There is no mode copying or chmod.
4. Each new function is below 60 physical lines. The largest responsibilities are host admission, scientific case traversal and CLI controls. AST lengths are recorded by the session checks.
5. Contracts use explicit ValueError checks and stay enabled under -O. They enforce input domains, bounds, unit moves, write permission, copy identity, exact invoices and full restoration. Meaningful invariants replace decorative assertions.
6. Every Tape owns its cells, head and counters. No global mutable tape state exists. Borrowed writes are forbidden at the cell boundary. The interpreter retains only the current opcode/Boolean operands and counter scan flag as logical finite state.
7. Invalid shape/program inputs fail before construction. Returned process status and intended failure text are checked; valid retry must pass. Byte copy writes and hashes are checked. Scientific/control exceptions propagate. A rejected mid-execution mutant has no restoration guarantee and cannot be mistaken for an accepted result.
8. Authenticated loading of one pinned canonical Python module is the bounded deviation below. No source string is generated from program input. Binary circuit encoding generates data, not executable code.
9. Tape methods directly access the current head and do not dereference a decoded wire index. Ordinary Python class/stdlib dispatch remains under the bounded deviation below. There is no plugin registry or dynamically selected caller.
10. Verification uses CPython 3.12 with -I -Werror -B, plus deliberate -O controls. Scoped Ruff E4/E7/E9/F, AST lengths, metadata, whitespace, source/history and export checks are required before publication. The existing opt-in workflow runs this package's registered checks on its package/input changes. No repository-wide lint/config migration is introduced.

## Explicit deviations

Rule: 3, fixed memory before steady operation.
Location: machine.py, checks.py and test_controls.py.
Reason: CPython creates integer, tuple, iteration and exception objects during interpretation and verification.
Scope: The bounded admitted domain and fixed verifier cases only. This is not a no-allocation Python implementation.
Compensating control: At most 200,000 program symbols, 4,096 wires and at most 66,666 outputs; counter width at most 12. All five cell arrays are allocated before execution. Control copies have explicit file/byte/subprocess bounds and scoped disposal.
Verification: Exact allocated-cell formula on every successful case, resource rejections, actual private-copy controls and source/export before/after identities.
Follow-up: A native implementation would need preallocated instrumentation/counter objects and allocation measurement; this is required before a no-allocation runtime claim.

Rule: 8, restrict metaprogramming.
Location: checks.py sources.
Reason: The canonical source is a separate hyphenated research package; ordinary imports could reuse unauthenticated bytecode or require modifying its frozen package.
Scope: Exactly research/synthetic-twiddle-circuit/circuit.py after authenticating all three declared live inputs.
Compensating control: Resolve a fixed path, check regular/nonlinked file and SHA256, compile retained source bytes directly, use a fresh ModuleType. No program-supplied path or code is evaluated.
Verification: Changed/missing source CLI controls, registered replay and Git-free export replay.
Follow-up: A source loader with equivalent isolation can replace this when a shared canonical library exists; no frozen module refactor is included here.

Rule: 9, indirect runtime dispatch.
Location: Tape methods, dataclass construction and subprocess/stdlib calls.
Reason: Python method and stdlib dispatch is intrinsic to this executable model and its verifier.
Scope: Five known Tape objects, one authenticated circuit module, standard-library helpers and one fixed verifier CLI per control.
Compensating control: No numerical operand is used as a Python list index in execution; the only cell index is the tape head. No uncontrolled callbacks or arbitrary command dispatch.
Verification: Source inspection, exact primitive formula and semantic/count/head/erasure CLI mutants.
Follow-up: A production tape-library lowering must preserve the same cell access and lifecycle contracts rather than assume Python dispatch is a physical implementation.
