# Opportunity 3: exact matrix / finite-field feasibility

Source-only preparatory status: no compiler, imported verifier, numerical check or timing was executed by this agent. The parent owns the sole serial guarded numerical runner.

The proposed first workload is the unchanged `complex_network.certificate()` side-verification segment at its literal `H = 25`: construct `ComplexSideCircuit(25)`, initialize `Checks`, compile physical roles, and run **all** of `verify_map`, `verify_labels`, and `verify_role_frames`. These are called in the identical order by the pinned caller. This is a genuine complete finite side-check segment, not the full network certificate, the selected construction replay, or a PR5864 timing workload. No h or mathematical parameters are searched.

Sources are pinned to `de5ec2e7a6074068452f45b1a191b5c72832df4a`. Authentic source copies are in `matrix/source/`; their SHA-256 hashes are enforced by `matrix/profile_side_verifier.py`. The caller is parsed only to confirm its fixed H. Only the self-contained side-verifier module is imported by the proposed run. Existing synced or predecessor source files are unchanged.

## Why this scope

`complex_circuit.rank` is literal GF(2) elimination and returns only a Python `int`. A packed native GF(2) kernel can preserve its exact field without adding FLINT/GMP dependencies or confusing modular lower bounds with rational rank. In contrast, `rational_span_frames.basis` exposes exact primitive integer rows, canonical signs and pivots; merely returning the same rational rank would violate its contract. `audit_stage_pair.modular_rank` is a mod-101 lower-bound screen inside a larger rational certificate. Speeding it would neither prove equality with rational rank nor remove the exact rational fallback. Those alternatives need their own expensive caller and independent arithmetic validation.

The profile also records `echelon`, `reduce`, `dot`, `Label.complement_in` and `Label.nondegenerate`, because a rank-only call may be too small to pay compiler/load and finite checks. Moving those surrounding routines is a wider contract: dictionary insertion order, canonical basis rows/pivot masks, exact list/dict/int types, complement vector order, exceptions, and all observable witness bytes must match. No source rewrite is justified before this cost evidence.

## Parent's one proposed diagnostic run

Under the already authorized **serial**, **180-second**, **1-GiB process-group RSS** guard, using the declared shared time budget, run from the workspace:

```sh
python3 -B outputs/c-verification-all-opportunities-20261027/matrix/profile_side_verifier.py --output outputs/c-verification-all-opportunities-20261027/matrix/profile-run-1
```

No automatic retry. The output path must not exist. `-O` is rejected for this profile because the unchanged verifier uses `assert`. The script neither compiles C nor alters imports in the source files. Instrumentation wraps rank only to retain each actual input matrix and scalar output. It profiles cold module load, construction, all side checks and role compilation; writes raw cProfile data, exact rank transcript/corpus, unmodified result fields and complete structural/basis/role hashes. Profiling and transcript overhead make these timings diagnostic only. Nested cumulative times cannot be summed or turned into claimed complete speedup.

## Conditional native design and controls

If measured costs leave a credible complete gain, the smallest candidate is a self-contained C extension with a checked `uint64_t` fast path for exact nonnegative built-in Python integers of at most 64 bits. Inputs outside that domain retain the untouched Python rank function. Every arbitrary-width/negative/subclass/iterable compatibility path must be explicit; silent truncation or changed exceptions are forbidden. Native forward elimination may clear only lower rows because rank is its sole returned observation, but this optimization is inappropriate for basis-producing helpers without exact witness comparison.

The qualification bill must include source hashing, compilation, linking, cold loading, conversion, every actual traced matrix, finite exhaustive small binary matrices, boundary bits and arbitrary-width fallback, negative/type/iterator controls, independent dense-list GF(2) elimination, and all complete unchanged side checks. Preserve the unchanged Python verifier as oracle. Repeat complete baseline/candidate runs only if the first one-pair screen remains favorable after those costs. No new third-party dependency or shared-helper replacement is needed for this smallest route.

A wider kernel must separately preserve `echelon` insertion/pivot order and `complement_in` row order and prove all bound/fallback cases. The existing whole-witness receipt will make these observations explicit, but matching hashes by itself is not independent mathematical correctness.

## Credit and limits

Credit existing PR5168 and PR5382 for optional FLINT producer/discovery use and deliberately separate clean integer verification; PR2853 and PR3143 for optional gmpy2/integer acceleration and its replay environment. These predecessors do not establish that adding those dependencies speeds this frozen verifier. Preserve the source's authorship, including the inherited complex-side construction and its distinct finite-verification scope.

This opportunity is independent of the remaining ≥15% complete PR5864 target. Matrix microseconds, instrumented totals, or side-only speedups cannot count toward that objective. A negative cost screen is a useful result and should stop construction within this round.

Open next question: does the fixed h25 complete side profile assign enough avoidable work to native finite-field kernels to fund their complete cold and independent-check bill? This remains unmeasured until the parent executes the bounded run.

## Profile received and wider source-only implementation

The parent completed the single diagnostic profile successfully: 78.065 seconds outer elapsed, about 414 MB process-group RSS; 75.838 seconds inside the profiled side segment. The relevant nested costs were `complement_in` 41.831 seconds (238,685 calls), `nondegenerate` 8.772 seconds (59,959 calls), and `rank` 2.028 seconds. `dot`'s 15.998 seconds is included in the callers and is not an additional saving. These are instrumented diagnostics, not unprofiled baseline speed measurements. The rank-only route is stopped as too small to be a compelling first candidate.

The wider source-only candidate replaces **only** `Label.complement_in` and `Label.nondegenerate`, leaving `echelon`, `reduce`, `contains`, canonical labels and the entire side verifier untouched. Files are in `matrix/`:

- `native_gf2.c`: dependency-free C extension with bounded unsigned 64-bit vectors; literal ordered augmented elimination for complements and packed Gram construction plus scalar rank.
- `native_backend.py`: cold compile/link/load, pinned-source and current-function-code guards, binding and untouched Python fallbacks.
- `finite_controls.py`: unchanged-source comparisons, an independent dense-list GF(2) oracle, exhaustive ordered small matrices, word/augmentation boundaries, type/iterator/negative/large-integer fallbacks, runtime rebinding rejection, permutation checks and fixed conversion-plus-kernel diagnostics.
- `compare_side_verifier.py`: one finite or complete cold run, no retries, no search or orchestration.

The C complement follows the source's first available pivot, all-row clearing, and output row order exactly. It never canonicalizes or sorts the output. All vectors must be exact nonnegative built-in integers fitting 64 bits. Exact dict insertion order is preserved; map keys are unobserved by both original methods. Complement augmentation additionally requires `len(self.basis) + len(other.basis) <= 64`; unsupported domains fall back to the unchanged source. No narrowing conversion is accepted. Gram processing returns exact ordered Gram rows and rank to retain the **same full rank transcript**, while the bound public method returns the original exact bool type.

The complete harness predeclares and checks all three diagnostic hashes:

- Result: `342e99212b12e518902ae9598613f5484113bacee8747c27a13b58a4b1d3986c`.
- Full structural/basis/role witness: `4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82`.
- Ordered rank trace: `85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f`.

Both complete arms perform identical result, complete-witness and rank-trace serialization and write those same bytes to their own output directory. Candidate additionally pays every cold compiler/link/load and finite-control cost; child compiler CPU is included in its internal CPU report. The outer parent guard remains the authoritative complete measurement. Each output directory and candidate build is fresh; reuse and overwrite are refused. Complete measurements reject `-O`; finite controls can be run under `-O` because their qualification decisions use explicit exceptions and the finite fixtures do not depend on assertion elimination.

Proposed first discriminating execution by the parent, under the existing serial 180-second/1-GiB limits:

```sh
python3 -B outputs/c-verification-all-opportunities-20261027/matrix/compare_side_verifier.py --mode finite --output outputs/c-verification-all-opportunities-20261027/runtime/matrix-finite-1
```

Only after finite success and a credible cost screen, one complete baseline and candidate pair use `--mode baseline` / `--mode candidate` and distinct new output directories. If the paid complete pair remains promising, the declared B1,C1,C2,B2,B3,C3 order can establish whether this **separate H=25 side-verification scope** improves at least 15% in both complete wall and CPU time, beyond the parent-declared noise/spread allowance. No numerical/compiler execution has been performed by this agent. Source compilation, controls, complete correctness and speed remain unverified until the parent runs them.

## Correctness revision 2: effective lookup guards and complete complements

Independent static review by the rational-design agent found two gaps after the parent's version 1 normal/`-O` finite passes. Version 1 sources are preserved under `matrix/drafts/v1/`; the parent retains all original stage/evidence/sample directories. `matrix/V2-CORRECTNESS-REVISION.md` records the reason for the new version. This is a correctness and coverage change before candidate timing, not a timing retry.

The binding now has an explicit stable-runtime contract. At installation it validates source bytes, exact function code/calling shape, each function's **captured `__builtins__` pointer** as well as the module slot, ordinary built-in resolution (including `sum`, `list`, `rank`'s helpers and the Label constructor/containment helpers), and the original class/descriptor dispatch. Before every optional native method call it checks identities of the effective lookup environment, helper/method code/defaults/closure cells, Label namespace/MRO and native entry points. Drift raises an explicit `RuntimeError` before either native work or Python fallback; altered helpers and descriptors are not called as probes. Ordinary unsupported widths, values and mapping types still go through the unchanged source when the runtime is stable. The implementation does not promise protection against arbitrary modification of the backend's own internals, interpreter binary or native process memory.

Both complete arms now stream every actual complement call into the same canonical SHA-256 transcript: call index, ordered `us` and `vs` vectors, and a typed output record. The source method normally returns a list; the recorder distinguishes a list from `None` and tests that distinction without claiming that the source method emits `None`. Complete H25 input snapshots are restricted to exact Label objects, ordinary dictionaries and exact integer vectors. The observer is disabled for the side-effecting finite fallback fixtures, so it does not add extra `values()` calls or consume iterators twice.

The complete run requires all 238,685 complement calls and retains the original three hashes. A **new complement digest must come from the first fresh version 2 baseline**, then be matched by its candidate and remaining samples. It is not inferred from the old profile. `compare_side_verifier.py` accepts `--expected-complement-sha256 <fresh-baseline-digest>` to enforce that lock. The stream receipt stores its byte count and SHA-256 with constant retained state; both arms pay identical per-call serialization and hashing. The large ordered input/output stream itself is not retained.

Added finite controls cover each builtin shadow, a forged function with a stale alternate builtins pointer, custom descriptors, post-binding helper identity/code/default changes, source class/global changes, actual builtin drift and native dispatch replacement. They require rejection before either native or fallback counters change and verify that no modified helper was invoked. Separate finite baseline/candidate observers must produce the same ordered complement stream; negative checks ensure that changed input order, changed result order and list/None distinctions alter the digest.

The C source is byte-identical to version 1 (`e9c3c9194a08718bd1575c1cf08c6c6772d3b644c2e274c25a84a1f9249d06cc`). No compiler, numerical execution, imports or tests were run by this source-owning agent for version 2.

Final v2 static-review correction: `--expected-complement-sha256` is now **mandatory for every complete candidate**, checked before output/build work, so `COMPLETE_SIDE_PASS` cannot be issued without matching the first fresh baseline's complement digest. The first baseline omits the option; later baselines can supply it too. Native module and entry-point types are checked by direct dictionary access before any possible attribute dispatch, and the finite suite checks rejection of a custom native proxy without invoking it. The independent static review found no other blocking arithmetic/binding issue under the declared serial stable-runtime boundary; execution is still unrun by this agent.
