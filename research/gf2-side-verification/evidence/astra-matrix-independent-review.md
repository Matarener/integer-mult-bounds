# Independent static review: bounded packed GF(2) side verifier

Reviewed 2026-10-27, against the frozen stage
outputs/c-verification-all-opportunities-20261027/stages/matrix-qualification-v1.
This reviewer only read source and wrote this report. No compiler, import of the
reviewed modules, numerical run, timing, browser, Git operation or dispatch was
performed. The parent owns the sole serial runner. No measured source was edited.
The rational nomination remains closed; this separate H=25 side workload does
not contribute a PR5864 improvement or reopen mathematics.

## Decision

**No blocking C memory-safety, integer-width, field-semantics or complement-order
error found in the supported finite domain.** The implementation is a plausible
source-faithful optimization of the frozen side checks, supported by substantial
finite independent validation. The parent must still determine complete measured
performance from its retained outer receipts.

Two concrete evidence/binding limits require either narrow documentation or a
separately frozen repair. Neither is evidence that a freshly loaded, unchanged
H=25 measurement is numerically wrong:

1. The runtime guard authenticates function code and the ownership of the globals
   dictionary, but does not authenticate all resolved globals/builtins, and it
   is not rechecked after installation. It does not establish arbitrary live
   runtime-drift equivalence or dynamic fallback.
2. The three complete hashes and native call count do not compare every ordered
   complement result. They cover complete structural/label/role witnesses and the
   complete Gram rank transcript. Complement order has a direct source argument
   and finite exact comparisons, not a full complement transcript.

Do not silently broaden either boundary in a release note. If stronger claims
are required, freeze changed instrumentation/guards separately, retain the old
samples and charge their cost before a new complete comparison.

## Inputs and pins

Inspected native_gf2.c, native_backend.py, finite_controls.py,
compare_side_verifier.py, profile_side_verifier.py and both files under source/.
The frozen source pins in the stage are:

- complex_circuit.py:
  d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1;
- complex_network.py:
  0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b;
- upstream base recorded by the harness:
  de5ec2e7a6074068452f45b1a191b5c72832df4a.

The source caller fixes H=25. The harness executes exactly the construction,
Checks initialization, compile_roles, verify_map, verify_labels and
verify_role_frames side segment in the caller's order. It does not execute the
remaining complex_network.certificate claims or admit a kappa result.

## Finding 1: the live-binding claim exceeds the actual guard

Relevant locations: native_backend.py:42-68 and 122-166.

The guard checks the bytes of both frozen Python files; expected function code,
co_filename, defaults/closure shape; globals-dictionary identity; Label's exact
class/MRO/attribute names; and each Label method's function code. These are useful
checks. Globals-dictionary identity is not equality of the values a function
will resolve from that dictionary or its builtins mapping.

Concrete static counterexample, without executing it: after load_source and
before bind, assign module.sum = lambda values: 0. Source bytes and every checked
function code remain identical. guard_module accepts the same module dictionary
ownership and class shape. A raw Label with basis {0: 1} has a literal Gram row
of zero under that changed sum, so literal nondegenerate returns False. The native
Gram is [1], rank 1, and the installed method returns True. The existing finite
binding-rejection controls change dot, rank or the target method; they do not
cover a module shadow of sum, list, enumerate, range, len, next or max, nor changes
to a function's builtins mapping.

A second static example is post-bind module.dot = lambda a, b: 0: supported
calls continue to invoke C without a freshness check, while captured original
fallback methods retain dynamic access to module.dot. Returning original_dot and
original_rank in the binding receipt does not enforce their continued use or
identity. Changes to Label attribute hooks after bind likewise are outside the
one-time guard.

Recommended bounded claim for the existing measurement: an isolated, freshly
loaded frozen module with standard resolved dependencies, whose globals/class
and input state remain stable for the run. Under that premise, the harness itself
does not introduce the counterexamples and the current scientific comparison is
not invalidated. Do not claim that arbitrary late runtime mutations automatically
fallback safely or preserve original semantics.

If broader reusable binding is required, capture and validate the resolved names
used by the affected functions and their nested code objects, including their
builtins mappings; explicitly handle the rank-trace wrapper as an allowed owned
replacement. Add pre-bind global-shadow and post-bind drift controls. Check
freshness at an appropriate paid boundary, or refuse native use once drift is
observed. A one-time initial guard can be sufficient for a deliberately private
stable module; it is not a live-drift proof.

## Finding 2: complete hashes omit the complement-return transcript

Relevant locations: compare_side_verifier.py:scientific_run/write_scientific and
source/complex_circuit.py:Checks.residual_ok/label_ok.

The complete witness contains circuit support/arguments/kinds, active nodes,
pieces with exact rational pairs, all cached Label bases/dimensions/keys, and
compiled role/source/output data. The rank transcript contains each original
ordered Gram matrix and its rank. Neither contains the ordered lists returned by
Label.complement_in.

The source consumes a complement through `not res or odd(res)` in residual_ok and
through the analogous predicate in label_ok. A reordered list or a different
same-span complement can preserve those predicates, all stored Label data and
all Gram calls. The native complement count 238,685 proves route/volume coverage,
not equality of the 238,685 returned lists. Thus a complete pair matching all
three hashes does not itself prove complete complement-witness equality.

The implementation nevertheless has a strong direct source argument: its
augmented rows, pivot choice, all-row XOR elimination and output traversal are
literal translations, and finite_controls.exact_list checks exact order against
a separate unchanged source module. Report these as the evidence for ordered
complement preservation. Do not attribute that conclusion to a transcript that
was not recorded.

If exact complete complement evidence is required, instrument both baseline and
candidate symmetrically to record/hash the full ordered (small rows, big rows,
returned vectors) stream, preserving insertion order and multiplicity. Price the
conversion, recording/hash and serialization in both commands. This changes the
measured workload identity and requires new frozen receipts; it should not be
retroactively attached to existing timings as though it had been paid.

## C memory and ownership review

native_gf2.c uses only fixed arrays of 64 uint64_t values. read_vectors first
requires an exact dict, rejects length >64, and checks `at >= length` before each
array write. It validates the final count. Every accepted value is an exact
Python int, excluding bool and int subclasses, and conversion through
PyLong_AsUnsignedLongLong either produces the full unsigned 64-bit value or
returns NotImplemented after an OverflowError. Negative and oversized integers
are not masked or truncated; the Python wrapper calls the original method.
Other Python errors propagate.

PyDict_Next supplies borrowed entries. In the accepted branch, only exact-int
conversion occurs before values are copied into C arrays. It invokes no foreign
numeric protocol; the GIL remains held and there is no release block. C arrays
are the only inputs used during elimination and result allocation, so Python
allocation/GC while constructing outputs does not leave borrowed vector pointers
in use. No caller dictionary or Label object is changed by the kernel. Keys are
not accessed semantically, matching the original values-only algorithms.

Every tuple/list allocation is checked. Newly created integers are transferred
with PyTuple_SET_ITEM/PyList_SET_ITEM into newly allocated containers. On a later
allocation failure, decref of the partially populated container safely releases
filled entries and tolerates its remaining NULL slots. gram_rank correctly
releases the Gram tuple when rank allocation fails, and releases both owned
objects if the final pair allocation fails. Both entries are stolen exactly once
on success. complement decrefs its partially filled list on an invariant or
integer-allocation failure. No leak, double-decref or unchecked reference use was
identified in these paths.

The native extension has no mutable cache/global answer state, no callback API,
no manual long-integer digit access and no recursion. Scratch is local and bounded
(three 64-element arrays in each main kernel). The busy/reentry complexity of the
rational cache is absent here. The static ABI assertion requires a 64-bit unsigned
long long, matching both conversion and output constructors. Unsupported compiler
platforms fail compilation rather than silently narrowing values.

## Shift and index proof

All shifts operate on uint64_t or UINT64_C values, never on a signed 32-bit `1`.

- parity64 shifts by 32, 16, 8 and 4; its table shift is in 0..15. Folding XORs
  together all nibbles and 0x6996 returns their final parity.
- Gram construction has n <=64 and j in 0..n-1, so every shift is in 0..63.
- binary_rank visits columns 0..63. It only accesses rows[rank] after finding a
  pivot with rank <= pivot < n; the loop additionally stops when rank == n.
- complement requires k+n <=64 before forming augmented rows. With n>0,
  k+i <=k+n-1 <=63. Pairing shifts j<k are likewise at most 63.
- During complement elimination, a pivot is dereferenced only after pivot<n.
  If rank reaches n, subsequent columns find pivot==n and continue without a
  row access. Thus 0<=rank<=n and n-rank is a valid output length.
- The low-mask expression special-cases k==64. That case necessarily has n==0,
  so there are no identity or reconstruction shifts by 64. The conditional
  operator does not evaluate the alternative `1 << k` branch.
- Reconstruction shifts k+j only for j<n; whenever that loop executes,
  k+j<=k+n-1<=63. The opposite edge k==0,n==64 uses shifts 0..63 and low_mask=0.

The tests exercise k=64,n=0; k=0,n=64; k=63,n=1; augmented width 65; vector bit 63;
values >=2^64; 65 vectors; and all-zero/dependent inputs. Static inspection found
no untested shift-by-64 expression reachable through the accepted domain.

## Exact field, pivots and observable order

The source operates over GF(2), with packed integer vectors and dot equal to
parity(x & y). The native parity operation and XOR elimination implement that
same field. This is not modular evidence for a rational-rank claim.

For complement, both implementations copy other.basis values first and then
self.basis values in dict insertion order. They put pairings in the low k bits
and coefficient identity in bit k+i, scan pairing columns from low to high,
choose the first available pivot at/after the current rank, swap it into that
rank, and clear its column in every other row. Both emit rows rank..n-1 in their
current order and reconstruct each vector by XORing the same ordered ambient
basis coefficients. They neither sort nor recanonicalize the complement list.
This preserves repeated/zero vectors too: a dependent ambient list can produce
zero/dependent image vectors while the coefficient-kernel basis cardinality is
still n-rank(pairing).

For Gram rank, C deliberately clears only lower rows, while the source clears
all other rows. Only scalar rank is returned by source.rank, so forward Gaussian
elimination is sufficient. The transcript uses the original Gram rows, copied
before C elimination, not a falsely advertised identical reduced matrix. Above-
pivot rows cannot affect the remaining below-pivot elimination subproblem. Native
Gram rows retain input insertion order, and nondegenerate returns an exact bool,
including True for an empty basis. C returns exact Python ints/list/tuple outputs.

## Independent oracle and coverage assessment

finite_controls loads two distinct source modules: an untouched oracle module and
a separately bound candidate module. It also implements an independent dense
binary oracle using lists, multiplication/addition modulo two and descending
pivot order, without calling packed source/native linear-algebra helpers.

For complements, dense checks establish orthogonality, membership in the ambient
span, coefficient-kernel output count and complete image dimension. For dependent
ambient inputs, the checked dimension formula rank(B)-rank(pairing) is valid
because ker(B) is contained in ker(pairing); expecting every output vector to be
independent would have been incorrect. Exact ordered-list comparison to the
unchanged source supplies the algorithm-specific witness-order check that the
mathematical span oracle intentionally does not provide.

The core corpus covers 5,329 ordered small/big pairs over three-bit vectors and
585 ordered Gram lists, including zeros and dependence. Additional controls cover
64-bit/augmented boundaries, 24 genuine Label insertion permutations, unsupported
numeric/container types, missing attributes, subclasses, broken iterators, source
method/helper replacement and wrong-math/reordered-output oracle negatives. The
source-control predicates use explicit require, so they survive -O. Complete
measurements explicitly reject -O to retain every original scientific assertion.

The parent reported normal finite success and an optimized finite run in progress
at assignment. This reviewer did not independently execute either mode and does
not certify the eventual optimized result from static inspection. No sanitizer,
allocation-fault or arbitrary runtime-drift verification is claimed. All defined
complete scientific outputs and every Gram input/rank are compared against fixed
expected hashes, and fixed native counts prevent silently using fallback for the
claimed H=25 complete path. Finding 2 bounds what that complete comparison says
about complements.

## Source/build and timing boundaries

The cold builder requires a new build directory, records the C source hash,
compiler command/output and extension hash, and checks unchanged source bytes
after compilation. The parent guard authenticates the frozen stage inventory.
The command compiles, links, loads and runs every finite/binding/fallback control
inside the candidate process; child compiler CPU is included by the outer guard.
Both complete arms serialize the same structural witness and rank-trace bytes.

The compiler reads the stage's C path directly rather than an independently
immutable source snapshot. Pre/post equality plus the parent's frozen-source
contract is sufficient for this stable private stage, but is not protection
against an adversarial transient file change restored between checks. Do not
claim stronger concurrent-source authentication than is enforced.

The finite suite contains its fixed diagnostic micro in every candidate control
bill. Those micro timings are not complete performance evidence. The parent's
outer full-process receipts, including build/controls and serialization, govern
any side-workload performance claim. A successful matrix result is scoped to this
frozen H=25 side verification, not the full network certificate, PR5864 speed,
selected frontier, new construction or kappa admission.

## V2 source-only follow-up review

The parent requested review of the separately owned matrix/ v2 drafts before
freezing new measurements. I read native_backend.py, finite_controls.py and
compare_side_verifier.py there, without importing, compiling or executing them.
C bytes match the reviewed v1 exactly: SHA256
e9c3c9194a08718bd1575c1cf08c6c6772d3b644c2e274c25a84a1f9249d06cc.
The v1 source/receipt conclusions above remain historical and are not rewritten.

**V2 addresses both earlier findings at source level under its explicit serial,
no-mutation-during-a-call contract.** This is clearance to freeze and qualify the
new source, not a finite/runtime or performance pass.

The revised initial guard verifies canonical resolved builtin lookup, rejects
source-level shadows, checks each function's captured __builtins__ pointer as
well as the module slot, and authenticates exact immutable source-code metadata
before equality comparisons. Custom Label descriptors/MRO/dispatch are rejected.
A forged function constructed with alternate builtins cannot become acceptable
merely by restoring the module's __builtins__ slot. Builtin identities are checked
before source file/path work; compilation for inspection uses an anchored compile
function. These changes address the concrete pre-bind sum-shadow counterexample.

RuntimeGuard snapshots source/helper/class identities, live function code,
defaults, closures/cells, captured builtin pointers and native entry functions.
It runs before either native arithmetic or fallback. Installing the guard object
into the wrapper closure before initializing its snapshots avoids immediately
invalidating the guard's own runtime cell. Checks are identity-based after binding,
so changed callables/descriptors need not be executed to detect drift. The new
controls explicitly cover source shadows, captured builtins, source/helper code,
class dispatch, inherited lookup, shared builtin drift and native dispatch.
These checks do not protect arbitrary mutation of guard/backend memory, unrelated
module globals, or mutation during a call; the module now states those limits.

ComplementTrace snapshots exact Label/exact dict/exact integer inputs in the
same other-then-self order in both arms and streams canonical newline-delimited
JSON containing call index, ordered self/other vectors and typed ordered output.
It distinguishes [] from None and preserves input/output order, multiplicity,
signs and unbounded exact integer values. The raw stream is not retained: its
SHA256, canonical byte count and call count are recorded. Thus the new evidence
is a complete ordered stream digest, not a downloadable full JSONL witness.

Finite fallback controls leave observation disabled, avoiding additional
values()/iterator invocations on arbitrary custom containers. Complete tracing
is deliberately restricted to exact objects; its independent tests include
large-integer fallback while retaining exact plain dict/int inputs. New negative
controls distinguish input reorder, output reorder and [] versus None. C's normal
complement result remains an exact list; None support is only a recorder control.

The complete command now requires 238,685 streamed calls and can compare the
stream digest with a fresh baseline. At the reviewed draft, the expected digest
CLI argument was still optional for candidate mode. A candidate without that
argument records a digest but does not compare it; its COMPLETE_SIDE_PASS cannot
by itself establish complement equality. I recommended requiring a nonempty
--expected-complement-sha256 for candidate mode before output/build work. At
minimum, the parent's acceptance gate must supply the fresh v2 baseline digest to
every candidate command or explicitly compare the complete stream receipts.
This is an operational qualification condition, not a found arithmetic error.

One minor interface hardening recommendation was also sent: bind should check
that native is an exact ModuleType before reading native.complement or
native.gram_rank. Root's freshly built native module already satisfies that
condition, but doing the check first prevents an unsupported proxy's attribute
hooks from running before its eventual rejection.

Reviewed draft Python hashes, before any final small hardening in response:

- native_backend.py:
  ff67d20a97287de84b71aaf3de759bb3b0d6ad1caa40ffa16d5e13750a5cb629;
- finite_controls.py:
  e90c663b7be03d6f28d4741b015697a24c56140fbb6fe33bbc149506b4d1cf85;
- compare_side_verifier.py:
  95aa0d249eb1906589f643d7507123d0113592c628e1da7c4eab02d5db29b8aa.

The new per-call guard and symmetric transcript costs belong to the new complete
workload. Preserve prior samples as v1 evidence and use freshly frozen v2 finite
and full-process receipts for any v2 performance conclusion. No new issue was
found that requires changing the C arithmetic implementation.

### Final v2 source disposition

I read the two final hardening changes and the added NativeProxy control.
Candidate mode now requires the expected complement SHA256 immediately after
argument parsing, before creating output or compiling. bind checks exact native
ModuleType and owned builtin entry points through direct dictionary lookup before
accessing native attributes. The proxy control requires rejection without any
attribute hook invocation.

**Static disposition: CLEARED TO FREEZE FOR V2 QUALIFICATION.** Both original
findings and the two final operational/purity recommendations are addressed in
the reviewed source under its stated stable-runtime boundary. No remaining
blocking issue was identified. This does not substitute for the parent's finite
normal/-O or complete performance/equality receipts.

Final reviewed Python hashes:

- native_backend.py:
  e473c38245c3668715b5a78dfe980b2fe3ed0d0c9b8c97c666fbae6ecf1fffd5;
- finite_controls.py:
  df989a831aac43cc1af95169dad8c64a7548760e6e1f96976da996703f2c8f7a;
- compare_side_verifier.py:
  6e507bb0c7e00d090a60289fddb6c55e90c946d0850c42c3c5e3e15c27604a68.

C remains unchanged from the reviewed v1 hash above. No reviewed matrix source,
measured stage or evidence was edited by this reviewer.
