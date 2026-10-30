# Source-announced adapter interfaces

2026-10-28. These are worker-announced interfaces, pending implementation source review. Parent owns integration. No execution performed by reviewer.

| Lane | Public adapter | Parent use | New controls |
|---|---|---|---|
| P1 | `bind_verify_map(module) -> {verify_map, owner, receipt}` | Install returned method in candidate only. Trusted wrappers call `owner.capture_c(c)` and `owner.capture_checks(checks)` after each original constructor succeeds. Call `owner.seal()` after final phase/class wrapping. `owner.arm_cli()` surrounds authenticated original CLI, paired with `owner.disarm_cli()` in finally. | `run_controls(backend, set_adapter) -> receipt`; explicit loaded adapter and backend, no implicit scientific module import. Lease validity and original prefix/fallback callback behavior are independently distinguished. |
| P2 | `make_runtime_guard(backend) -> RuntimeGuard-compatible class` | Candidate-only `backend.RuntimeGuard = factory(backend)` before bind. Original constructor `(module,label,native,original_functions)`, `check(self)` and fields retained. | `run_guard_controls(reference_backend,candidate_backend,native) -> receipt`; four source loads for traced/untraced original/candidate, then restore/reuse bindings across mutations. |
| P3 | `make_trace_type(backend,native_encoder_module) -> trace subclass` | Inherits original before/receipt; install instance before binding captures closures. Exposes fixed encoder owner/entry for parent freshness. | `run_controls(backend,native_module) -> receipt`; no self-build. |

P3 C interface: standalone `_trace_encoding.encode_record(call, us, vs, output)`, `METH_FASTCALL`, exactly four positional arguments; bytes including newline or `NotImplemented`. Helper symbols use `h25_trace_*`; `H25_TRACE_EMBEDDED` omits standalone registration/init for a parent-owned combined module. The parent selects either separate owner/entry freshness or merged-module entry freshness, always before arithmetic. Count checks on every boundary where installed, including Gram if using the common guard.

P1 reserves its one-use token at entry, expires in finally, and keeps helpers private rather than modifying scientific globals. Unsupported entry delegates original once. Unsupported post-prefix state uses the literal original tail. It plans original `enumerate(c.triples)` inner iteration, indexed private sets, explicit list clearing and left-set reference reset to avoid traceback-retained cached operands.

Integration ordering must reconcile two different snapshots: finish class/phase wrappers before P1 owner sealing; finish trace/native wrapper closure installation before P2 RuntimeGuard capture. Do not install a new class member or closure after the corresponding snapshot. Immutable reference instances remain separate from candidate instances.

Source admission is not code admission. Each implementation still needs exact checks of source preparation, exception paths, callbacks, borrowed/native references and all new costs. Controls should reuse restored fixtures when safe and target changed behavior; retaining existing controls does not require duplicating their full Cartesian product in each lane.
