# Independent proposal decisions

Source-only review of each lane's RESEARCH.md and PROPOSAL.json on 2026-10-28, against CONTRACT-MATRIX.md and the frozen PR5995 sources. No implementation or numerical execution reviewed. Parent retains implementation authorization and every run.

## P1 — HOLD for one contract repair

Private positional sets, separate unchanged pairwise predicates, untouched prefix and literal-tail fallback are acceptable. Admission of the local `got` keys is a useful concrete improvement: a custom collision key could otherwise run equality code in the optimized tail. The proposal correctly avoids persistent reuse, bitmask substitution, cached verification answers, and replaying callbacks from a previously executed prefix.

The remaining blocker is the claim that the whole `verify_map` lease follows the existing backend restriction. The existing backend states that its kernel calls run serially without mutation during each call. `verify_map` has no such bound native call over its all-pair loops. The longer invariant therefore needs explicit parent establishment and a limited supported-caller scope.

Minimal repair: describe a **new scoped frozen-caller invariant**, not an inherited guarantee. Specify exactly how the parent grants a per-invocation capability for the privately constructed exact Checks/circuit at the original call site, which runtime conditions it relies upon, and when it denies that capability. The policy itself must be trusted and callback-free, not an arbitrary caller function invoked during admission. Missing capability or unsupported state selects the already-proposed literal tail. No generic detection of all Python aliases, process mutation, or adversarial signal handling is required or claimed. A declaration that the lease is present, without identifying its issuing boundary, is insufficient.

Source-generated adapter preparation must authenticate the exact original prefix and fallback tail and isolate new helper names from the untouched reference module. Candidate and reference cannot share mutable globals that redirect the oracle to candidate behavior. Parent must price source preparation, admission, exact Fraction environment checks, ownership bookkeeping, controls and cleanup. Nothing in this review establishes measured saving.

## P2 — ACCEPT FOR IMPLEMENTATION, correctness unproven

First-occurrence `is` deduplication removes only repeated function records. Every separate global/class/native slot remains; distinct function objects sharing code remain distinct. The unchanged predicate and short-circuit order plus original anchored exception messages supports replacing successful `require` calls with failure-only branches. Empty-cell `ValueError` and attribute errors must propagate as before.

The explicit adapter, constructor/wrapper/final boundaries and proposed differential controls cover the relevant design. Keep the factory installation candidate-only. Finalize wrapper closures before snapshot; do not rebuild a guard after drift to bless new values. P3's additional encoder owner/entry is a parent integration obligation and cannot disappear because P2's primary constructor mirrors the original two native entries.

Implementation review must verify literal predicates/messages/order, record inventory, and the planned negative controls. No compiler alternative is approved by this decision.

## P3 — ACCEPT FOR IMPLEMENTATION, correctness unproven

A stateless exact-byte encoder with literal JSON fallback preserves the observation boundary without batching. Retaining `before`, original output validation, immediate original hash update, and byte/count order is the narrowest proposed route. Sorted JSON order is `call,result,us,vs`, which the proposal correctly distinguishes from the human schema label.

The bounded domain fits comfortably below 8192 bytes: at most 192 unsigned 20-digit vector values, their separators, one 20-digit count and fixed punctuation. The implementation must still check every append, return no partial bytes, check conversion error indicators, and clear only expected overflow before fallback. The GIL remains held, borrowed values are consumed within owned argument lifetimes, and no aliases escape.

Parent must choose and document one freshness arrangement before integration: merge encoder into the guarded native module and extend native entries, or add a separate exact native owner/entry check before arithmetic. Capture finalized bindings before guard initialization. Keep the ordinary frozen JSON-runtime assumption explicit; this proposal does not support arbitrary serializer monkeypatching. Fallback must still preserve negative/wide/direct-call shapes and decimal-limit exceptions.

Implementation review needs exact record bytes and every prefix/error state, not just the final digest. New cold build/import/check/control costs remain unknown and paid.

## Combined gate

No identified arithmetic conflict among the three designs. Ownership differs naturally: sets per map invocation, guard per module binding, trace per stream. The main integration hazards are shared reference globals, P3 entry coverage, snapshots captured before final installation, changed fallback boundaries, and omitting new finite-control costs. Freeze separate baseline/candidate modules or processes, preserve full control union and old independent oracles, then let the parent execute the serial correctness queue.

This is a source admission decision only. Individual complete pilots may justify integration without an individual 15% result; the combined complete wall and CPU/noise gates remain unchanged.

## P1 revision 2 addendum — ACCEPT FOR IMPLEMENTATION

The revised OWNERSHIP.md, RESEARCH.md and PROPOSAL.json resolve the design hold. They explicitly introduce a new whole-tail invariant, capture actual construction identities in the parent, reserve a one-use capability before prefix execution, admit actual state after the prefix, deny unsupported hooks/source conditions, avoid user policy callbacks, and expire on every exit. General calls retain literal fallback. Source-derived CALL-BUDGET.json correctly preserves both 10.58M intersection operations and the coefficient/equality work while removing 21,157,700 operand constructions for the stated complete input.

Executable lease issuance, environment denial and source/Fraction admission remain implementation-review obligations, not verified facts. Cleanup requires care: Python exception tracebacks can retain frame locals. If the implementation promises to release all private sets on error, explicitly drop/clear the set sequence and active loop references in `finally`; ordinary propagation alone does not prove release. No extra performance threshold is introduced.
