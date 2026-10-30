# Engineering decisions

Build the Lever led to circuit.py and the committed exact replay. Prove It Works led to the actual optimized CLI corruptions and final committed-byte/Git-free checks. Separate Before Serializing Shared State led to a private package, outputs and ownership holder, with short shared Git and reservation locks.

The executable surface is compile_round followed by evaluate on a complete tuple of literal bits. A Circuit has immutable slot, gate and output tuples. Boundary validation rejects Boolean values used as integer dimensions or indices, malformed extents, forward wire references and unsupported opcodes before evaluation. The bit arithmetic has no integer exponent operation. encode_address/decode_word are boundary adapters used by checks.

Power of Ten inspections found no recursive call, background task, network operation, shared writer or unbounded input loop in the new scientific code. Bounds are ell<=256, axes<=64, input bits<=16384, gates<=100000 and output bits<=257. All loops iterate over these fixed extents or the stated finite verification domains. Subprocess controls have a 120-second timeout. Gate output cells are preallocated and cleared by finally on success or failure. Shape/output/gate invariants are ordinary exceptions and remain active under -O. Functions are kept below 60 lines after formatting. CLI status, copy writes, identities and subprocess outcomes are checked. Direct calls and shallow immutable tuple access retain visible ownership.

Rule 3, fixed memory, has a managed-runtime deviation in circuit.py and checks.py. Python allocates integers, tuples and interpreter objects; a literal no-allocation runtime is unavailable. Enforced finite extents bound live data, the gate wire array is allocated before the gate loop, and controls run bounded child processes. These are logical cell/circuit bounds, not measured interpreter heap bytes. The next physical lowering should use explicit fixed buffers and verify a runtime memory bill.

Rule 8, metaprogramming, has a bounded source-loader deviation in verify.py. The replay compiles exactly circuit.py, checks.py and the authenticated canonical physical.py from explicit local paths. It never evaluates caller-provided code or a bytecode cache. The dataclass decorator supplies the immutable record constructor and equality; there is one static Circuit type. A machine implementation should replace this host source loader with its fixed program image.

Rule 9, indirect calls, has the same bounded loader/module-namespace deviation. The possible scientific modules and call sites are fixed. checks.py receives exactly the newly loaded circuit module and pinned canonical physical module; there is no plugin registry or callback chain.

Rule 10 uses -Werror under CPython 3.12 and scoped Ruff E4/E7/E9/F on the new Python files. Those commands are recorded beside the final replay. No repository-wide diagnostics or frozen source rewrites are implied.

The source physical.py has existing nested butterfly/twiddle functions and uses indexed record arrays. This successor imports it only as a finite reference/join implementation. It does not make its indexed access a new physical-cost premise. The complete transform fixtures test the header substitution; the all-size arithmetic claim rests on PROOF.md.

Control exports use exclusive regular byte writes with owned-source lstat, destination UID and inode-disjoint checks. No copy2, copied metadata, chmod, symlink traversal or shared runtime mutation is used. Cleanup removes only the private TemporaryDirectory tree after its source bytes are restored. Session exports additionally retain actual pre/post hashes and identity receipts before removal.
